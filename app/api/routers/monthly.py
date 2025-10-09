from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Optional

from app.db.session import get_db
import app.services.compute_monthly as monthly_svc  # import a modulo, robusto

router = APIRouter(prefix="/cases", tags=["Monthly"])

def _to_period(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    try:
        dt = datetime.strptime(s, "%Y-%m")
        return dt.year * 100 + dt.month
    except ValueError:
        raise HTTPException(status_code=422, detail="Use YYYY-MM")

@router.post("/{slug}/compute-monthly")
def post_compute_monthly(
    slug: str,
    full_refresh: bool = Query(False, description="Se true, cancella prima e ricalcola"),
    period_from: Optional[str] = Query(None, description="YYYY-MM"),
    period_to: Optional[str]   = Query(None, description="YYYY-MM"),
    db: Session = Depends(get_db),
):
    # opzionale: verifica esistenza pratica
    ok = db.execute(text("SELECT 1 FROM cases WHERE slug = :slug"), {"slug": slug}).first()
    if not ok:
        raise HTTPException(status_code=404, detail="Case not found")

    pf = _to_period(period_from)
    pt = _to_period(period_to)

    out = monthly_svc.compute_case_monthly(
        db, slug, period_from=pf, period_to=pt, full_refresh=full_refresh
    )
    return {"case": slug, "monthly": out}

@router.get("/{slug}/sp-monthly")
def get_sp_monthly(
    slug: str,
    period_from: Optional[str] = Query(None),
    period_to: Optional[str]   = Query(None),
    db: Session = Depends(get_db)
):
    pf, pt = _to_period(period_from), _to_period(period_to)
    params, cond = {"case_id": slug}, "WHERE case_id = :case_id"
    if pf: cond += " AND period_key >= :pf"; params["pf"] = pf
    if pt: cond += " AND period_key <= :pt"; params["pt"] = pt
    q = f"""
      SELECT period_key, riclass_code, amount, source
      FROM fin_sp_monthly
      {cond}
      ORDER BY period_key, riclass_code
    """
    rows = db.execute(text(q), params).mappings().all()
    return {"case": slug, "rows": rows}

@router.get("/{slug}/ce-monthly")
def get_ce_monthly(
    slug: str,
    period_from: Optional[str] = Query(None),
    period_to: Optional[str]   = Query(None),
    db: Session = Depends(get_db)
):
    pf, pt = _to_period(period_from), _to_period(period_to)
    params, cond = {"case_id": slug}, "WHERE case_id = :case_id"
    if pf: cond += " AND period_key >= :pf"; params["pf"] = pf
    if pt: cond += " AND period_key <= :pt"; params["pt"] = pt
    q = f"""
      SELECT period_key, riclass_code, amount, source
      FROM fin_ce_monthly
      {cond}
      ORDER BY period_key, riclass_code
    """
    rows = db.execute(text(q), params).mappings().all()
    return {"case": slug, "rows": rows}
