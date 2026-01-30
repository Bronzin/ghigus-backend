# app/schemas/concordato.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


class ConcordatoLineOut(BaseModel):
    id: int
    case_id: str
    period_index: int
    creditor_class: str
    debito_iniziale: float = 0
    pagamento_proposto: float = 0
    rata_pianificata: float = 0
    pagamento: float = 0
    pagamento_cumulativo: float = 0
    debito_residuo: float = 0
    pct_soddisfazione: float = 0

    class Config:
        from_attributes = True


class ConcordatoResponse(BaseModel):
    case_id: str
    lines: List[ConcordatoLineOut]
    count: int
