# app/api/routers/imm_fin.py
"""Router per movimenti immobilizzazioni finanziarie."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime

from app.db.session import get_db
from app.db.models.mdm_imm_fin import MdmImmFinMovimento
from app.schemas.imm_fin import (
    ImmFinMovimentoOut, ImmFinMovimentoCreate, ImmFinMovimentiResponse,
)

router = APIRouter(tags=["imm-fin-movimenti"])

VALID_TIPI = {"ACQUISIZIONE", "DISMISSIONE"}


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.get("/cases/{slug}/imm-fin-movimenti", response_model=ImmFinMovimentiResponse)
def list_movimenti(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    items = (
        db.query(MdmImmFinMovimento)
        .filter(
            MdmImmFinMovimento.case_id == slug,
            MdmImmFinMovimento.scenario_id == scenario,
        )
        .order_by(MdmImmFinMovimento.period_index, MdmImmFinMovimento.id)
        .all()
    )
    return ImmFinMovimentiResponse(case_id=slug, items=items, count=len(items))


@router.post("/cases/{slug}/imm-fin-movimenti", response_model=ImmFinMovimentoOut)
def create_movimento(slug: str, body: ImmFinMovimentoCreate,
                     scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    if body.tipo not in VALID_TIPI:
        raise HTTPException(status_code=400, detail=f"tipo must be one of: {', '.join(sorted(VALID_TIPI))}")
    mov = MdmImmFinMovimento(
        case_id=slug,
        scenario_id=scenario,
        label=body.label,
        period_index=body.period_index,
        tipo=body.tipo,
        importo=Decimal(str(body.importo)),
        created_at=datetime.utcnow(),
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


@router.get("/cases/{slug}/imm-fin-movimenti/{mov_id}", response_model=ImmFinMovimentoOut)
def get_movimento(slug: str, mov_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    mov = db.query(MdmImmFinMovimento).filter(MdmImmFinMovimento.id == mov_id).first()
    if not mov:
        raise HTTPException(status_code=404, detail="Movimento non trovato")
    return mov


@router.put("/cases/{slug}/imm-fin-movimenti/{mov_id}", response_model=ImmFinMovimentoOut)
def update_movimento(slug: str, mov_id: int, body: ImmFinMovimentoCreate,
                     db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    mov = db.query(MdmImmFinMovimento).filter(MdmImmFinMovimento.id == mov_id).first()
    if not mov:
        raise HTTPException(status_code=404, detail="Movimento non trovato")
    if body.tipo not in VALID_TIPI:
        raise HTTPException(status_code=400, detail=f"tipo must be one of: {', '.join(sorted(VALID_TIPI))}")
    mov.label = body.label
    mov.period_index = body.period_index
    mov.tipo = body.tipo
    mov.importo = Decimal(str(body.importo))
    db.commit()
    db.refresh(mov)
    return mov


@router.delete("/cases/{slug}/imm-fin-movimenti/{mov_id}")
def delete_movimento(slug: str, mov_id: int, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    mov = db.query(MdmImmFinMovimento).filter(MdmImmFinMovimento.id == mov_id).first()
    if not mov:
        raise HTTPException(status_code=404, detail="Movimento non trovato")
    db.delete(mov)
    db.commit()
    return {"ok": True}
