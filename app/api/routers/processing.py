# app/api/routers/processing.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.processing import (
    ingest_case,
    compute_case,
    process_case,
)

router = APIRouter(tags=["processing"])

@router.post("/cases/{slug}/ingest")
def ingest_case_by_slug(slug: str, db: Session = Depends(get_db)):
    try:
        return ingest_case(db, slug)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cases/{slug}/compute")
def compute_case_by_slug(slug: str, db: Session = Depends(get_db)):
    try:
        return compute_case(db, slug)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cases/{slug}/process")
def process_case_by_slug(slug: str, db: Session = Depends(get_db)):
    try:
        return process_case(db, slug)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
