# app/schemas/compute.py
from typing import Literal, List, Optional
from pydantic import BaseModel

Trend = Literal["up", "down", "flat"]

class KPI(BaseModel):
    id: str
    label: str
    value: float
    unit: Optional[str] = None
    trend: Optional[Trend] = None
    change: Optional[float] = None

class DistributionItem(BaseModel):
    label: str
    percent: float   # 0..1
    amount: float    # valore in €
    
class ComputeResult(BaseModel):
    kpis: List[KPI]
    cnc: List[DistributionItem]
    lg:  List[DistributionItem]
    source_file: Optional[dict] = None  # upload_id, path, signed_url
    notes: Optional[str] = None
