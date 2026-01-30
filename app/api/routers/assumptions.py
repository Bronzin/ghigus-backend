# app/api/routers/assumptions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.assumptions import AssumptionsResponse, AssumptionsUpdate, AssumptionsData
from app.services.assumptions import get_assumptions, save_assumptions

router = APIRouter(tags=["assumptions"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/cases/{slug}/assumptions", response_model=AssumptionsResponse)
def read_assumptions(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    data = get_assumptions(db, slug, scenario)
    if data is None:
        data = AssumptionsData()
    return AssumptionsResponse(case_id=slug, data=data)


@router.put("/cases/{slug}/assumptions", response_model=AssumptionsResponse)
def update_assumptions(slug: str, body: AssumptionsUpdate, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    save_assumptions(db, slug, body.data, scenario)
    return AssumptionsResponse(case_id=slug, data=body.data)
