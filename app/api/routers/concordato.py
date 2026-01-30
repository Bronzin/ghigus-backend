# app/api/routers/concordato.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.concordato import ConcordatoResponse
from app.services.concordato import compute_concordato, get_concordato
from app.services.mdm_engine import run_full_pipeline

router = APIRouter(tags=["concordato"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.post("/cases/{slug}/compute-concordato", response_model=ConcordatoResponse)
def run_concordato(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    count = compute_concordato(db, slug, scenario)
    lines = get_concordato(db, slug, scenario)
    return ConcordatoResponse(case_id=slug, lines=lines, count=count)


@router.get("/cases/{slug}/concordato", response_model=ConcordatoResponse)
def read_concordato(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    lines = get_concordato(db, slug, scenario)
    return ConcordatoResponse(case_id=slug, lines=lines, count=len(lines))


@router.post("/cases/{slug}/compute-full")
def run_full(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    """Pipeline completa MDM: computa tutto in ordine di dipendenza."""
    _ensure_case(db, slug)
    result = run_full_pipeline(db, slug, scenario)
    return {"case_id": slug, "scenario_id": scenario, "pipeline": result}
