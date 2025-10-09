# app/routers/cases_cflow.py
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db  # dependency sync (Session)

router = APIRouter(prefix="/cases", tags=["cases-cflow"])


@router.post("/{slug}/compute-cflow")
def post_compute_cflow(
    slug: str,
    period_from: int = Query(..., description="YYYYMM"),
    period_to: int = Query(..., description="YYYYMM"),
    full_refresh: bool = Query(False),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    if period_from > period_to:
        raise HTTPException(status_code=400, detail="period_from must be <= period_to")

    # Invoca la stored function SQL (pattern come Banks/KPI)
    sql = text("SELECT compute_cflow_monthly(:case_id, :pf, :pt, :fr)")
    db.execute(sql, {"case_id": slug, "pf": period_from, "pt": period_to, "fr": full_refresh})
    # flush non necessario per SELECT, commit non necessario (dipende dal vostro Session scope)
    return {"case": slug, "status": "ok", "range": [period_from, period_to], "full_refresh": full_refresh}


@router.get("/{slug}/cflow-monthly")
def get_cflow_monthly(
    slug: str,
    period_from: Optional[int] = Query(None, description="YYYYMM"),
    period_to: Optional[int] = Query(None, description="YYYYMM"),
    section: Optional[str] = Query(None, description="OPERATING|INVESTING|FINANCING"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    base_sql = """
        SELECT case_id, period_key, section, line_code, amount
        FROM fin_cflow_monthly
        WHERE case_id = :case_id
    """
    params: Dict[str, Any] = {"case_id": slug}

    if period_from is not None:
        base_sql += " AND period_key >= :period_from"
        params["period_from"] = period_from
    if period_to is not None:
        base_sql += " AND period_key <= :period_to"
        params["period_to"] = period_to
    if section is not None:
        base_sql += " AND section = :section"
        params["section"] = section

    base_sql += " ORDER BY period_key, section, line_code"

    rows = db.execute(text(base_sql), params).mappings().all()
    return {"case": slug, "rows": list(rows)}
