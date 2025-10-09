# app/api/routers/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db  # già presente nel tuo progetto

router = APIRouter(prefix="/cases", tags=["Dashboard"])

@router.get("/{slug}/dashboard")
def get_dashboard(
    slug: str,
    period_from: int = Query(..., ge=190001, le=299912),
    period_to:   int = Query(..., ge=190001, le=299912),
    include: list[str] | None = Query(None, description="Subset: KPI,BANKS,CF_SECTION"),
    db: Session = Depends(get_db),
):
    if period_from > period_to:
        raise HTTPException(status_code=400, detail="period_from must be <= period_to")
    include_norm = [s.upper() for s in include] if include else None

    sql = """
    SELECT * 
    FROM get_dashboard_payload(:case_id, :pf, :pt)
    WHERE (:inc IS NULL OR series_type = ANY(:inc))
    ORDER BY period_key, series_type, name, metric NULLS FIRST
    """
    rows = db.execute(
        text(sql),
        {"case_id": slug, "pf": period_from, "pt": period_to, "inc": include_norm}
    ).mappings().all()

    return {
        "case_id": slug,
        "from": period_from,
        "to": period_to,
        "include": include_norm,
        "data": rows,
    }
