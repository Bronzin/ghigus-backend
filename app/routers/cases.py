"""Routers handling case management endpoints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/cases", tags=["cases"])


class CaseCreate(BaseModel):
    """Payload for creating a new case."""

    company_id: str = Field(..., description="Identifier of the related company")
    name: str = Field(..., description="Human readable name for the case")
    description: Optional[str] = Field(None, description="Optional case description")


class CaseResponse(BaseModel):
    """Response returned after creating a case."""

    id: str
    company_id: str
    name: str
    description: Optional[str]
    status: str


class UploadMetadata(BaseModel):
    """Metadata describing an uploaded accounting or XBRL document."""

    filename: str
    file_type: str = Field(..., description="Type of the uploaded document (e.g. xbrl, balance-sheet)")
    size: Optional[int] = Field(None, description="Size of the file in bytes")
    notes: Optional[str] = Field(None, description="Additional notes regarding the upload")


class AssumptionsPayload(BaseModel):
    """Payload for storing case assumptions."""

    assumptions: Dict[str, Any]


_cases: Dict[str, CaseResponse] = {}
_uploads: Dict[str, List[Dict[str, Any]]] = {}
_assumptions: Dict[str, Dict[str, Any]] = {}


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate) -> CaseResponse:
    """Create a new case and return its metadata."""
    case_id = str(uuid4())
    case = CaseResponse(
        id=case_id,
        company_id=payload.company_id,
        name=payload.name,
        description=payload.description,
        status="created",
    )
    _cases[case_id] = case
    return case


@router.post("/{case_id}/upload", status_code=status.HTTP_201_CREATED)
def upload_case_metadata(case_id: str, metadata: UploadMetadata) -> Dict[str, Any]:
    """Store metadata about an accounting or XBRL upload for the case."""
    if case_id not in _cases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    uploads = _uploads.setdefault(case_id, [])
    upload_record = {
        "upload_id": str(uuid4()),
        "metadata": metadata.model_dump(),
    }
    uploads.append(upload_record)
    return {
        "case_id": case_id,
        "upload_id": upload_record["upload_id"],
        "metadata": metadata,
        "status": "stored",
    }


@router.post("/{case_id}/assumptions", status_code=status.HTTP_200_OK)
def set_assumptions(case_id: str, payload: AssumptionsPayload) -> Dict[str, Any]:
    """Persist the assumptions associated with a case."""
    if case_id not in _cases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    _assumptions[case_id] = payload.assumptions
    return {"case_id": case_id, "assumptions": payload.assumptions}


@router.get("/{case_id}/compute")
def compute_case(case_id: str) -> Dict[str, Any]:
    """Return mocked metrics and distributions for the case."""
    if case_id not in _cases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    return {
        "case_id": case_id,
        "kpi": {
            "revenue_growth": 0.12,
            "ebitda_margin": 0.23,
            "net_income": 150000,
        },
        "distributions": {
            "lg": {
                "p10": 0.05,
                "p50": 0.15,
                "p90": 0.27,
            },
            "cnc": {
                "p10": -0.02,
                "p50": 0.08,
                "p90": 0.16,
            },
        },
        "delta": {
            "baseline": 100000,
            "scenario": 125000,
            "variation": 25000,
        },
    }


@router.post("/{case_id}/report")
def generate_report(case_id: str) -> Dict[str, Any]:
    """Generate a mock DOCX report and return a placeholder URL."""
    if case_id not in _cases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    report_url = f"https://example.com/reports/{case_id}.docx"
    return {
        "case_id": case_id,
        "report_url": report_url,
        "message": "Report generation has been queued.",
    }
