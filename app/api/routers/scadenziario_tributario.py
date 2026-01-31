# app/api/routers/scadenziario_tributario.py
"""Router CRUD per scadenziari debiti tributari."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.schemas.scadenziario_tributario import (
    ScadenziarioTributarioCreate,
    ScadenziarioTributarioOut,
    ScadenziarioTributarioListOut,
    ScadenziarTributariResponse,
    RataOut,
)
from app.services.scadenziario_tributario import (
    create_scadenziario,
    get_scadenziari,
    get_scadenziario_detail,
    delete_scadenziario,
)

router = APIRouter(tags=["scadenziari-tributari"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/cases/{slug}/scadenziari-tributari", response_model=ScadenziarTributariResponse)
def list_scadenziari(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    items = get_scadenziari(db, slug, scenario)
    return ScadenziarTributariResponse(case_id=slug, items=items, count=len(items))


@router.post("/cases/{slug}/scadenziari-tributari", response_model=ScadenziarioTributarioOut)
def add_scadenziario(slug: str, body: ScadenziarioTributarioCreate,
                     scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    sched = create_scadenziario(db, slug, scenario, body.model_dump())
    _, rate = get_scadenziario_detail(db, sched.id)
    return ScadenziarioTributarioOut(
        **{k: getattr(sched, k) for k in ScadenziarioTributarioListOut.model_fields},
        rate=rate,
    )


@router.get("/cases/{slug}/scadenziari-tributari/{sched_id}", response_model=ScadenziarioTributarioOut)
def read_scadenziario(slug: str, sched_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    sched, rate = get_scadenziario_detail(db, sched_id)
    if not sched:
        raise HTTPException(status_code=404, detail="Scadenziario non trovato")
    return ScadenziarioTributarioOut(
        **{k: getattr(sched, k) for k in ScadenziarioTributarioListOut.model_fields},
        rate=rate,
    )


@router.delete("/cases/{slug}/scadenziari-tributari/{sched_id}")
def remove_scadenziario(slug: str, sched_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    if not delete_scadenziario(db, sched_id):
        raise HTTPException(status_code=404, detail="Scadenziario non trovato")
    return {"ok": True}
