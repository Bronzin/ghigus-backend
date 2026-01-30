# app/api/routers/passivo.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.db.session import get_db
from app.schemas.passivo import (
    PassivoItemOut, PassivoItemUpdate, PassivoResponse,
    TipologiaOut, TipologiaUpdate, TipologieResponse,
)
from app.services.passivo import (
    seed_passivo_from_riclass,
    apply_compensazioni_from_attivo,
    compute_passivo_totals,
    assign_tipologie,
    get_passivo_items,
    get_tipologie,
)

router = APIRouter(tags=["passivo"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/cases/{slug}/passivo", response_model=PassivoResponse)
def read_passivo(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    items = get_passivo_items(db, slug, scenario)
    return PassivoResponse(case_id=slug, items=items, count=len(items))


@router.post("/cases/{slug}/passivo", response_model=PassivoResponse)
def seed_and_compute_passivo(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    """Seed dall'SP riclassificato, applica compensazioni e calcola totali."""
    _ensure_case(db, slug)
    seed_passivo_from_riclass(db, slug, scenario)
    apply_compensazioni_from_attivo(db, slug, scenario)
    compute_passivo_totals(db, slug, scenario)
    items = get_passivo_items(db, slug, scenario)
    return PassivoResponse(case_id=slug, items=items, count=len(items))


@router.put("/cases/{slug}/passivo/items/{item_id}", response_model=PassivoItemOut)
def update_passivo_item(slug: str, item_id: int, body: PassivoItemUpdate, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    from app.db.models.mdm_passivo import MdmPassivoItem
    from app.services.passivo import _compute_passivo_item
    from decimal import Decimal

    item = db.query(MdmPassivoItem).filter(MdmPassivoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Passivo item non trovato")
    updates = body.model_dump(exclude_none=True)
    for key, val in updates.items():
        if hasattr(item, key):
            if isinstance(val, (int, float)):
                setattr(item, key, Decimal(str(val)))
            else:
                setattr(item, key, val)
    _compute_passivo_item(item)
    db.commit()
    return item


@router.get("/cases/{slug}/passivo-tipologie", response_model=TipologieResponse)
def read_tipologie(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    items = get_tipologie(db, slug, scenario)
    return TipologieResponse(case_id=slug, items=items)


@router.put("/cases/{slug}/passivo-tipologie", response_model=TipologieResponse)
def update_tipologie(slug: str, body: List[TipologiaUpdate], scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    tipologie_dicts = [t.model_dump() for t in body]
    assign_tipologie(db, slug, scenario, tipologie_dicts)
    items = get_tipologie(db, slug, scenario)
    return TipologieResponse(case_id=slug, items=items)
