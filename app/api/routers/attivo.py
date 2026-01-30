# app/api/routers/attivo.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.db.session import get_db
from app.schemas.attivo import AttivoItemOut, AttivoItemUpdate, AttivoResponse
from app.services.attivo import (
    seed_attivo_from_riclass,
    compute_attivo_totals,
    upsert_attivo_item,
    get_attivo_items,
)

router = APIRouter(tags=["attivo"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/cases/{slug}/attivo", response_model=AttivoResponse)
def read_attivo(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    items = get_attivo_items(db, slug, scenario)
    return AttivoResponse(case_id=slug, items=items, count=len(items))


@router.post("/cases/{slug}/attivo", response_model=AttivoResponse)
def seed_and_compute_attivo(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    """Seed dall'SP riclassificato e calcola i totali."""
    _ensure_case(db, slug)
    seed_attivo_from_riclass(db, slug, scenario)
    compute_attivo_totals(db, slug, scenario)
    items = get_attivo_items(db, slug, scenario)
    return AttivoResponse(case_id=slug, items=items, count=len(items))


@router.put("/cases/{slug}/attivo/items/{item_id}", response_model=AttivoItemOut)
def update_attivo_item(slug: str, item_id: int, body: AttivoItemUpdate, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    try:
        item = upsert_attivo_item(db, item_id, body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return item
