# app/schemas/finanziamento.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class FinanziamentoScheduleOut(BaseModel):
    id: int
    finanziamento_id: int
    period_index: int
    quota_capitale: float = 0
    quota_interessi: float = 0
    rata: float = 0
    debito_residuo: float = 0

    class Config:
        from_attributes = True


class FinanziamentoOut(BaseModel):
    id: int
    case_id: str
    scenario_id: str
    label: str
    importo_capitale: float
    tasso_annuo: float
    durata_mesi: int
    mese_erogazione: int
    tipo_ammortamento: str
    is_existing: bool = False
    debito_residuo_iniziale: Optional[float] = None
    rate_rimanenti: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FinanziamentoWithSchedule(FinanziamentoOut):
    schedule: List[FinanziamentoScheduleOut] = []


class FinanziamentoCreate(BaseModel):
    label: str
    importo_capitale: float
    tasso_annuo: float = 3.0
    durata_mesi: int = 60
    mese_erogazione: int = 0
    tipo_ammortamento: str = "FRANCESE"
    is_existing: bool = False
    debito_residuo_iniziale: Optional[float] = None
    rate_rimanenti: Optional[int] = None


class FinanziamentiResponse(BaseModel):
    case_id: str
    items: List[FinanziamentoOut]
    count: int


class AttivoScheduleEntry(BaseModel):
    period_index: int
    importo: float

    class Config:
        from_attributes = True


class AttivoScheduleUpdate(BaseModel):
    """Lista di incassi mensili per una voce attivo."""
    entries: List[AttivoScheduleEntry]


class PfnResponse(BaseModel):
    liquidita: float
    attivita_finanziarie: float
    debiti_finanziari_bt: float
    debiti_finanziari_mlt: float
    pfn: float
    interpretation: str


class PfnProjectionEntry(BaseModel):
    period_index: int
    cassa: float
    debiti_finanziari_bt: float
    debiti_finanziari_mlt: float
    pfn: float


class PfnProjectionResponse(BaseModel):
    case_id: str
    entries: List[PfnProjectionEntry]


class SostenibilitaMonth(BaseModel):
    period_index: int
    saldo_banca: float
    pagamenti: float
    pagamenti_cumulativi: float
    avanzo: float
    status: str  # GREEN, YELLOW, RED


class SostenibilitaResponse(BaseModel):
    case_id: str
    overall: str  # GREEN, YELLOW, RED, GREY
    first_red: Optional[int] = None
    min_avanzo: Optional[float] = None
    months: List[SostenibilitaMonth]
