from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SpRiclassOut(BaseModel):
    id: int
    case_id: str
    riclass_code: str
    riclass_desc: Optional[str] = None
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True  # pydantic v2


class CeRiclassOut(BaseModel):
    id: int
    case_id: str
    riclass_code: str
    riclass_desc: Optional[str] = None
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class KpiStandardOut(BaseModel):
    id: int
    case_id: str
    name: str
    value: float
    unit: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
