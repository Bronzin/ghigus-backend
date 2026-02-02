# app/schemas/imm_fin.py
from __future__ import annotations
from typing import List
from pydantic import BaseModel
from datetime import datetime


class ImmFinMovimentoOut(BaseModel):
    id: int
    case_id: str
    scenario_id: str
    label: str
    period_index: int
    tipo: str
    importo: float
    created_at: datetime

    class Config:
        from_attributes = True


class ImmFinMovimentoCreate(BaseModel):
    label: str
    period_index: int
    tipo: str  # ACQUISIZIONE | DISMISSIONE
    importo: float


class ImmFinMovimentiResponse(BaseModel):
    case_id: str
    items: List[ImmFinMovimentoOut]
    count: int
