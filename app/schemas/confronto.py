# app/schemas/confronto.py
from __future__ import annotations
from typing import List
from pydantic import BaseModel


class ConfrontoClasseRow(BaseModel):
    creditor_class: str
    debito_totale: float
    soddisfazione_liq_importo: float
    soddisfazione_liq_pct: float
    soddisfazione_conc_importo: float
    soddisfazione_conc_pct: float
    delta_importo: float
    delta_pct: float
    concordato_migliore: bool


class ConfrontoResponse(BaseModel):
    case_id: str
    scenario_id: str
    classi: List[ConfrontoClasseRow]
    esito: str  # "CONCORDATO_CONVENIENTE" | "LIQUIDAZIONE_CONVENIENTE" | "PARI"
