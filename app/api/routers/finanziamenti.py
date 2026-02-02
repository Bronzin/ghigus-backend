# app/api/routers/finanziamenti.py
"""Router per nuovi finanziamenti, PFN, sostenibilita' e attivo schedule."""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import csv
import io
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from datetime import datetime

from app.db.session import get_db
from app.db.models.mdm_attivo import MdmAttivoItem
from app.db.models.mdm_attivo_schedule import MdmAttivoSchedule
from app.schemas.finanziamento import (
    FinanziamentoOut, FinanziamentoWithSchedule, FinanziamentoCreate,
    FinanziamentiResponse, FinanziamentoScheduleOut,
    AttivoScheduleUpdate, AttivoScheduleEntry,
    PfnResponse, PfnProjectionResponse, PfnProjectionEntry,
    SostenibilitaResponse, SostenibilitaMonth,
)
from app.services.finanziamenti import (
    get_finanziamenti, get_finanziamento_schedule,
    create_finanziamento, delete_finanziamento, save_finanziamento_schedule,
)
from app.services.pfn import compute_pfn_from_mdm, compute_pfn_from_projections
from app.services.sostenibilita import compute_sostenibilita

router = APIRouter(tags=["finanziamenti"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


# ── Nuovi Finanziamenti ──────────────────────────────────────

@router.get("/cases/{slug}/finanziamenti", response_model=FinanziamentiResponse)
def list_finanziamenti(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    items = get_finanziamenti(db, slug, scenario)
    return FinanziamentiResponse(case_id=slug, items=items, count=len(items))


@router.post("/cases/{slug}/finanziamenti", response_model=FinanziamentoWithSchedule)
def add_finanziamento(slug: str, body: FinanziamentoCreate,
                      scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    fin = create_finanziamento(db, slug, scenario, body.model_dump())
    schedule = get_finanziamento_schedule(db, fin.id)
    return FinanziamentoWithSchedule(
        **{k: getattr(fin, k) for k in FinanziamentoOut.model_fields},
        schedule=schedule,
    )


@router.get("/cases/{slug}/finanziamenti/{fin_id}", response_model=FinanziamentoWithSchedule)
def get_finanziamento_detail(slug: str, fin_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    from app.db.models.mdm_finanziamento import MdmNuovoFinanziamento
    fin = db.query(MdmNuovoFinanziamento).filter(MdmNuovoFinanziamento.id == fin_id).first()
    if not fin:
        raise HTTPException(status_code=404, detail="Finanziamento non trovato")
    schedule = get_finanziamento_schedule(db, fin.id)
    return FinanziamentoWithSchedule(
        **{k: getattr(fin, k) for k in FinanziamentoOut.model_fields},
        schedule=schedule,
    )


@router.delete("/cases/{slug}/finanziamenti/{fin_id}")
def remove_finanziamento(slug: str, fin_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    if not delete_finanziamento(db, fin_id):
        raise HTTPException(status_code=404, detail="Finanziamento non trovato")
    return {"ok": True}


@router.post("/cases/{slug}/upload-finanziamenti-esistenti",
             response_model=FinanziamentiResponse)
def upload_finanziamenti_esistenti(
    slug: str,
    file: UploadFile = File(...),
    scenario: str = Query("base"),
    db: Session = Depends(get_db),
):
    """Import pre-existing financing schedules from CSV.

    CSV columns: label, period_index, quota_capitale, quota_interessi
    One row per month per financing. Rows are grouped by label.
    """
    _ensure_case(db, slug)

    from app.db.models.mdm_finanziamento import MdmNuovoFinanziamento, MdmFinanziamentoSchedule

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    required_cols = {"label", "period_index", "quota_capitale", "quota_interessi"}
    if reader.fieldnames is None or not required_cols.issubset(
        {c.strip().lower() for c in reader.fieldnames}
    ):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {', '.join(sorted(required_cols))}",
        )

    # Normalise header names (strip whitespace, lowercase)
    col_map = {c.strip().lower(): c for c in reader.fieldnames} if reader.fieldnames else {}

    grouped: dict[str, list[dict]] = defaultdict(list)
    for lineno, row in enumerate(reader, start=2):
        try:
            label = row[col_map["label"]].strip()
            period_index = int(row[col_map["period_index"]].strip())
            quota_capitale = Decimal(row[col_map["quota_capitale"]].strip().replace(",", "."))
            quota_interessi = Decimal(row[col_map["quota_interessi"]].strip().replace(",", "."))
        except (ValueError, InvalidOperation, KeyError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Parse error on line {lineno}: {e}",
            )
        if not label:
            raise HTTPException(status_code=400, detail=f"Empty label on line {lineno}")
        grouped[label].append({
            "period_index": period_index,
            "quota_capitale": quota_capitale,
            "quota_interessi": quota_interessi,
        })

    if not grouped:
        raise HTTPException(status_code=400, detail="CSV is empty or has no valid rows")

    created_fins: list[MdmNuovoFinanziamento] = []
    for label, rows in grouped.items():
        rows.sort(key=lambda r: r["period_index"])
        tot_capitale = sum(r["quota_capitale"] for r in rows)

        fin = MdmNuovoFinanziamento(
            case_id=slug,
            scenario_id=scenario,
            label=label,
            importo_capitale=tot_capitale,
            tasso_annuo=Decimal("0"),
            durata_mesi=len(rows),
            mese_erogazione=rows[0]["period_index"],
            tipo_ammortamento="FRANCESE",
            is_existing=True,
            debito_residuo_iniziale=tot_capitale,
            rate_rimanenti=len(rows),
            created_at=datetime.utcnow(),
        )
        db.add(fin)
        db.flush()

        residuo = tot_capitale
        for r in rows:
            rata = r["quota_capitale"] + r["quota_interessi"]
            residuo -= r["quota_capitale"]
            db.add(MdmFinanziamentoSchedule(
                finanziamento_id=fin.id,
                period_index=r["period_index"],
                quota_capitale=r["quota_capitale"],
                quota_interessi=r["quota_interessi"],
                rata=rata,
                debito_residuo=max(residuo, Decimal("0")),
            ))

        created_fins.append(fin)

    db.commit()

    all_items = get_finanziamenti(db, slug, scenario)
    return FinanziamentiResponse(case_id=slug, items=all_items, count=len(all_items))


# ── Attivo Schedule (incassi mensili) ─────────────────────────

@router.get("/cases/{slug}/attivo/items/{item_id}/schedule",
            response_model=List[AttivoScheduleEntry])
def read_attivo_schedule(slug: str, item_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    rows = (
        db.query(MdmAttivoSchedule)
        .filter(MdmAttivoSchedule.attivo_item_id == item_id)
        .order_by(MdmAttivoSchedule.period_index)
        .all()
    )
    return [AttivoScheduleEntry(period_index=r.period_index, importo=float(r.importo))
            for r in rows]


@router.put("/cases/{slug}/attivo/items/{item_id}/schedule",
            response_model=List[AttivoScheduleEntry])
def update_attivo_schedule(slug: str, item_id: int, body: AttivoScheduleUpdate,
                           db: Session = Depends(get_db)):
    """Sostituisce l'intera schedulazione incassi per un item attivo."""
    _ensure_case(db, slug)
    item = db.query(MdmAttivoItem).filter(MdmAttivoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item attivo non trovato")

    db.query(MdmAttivoSchedule).filter(
        MdmAttivoSchedule.attivo_item_id == item_id
    ).delete()

    from decimal import Decimal
    for entry in body.entries:
        db.add(MdmAttivoSchedule(
            attivo_item_id=item_id,
            period_index=entry.period_index,
            importo=Decimal(str(entry.importo)),
        ))
    db.commit()

    return body.entries


# ── PFN (Posizione Finanziaria Netta) ─────────────────────────

@router.get("/cases/{slug}/pfn", response_model=PfnResponse)
def read_pfn(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    """PFN calcolata dal dato MDM rettificato."""
    _ensure_case(db, slug)
    data = compute_pfn_from_mdm(db, slug, scenario)
    return PfnResponse(**data)


@router.get("/cases/{slug}/pfn-projections", response_model=PfnProjectionResponse)
def read_pfn_projections(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    """PFN proiettata su ogni periodo dallo SP."""
    _ensure_case(db, slug)
    entries = compute_pfn_from_projections(db, slug, scenario)
    return PfnProjectionResponse(
        case_id=slug,
        entries=[PfnProjectionEntry(**e) for e in entries],
    )


# ── Sostenibilita' ────────────────────────────────────────────

@router.get("/cases/{slug}/sostenibilita", response_model=SostenibilitaResponse)
def read_sostenibilita(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    """Indicatore di sostenibilita' del piano: semaforo per ogni mese."""
    _ensure_case(db, slug)
    data = compute_sostenibilita(db, slug, scenario)
    return SostenibilitaResponse(
        case_id=slug,
        overall=data["overall"],
        first_red=data["first_red"],
        min_avanzo=data["min_avanzo"],
        months=[SostenibilitaMonth(**m) for m in data["months"]],
    )
