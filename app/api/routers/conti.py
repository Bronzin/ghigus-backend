# app/api/routers/conti.py
"""Endpoints for Piano dei Conti (chart of accounts) lookup tables."""

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.lkp_conti import LkpContoSP, LkpContoCE

router = APIRouter(prefix="/api/v1/conti", tags=["conti"])


class ContoOut(BaseModel):
    code: str
    description: str
    category: str

    class Config:
        from_attributes = True


@router.get("/sp", response_model=List[ContoOut])
def list_conti_sp(db: Session = Depends(get_db)):
    """Return full list of Stato Patrimoniale standard accounts."""
    return db.query(LkpContoSP).order_by(LkpContoSP.category, LkpContoSP.code).all()


@router.get("/ce", response_model=List[ContoOut])
def list_conti_ce(db: Session = Depends(get_db)):
    """Return full list of Conto Economico standard accounts."""
    return db.query(LkpContoCE).order_by(LkpContoCE.category, LkpContoCE.code).all()
