# app/schemas/passivo.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


class PassivoItemOut(BaseModel):
    id: int
    case_id: str
    category: str
    item_label: Optional[str] = None
    saldo_contabile: float = 0
    incrementi: float = 0
    decrementi: float = 0
    compensato: float = 0
    fondo_rischi: float = 0
    sanzioni_accessori: float = 0
    interessi: float = 0
    totale_rettifiche: float = 0
    passivo_rettificato: float = 0
    tipologia_creditore: Optional[str] = None
    classe_creditore: Optional[str] = None

    class Config:
        from_attributes = True


class PassivoItemUpdate(BaseModel):
    incrementi: Optional[float] = None
    decrementi: Optional[float] = None
    compensato: Optional[float] = None
    fondo_rischi: Optional[float] = None
    sanzioni_accessori: Optional[float] = None
    interessi: Optional[float] = None
    tipologia_creditore: Optional[str] = None
    classe_creditore: Optional[str] = None


class PassivoResponse(BaseModel):
    case_id: str
    items: List[PassivoItemOut]
    count: int


class TipologiaOut(BaseModel):
    id: int
    case_id: str
    sezione: str
    slot_order: int
    classe: str
    specifica: Optional[str] = None
    codice_ordinamento: Optional[str] = None

    class Config:
        from_attributes = True


class TipologiaUpdate(BaseModel):
    sezione: str
    slot_order: int
    classe: str
    specifica: Optional[str] = None
    codice_ordinamento: Optional[str] = None


class TipologieResponse(BaseModel):
    case_id: str
    items: List[TipologiaOut]
