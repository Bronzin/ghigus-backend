# app/api/routers/finanziamenti.py
"""Router per nuovi finanziamenti, PFN, sostenibilita' e attivo schedule."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

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
