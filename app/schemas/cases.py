# app/schemas/cases.py
from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CreateCaseRequest(BaseModel):
    slug: str = Field(..., max_length=64)
    name: str
    company_id: str
    description: Optional[str] = None


class CaseResponse(BaseModel):
    id: str
    slug: str
    name: str
    company_id: str
    description: Optional[str] = None
    status: str = "created"

    class Config:
        from_attributes = True
        
class CaseCreate(BaseModel):
    slug: str
    name: str
    company_id: str   # deve essere stringa

class CaseResponse(BaseModel):
    id: str
    slug: str
    name: str
    company_id: str
    status: str | None = None
    description: str | None = None
    class Config:
        from_attributes = True  # (pydantic v2)        


class AssumptionsPayload(BaseModel):
    items: Dict[str, Any]


class ComputeResult(BaseModel):
    kpis: List[Dict[str, Any]]
    cnc: List[Dict[str, Any]]
    lg: List[Dict[str, Any]]
