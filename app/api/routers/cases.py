# app/api/routers/cases.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models.case import Case

router = APIRouter(prefix="/cases", tags=["cases"])

class CaseCreate(BaseModel):
    slug: str
    name: str
    company_id: Optional[str] = None
    description: Optional[str] = None

class CaseOut(BaseModel):
    id: str
    name: str
    company_id: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    status: Optional[str] = None
    class Config:
        from_attributes = True

@router.post("", response_model=CaseOut)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    existing = db.query(Case).filter(Case.id == payload.slug).first()
    if existing:
        return existing  # idempotente
    c = Case(
        id=payload.slug,
        name=payload.name,
        company_id=payload.company_id,
        description=payload.description,
        slug=payload.slug,
        status="new",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("", response_model=List[CaseOut])
def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.created_at.desc()).all()

@router.get("/{slug}", response_model=CaseOut)
def get_case(slug: str, db: Session = Depends(get_db)):
    c = db.query(Case).filter(Case.id == slug).first()
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return c
