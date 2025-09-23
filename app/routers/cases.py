# app/routers/cases.py
from __future__ import annotations
import logging
from ..db.deps import get_db

from typing import Generator, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.services.storage import download_bytes
from app.services.ingest import parse_csv_bytes

from app.core.db import SessionLocal
from app.models.case import Case
from app.models.upload import Upload
from app.schemas.cases import (
    CreateCaseRequest,
    CaseCreate,
    CaseResponse,
    AssumptionsPayload,
)

from typing import Any, Dict, List
from app.models.case_snapshot import CaseSnapshot


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cases", tags=["cases"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_case_by_any(db: Session, case_id: str) -> Optional[Case]:
    # accetta sia UUID (id) che slug
    stmt = select(Case).where((Case.id == case_id) | (Case.slug == case_id)).limit(1)
    return db.execute(stmt).scalars().first()


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    # 1) slug unico per non creare confusione
    exists = db.execute(select(Case).where(Case.slug == payload.slug)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="slug already exists")

    # 2) creazione record
    case = Case(
        id=str(uuid4()),                   # id come stringa/uuid
        slug=payload.slug,
        name=payload.name,
        company_id=str(payload.company_id) # assicurati che sia stringa
    )

    db.add(case)
    try:
        db.commit()        # 3) COMMIT esplicito
    except Exception as e:
        db.rollback()
        logger.exception("create_case failed")
        # 4) restituiamo il tipo di errore per capirci subito
        raise HTTPException(status_code=500, detail=f"db error: {e.__class__.__name__}: {e}")
    db.refresh(case)
    return case


@router.post("/{case_id}/assumptions", status_code=status.HTTP_200_OK)
def set_assumptions(case_id: str, payload: AssumptionsPayload, db: Session = Depends(get_db)) -> dict:
    case = _get_case_by_any(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    # MVP: non persistiamo, solo echo
    return {"case_id": case.slug, "assumptions": payload.items}



def _get_case(db: Session, case_id: str) -> Case | None:
    return db.execute(
        select(Case).where((Case.id == case_id) | (Case.slug == case_id)).limit(1)
    ).scalars().first()

@router.get("/{case_id}/compute", summary="Compute CNC vs LG dal canonico")
def compute_from_canonical(case_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    case = _get_case(db, case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    snap = db.execute(
        select(CaseSnapshot)
        .where(CaseSnapshot.case_id == case.id)
        .order_by(desc(CaseSnapshot.created_at))
        .limit(1)
    ).scalars().first()
    if not snap:
        raise HTTPException(400, "No canonical snapshot. Esegui /ingest")

    canonical = snap.canonical or {}
    tb = canonical.get("tb") or {}
    rows = int(tb.get("rows") or 0)

    kpis: List[Dict[str, Any]] = [
        {"id": "rows", "label": "Righe TB", "value": rows, "unit": "", "trend": "up"}
    ]

    base = max(rows, 1)
    cnc = [
        {"label": "Privilegiati",  "percent": 0.6, "amount": round(base * 100.0 * 0.6, 2)},
        {"label": "Chirografari", "percent": 0.3, "amount": round(base * 100.0 * 0.3, 2)},
        {"label": "Altri",         "percent": 0.1, "amount": round(base * 100.0 * 0.1, 2)},
    ]
    lg = [
        {"label": "Privilegiati",  "percent": 0.5, "amount": round(base * 100.0 * 0.5, 2)},
        {"label": "Chirografari", "percent": 0.2, "amount": round(base * 100.0 * 0.2, 2)},
        {"label": "Altri",         "percent": 0.1, "amount": round(base * 100.0 * 0.1, 2)},
    ]
    return {"kpis": kpis, "cnc": cnc, "lg": lg}

@router.post("/{case_id}/report", status_code=status.HTTP_201_CREATED)
def generate_report(case_id: str, db: Session = Depends(get_db)) -> dict:
    case = _get_case_by_any(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return {"case_id": case.slug, "status": "queued"}
