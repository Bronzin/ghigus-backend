# app/api/routers/liquidazione.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.liquidazione import (
    LiquidazioneResponse, LiquidazioneLineOut,
    TestPiatResponse, TestPiatLineOut,
)
from app.services.liquidazione import compute_liquidazione, get_liquidazione
from app.services.test_piat import compute_test_piat, get_test_piat

router = APIRouter(tags=["liquidazione"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.post("/cases/{slug}/compute-liquidazione", response_model=LiquidazioneResponse)
def run_liquidazione(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    count = compute_liquidazione(db, slug, scenario)
    lines = get_liquidazione(db, slug, scenario)
    return LiquidazioneResponse(case_id=slug, lines=lines, count=count)


@router.get("/cases/{slug}/liquidazione", response_model=LiquidazioneResponse)
def read_liquidazione(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    lines = get_liquidazione(db, slug, scenario)
    return LiquidazioneResponse(case_id=slug, lines=lines, count=len(lines))


@router.post("/cases/{slug}/compute-test-piat", response_model=TestPiatResponse)
def run_test_piat(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    result = compute_test_piat(db, slug, scenario)
    lines = get_test_piat(db, slug, scenario)
    return TestPiatResponse(
        case_id=slug,
        lines=lines,
        total_a=result["total_a"],
        total_b=result["total_b"],
        ratio_ab=result["ratio_ab"],
        interpretation=result["interpretation"],
    )


@router.get("/cases/{slug}/test-piat", response_model=TestPiatResponse)
def read_test_piat(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    lines = get_test_piat(db, slug, scenario)
    if not lines:
        return TestPiatResponse(case_id=slug, lines=[], total_a=0, total_b=0, ratio_ab=0, interpretation="")
    first = lines[0]
    return TestPiatResponse(
        case_id=slug,
        lines=lines,
        total_a=float(first.total_a or 0),
        total_b=float(first.total_b or 0),
        ratio_ab=float(first.ratio_ab or 0),
        interpretation=first.interpretation or "",
    )
