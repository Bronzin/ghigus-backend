# app/schemas/xbrl.py
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List, Dict, Any


class XbrlFactOut(BaseModel):
    id: int
    case_id: str
    concept: Optional[str] = None
    context_ref: Optional[str] = None
    unit: Optional[str] = None
    decimals: Optional[str] = None
    value: Optional[float] = None
    instant: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class XbrlFactsResponse(BaseModel):
    case_id: str
    facts: List[XbrlFactOut]
    count: int


class XbrlSummaryRow(BaseModel):
    riclass_code: str
    riclass_desc: Optional[str] = None
    amounts: Dict[str, Optional[float]]  # period -> amount


class XbrlKpiRow(BaseModel):
    name: str
    unit: Optional[str] = None
    values: Dict[str, Optional[float]]  # period -> value


class XbrlSummaryResponse(BaseModel):
    case_id: str
    periods: List[str]
    sp: List[XbrlSummaryRow]
    ce: List[XbrlSummaryRow]
    kpi: List[XbrlKpiRow]


class XbrlUnmappedConcept(BaseModel):
    concept: Optional[str] = None
    count: int


class XbrlUnmappedResponse(BaseModel):
    case_id: str
    unmapped: List[XbrlUnmappedConcept]
    unmapped_count: int
    mapped_count: int
