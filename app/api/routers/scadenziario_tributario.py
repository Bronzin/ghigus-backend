# app/api/routers/scadenziario_tributario.py
"""Router CRUD per scadenziari debiti tributari."""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
import csv
import io
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from datetime import datetime

from app.db.session import get_db
from app.schemas.scadenziario_tributario import (
    ScadenziarioTributarioCreate,
    ScadenziarioTributarioOut,
    ScadenziarioTributarioListOut,
    ScadenziarTributariResponse,
    RataOut,
)
from app.services.scadenziario_tributario import (
    create_scadenziario,
    get_scadenziari,
    get_scadenziario_detail,
    delete_scadenziario,
)

router = APIRouter(tags=["scadenziari-tributari"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/cases/{slug}/scadenziari-tributari", response_model=ScadenziarTributariResponse)
def list_scadenziari(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    items = get_scadenziari(db, slug, scenario)
    return ScadenziarTributariResponse(case_id=slug, items=items, count=len(items))


@router.post("/cases/{slug}/scadenziari-tributari", response_model=ScadenziarioTributarioOut)
def add_scadenziario(slug: str, body: ScadenziarioTributarioCreate,
                     scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    sched = create_scadenziario(db, slug, scenario, body.model_dump())
    _, rate = get_scadenziario_detail(db, sched.id)
    return ScadenziarioTributarioOut(
        **{k: getattr(sched, k) for k in ScadenziarioTributarioListOut.model_fields},
        rate=rate,
    )


@router.get("/cases/{slug}/scadenziari-tributari/{sched_id}", response_model=ScadenziarioTributarioOut)
def read_scadenziario(slug: str, sched_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    sched, rate = get_scadenziario_detail(db, sched_id)
    if not sched:
        raise HTTPException(status_code=404, detail="Scadenziario non trovato")
    return ScadenziarioTributarioOut(
        **{k: getattr(sched, k) for k in ScadenziarioTributarioListOut.model_fields},
        rate=rate,
    )


@router.delete("/cases/{slug}/scadenziari-tributari/{sched_id}")
def remove_scadenziario(slug: str, sched_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    if not delete_scadenziario(db, sched_id):
        raise HTTPException(status_code=404, detail="Scadenziario non trovato")
    return {"ok": True}


@router.post("/cases/{slug}/upload-scadenziari-esistenti",
             response_model=ScadenziarTributariResponse)
def upload_scadenziari_esistenti(
    slug: str,
    file: UploadFile = File(...),
    scenario: str = Query("base"),
    db: Session = Depends(get_db),
):
    """Import pre-existing tax debt schedules from CSV.

    CSV columns: ente, period_index, quota_capitale, quota_interessi, quota_sanzioni
    One row per month per schedule. Rows are grouped by ente.
    """
    _ensure_case(db, slug)

    from app.db.models.mdm_scadenziario_tributario import (
        MdmScadenziarioTributario,
        MdmScadenziarioTributarioRate,
    )

    content = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    required_cols = {"ente", "period_index", "quota_capitale", "quota_interessi", "quota_sanzioni"}
    if reader.fieldnames is None or not required_cols.issubset(
        {c.strip().lower() for c in reader.fieldnames}
    ):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {', '.join(sorted(required_cols))}",
        )

    col_map = {c.strip().lower(): c for c in reader.fieldnames} if reader.fieldnames else {}

    grouped: dict[str, list[dict]] = defaultdict(list)
    for lineno, row in enumerate(reader, start=2):
        try:
            ente = row[col_map["ente"]].strip()
            period_index = int(row[col_map["period_index"]].strip())
            quota_capitale = Decimal(row[col_map["quota_capitale"]].strip().replace(",", "."))
            quota_interessi = Decimal(row[col_map["quota_interessi"]].strip().replace(",", "."))
            quota_sanzioni = Decimal(row[col_map["quota_sanzioni"]].strip().replace(",", "."))
        except (ValueError, InvalidOperation, KeyError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Parse error on line {lineno}: {e}",
            )
        if not ente:
            raise HTTPException(status_code=400, detail=f"Empty ente on line {lineno}")
        grouped[ente].append({
            "period_index": period_index,
            "quota_capitale": quota_capitale,
            "quota_interessi": quota_interessi,
            "quota_sanzioni": quota_sanzioni,
        })

    if not grouped:
        raise HTTPException(status_code=400, detail="CSV is empty or has no valid rows")

    for ente, rows in grouped.items():
        rows.sort(key=lambda r: r["period_index"])
        tot_capitale = sum(r["quota_capitale"] for r in rows)
        tot_sanzioni = sum(r["quota_sanzioni"] for r in rows)

        sched = MdmScadenziarioTributario(
            case_id=slug,
            scenario_id=scenario,
            ente=ente,
            descrizione=f"Importato da CSV",
            debito_originario=tot_capitale,
            num_rate=len(rows),
            tasso_interessi=Decimal("0"),
            sanzioni_totali=tot_sanzioni,
            mese_inizio=rows[0]["period_index"],
            is_existing=True,
            created_at=datetime.utcnow(),
        )
        db.add(sched)
        db.flush()

        residuo = tot_capitale
        for r in rows:
            rata = r["quota_capitale"] + r["quota_interessi"] + r["quota_sanzioni"]
            residuo -= r["quota_capitale"]
            db.add(MdmScadenziarioTributarioRate(
                scadenziario_id=sched.id,
                period_index=r["period_index"],
                quota_capitale=r["quota_capitale"],
                quota_interessi=r["quota_interessi"],
                quota_sanzioni=r["quota_sanzioni"],
                importo_rata=rata,
                debito_residuo=max(residuo, Decimal("0")),
            ))

    db.commit()

    all_items = get_scadenziari(db, slug, scenario)
    return ScadenziarTributariResponse(case_id=slug, items=all_items, count=len(all_items))
