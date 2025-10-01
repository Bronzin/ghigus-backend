from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.db.session import get_db
from app.db.models.final import SpRiclass, CeRiclass, KpiStandard
from app.schemas.riclass import SpRiclassOut, CeRiclassOut, KpiStandardOut

router = APIRouter(tags=["riclass"])

def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")

@router.get("/cases/{slug}/sp-riclass", response_model=List[SpRiclassOut])
def list_sp_riclass(slug: str, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    q = (
        db.query(SpRiclass)
        .filter(SpRiclass.case_id == slug)
        .order_by(SpRiclass.riclass_code.asc(), SpRiclass.id.asc())
    )
    return q.all()

@router.get("/cases/{slug}/ce-riclass", response_model=List[CeRiclassOut])
def list_ce_riclass(slug: str, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    q = (
        db.query(CeRiclass)
        .filter(CeRiclass.case_id == slug)
        .order_by(CeRiclass.riclass_code.asc(), CeRiclass.id.asc())
    )
    return q.all()

@router.get("/cases/{slug}/kpi-standard", response_model=List[KpiStandardOut])
def list_kpi(slug: str, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    q = (
        db.query(KpiStandard)
        .filter(KpiStandard.case_id == slug)
        .order_by(KpiStandard.name.asc(), KpiStandard.id.asc())
    )
    return q.all()
