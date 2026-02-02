# app/schemas/scadenziario_tributario.py
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class RataOut(BaseModel):
    period_index: int
    quota_capitale: float = 0
    quota_interessi: float = 0
    quota_sanzioni: float = 0
    importo_rata: float = 0
    debito_residuo: float = 0

    class Config:
        from_attributes = True


class ScadenziarioTributarioCreate(BaseModel):
    ente: str
    descrizione: Optional[str] = None
    debito_originario: float = 0
    num_rate: int = 12
    tasso_interessi: float = 0
    sanzioni_totali: float = 0
    mese_inizio: int = 0


class ScadenziarioTributarioListOut(BaseModel):
    id: int
    case_id: str
    scenario_id: str
    ente: str
    descrizione: Optional[str] = None
    debito_originario: float = 0
    num_rate: int = 12
    tasso_interessi: float = 0
    sanzioni_totali: float = 0
    mese_inizio: int = 0
    is_existing: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class ScadenziarioTributarioOut(ScadenziarioTributarioListOut):
    rate: List[RataOut] = []


class ScadenziarTributariResponse(BaseModel):
    case_id: str
    items: List[ScadenziarioTributarioListOut]
    count: int
