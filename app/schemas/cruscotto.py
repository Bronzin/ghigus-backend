# app/schemas/cruscotto.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class CruscottoPeriod(BaseModel):
    period_index: int
    label: str
    ricavi: float = 0
    ebitda: float = 0
    utile_netto: float = 0
    flusso_cassa: float = 0
    saldo_banca: float = 0


class CruscottoSummary(BaseModel):
    case_id: str
    periods: List[CruscottoPeriod]
    dscr: float = 0
    sp_sintetico: Dict[str, float] = {}
    totali: Dict[str, float] = {}


class RelazioneAiTable(BaseModel):
    title: str
    headers: List[str]
    rows: List[List[Any]]


class RelazioneAiResponse(BaseModel):
    case_id: str
    tables: List[RelazioneAiTable]
