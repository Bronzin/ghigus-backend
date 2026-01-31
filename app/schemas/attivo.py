# app/schemas/attivo.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


class AttivoItemOut(BaseModel):
    id: int
    case_id: str
    category: str
    item_label: Optional[str] = None
    saldo_contabile: float = 0
    cessioni: float = 0
    compensazioni: float = 0
    rettifiche_economiche: float = 0
    rettifica_patrimoniale: float = 0
    fondo_svalutazione: float = 0
    pct_svalutazione: float = 0
    totale_rettifiche: float = 0
    attivo_rettificato: float = 0
    continuita_realizzo: float = 0
    modalita: str = "CONTINUITA"
    linked_passivo_id: Optional[int] = None

    class Config:
        from_attributes = True


class AttivoItemUpdate(BaseModel):
    cessioni: Optional[float] = None
    compensazioni: Optional[float] = None
    rettifiche_economiche: Optional[float] = None
    rettifica_patrimoniale: Optional[float] = None
    fondo_svalutazione: Optional[float] = None
    pct_svalutazione: Optional[float] = None
    continuita_realizzo: Optional[float] = None
    modalita: Optional[str] = None
    linked_passivo_id: Optional[int] = None


class AttivoResponse(BaseModel):
    case_id: str
    items: List[AttivoItemOut]
    count: int
