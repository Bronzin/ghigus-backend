# app/schemas/projections.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


class ProjectionLineOut(BaseModel):
    id: int
    case_id: str
    period_index: int
    line_code: str
    line_label: Optional[str] = None
    section: Optional[str] = None
    amount: float = 0
    is_subtotal: bool = False

    class Config:
        from_attributes = True


class CflowLineOut(BaseModel):
    id: int
    case_id: str
    period_index: int
    line_code: str
    line_label: Optional[str] = None
    section: Optional[str] = None
    amount: float = 0

    class Config:
        from_attributes = True


class BancaLineOut(BaseModel):
    id: int
    case_id: str
    period_index: int
    line_code: str
    line_label: Optional[str] = None
    section: Optional[str] = None
    amount: float = 0

    class Config:
        from_attributes = True


class ProjectionResponse(BaseModel):
    case_id: str
    projection_type: str
    lines: List[ProjectionLineOut]
    count: int


class CflowResponse(BaseModel):
    case_id: str
    lines: List[CflowLineOut]
    count: int


class BancaResponse(BaseModel):
    case_id: str
    lines: List[BancaLineOut]
    count: int
