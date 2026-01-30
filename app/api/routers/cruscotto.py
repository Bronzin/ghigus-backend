# app/api/routers/cruscotto.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.services.cruscotto import get_cruscotto
from app.services.relazione_ai import get_relazione_ai

router = APIRouter(tags=["cruscotto"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/cases/{slug}/cruscotto")
def read_cruscotto(slug: str, scenario: str = Query("base"), periods: int = Query(10, ge=1, le=20), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    return get_cruscotto(db, slug, scenario_id=scenario, num_periods=periods)


@router.get("/cases/{slug}/relazione-ai")
def read_relazione_ai(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    return get_relazione_ai(db, slug, scenario_id=scenario)
