# app/schemas/liquidazione.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


class LiquidazioneLineOut(BaseModel):
    id: int
    case_id: str
    section: str
    line_code: str
    line_label: Optional[str] = None
    importo_totale: float = 0
    importo_massa_1: float = 0
    importo_massa_2: float = 0
    importo_massa_3: float = 0
    pct_soddisfazione: float = 0
    credito_residuo: float = 0

    class Config:
        from_attributes = True


class LiquidazioneResponse(BaseModel):
    case_id: str
    lines: List[LiquidazioneLineOut]
    count: int


class TestPiatLineOut(BaseModel):
    id: int
    case_id: str
    section: str
    line_code: str
    line_label: Optional[str] = None
    sign: int = 1
    amount: float = 0
    total_a: float = 0
    total_b: float = 0
    ratio_ab: float = 0
    interpretation: Optional[str] = None

    class Config:
        from_attributes = True


class TestPiatResponse(BaseModel):
    case_id: str
    lines: List[TestPiatLineOut]
    total_a: float = 0
    total_b: float = 0
    ratio_ab: float = 0
    interpretation: str = ""
