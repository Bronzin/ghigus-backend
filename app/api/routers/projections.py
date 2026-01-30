# app/api/routers/projections.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.services.ce_projection import compute_ce_projections, get_ce_projections
from app.services.sp_projection import compute_sp_projections, get_sp_projections
from app.services.cflow_projection import compute_cflow_projections, get_cflow_projections
from app.services.banca_projection import compute_banca_projections, get_banca_projections

router = APIRouter(tags=["projections"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.post("/cases/{slug}/compute-projections")
def run_all_projections(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    """Computa tutte le proiezioni nell'ordine corretto: CE -> SP -> CFlow -> Banca."""
    _ensure_case(db, slug)
    n_ce = compute_ce_projections(db, slug, scenario)
    n_sp = compute_sp_projections(db, slug, scenario)
    n_cflow = compute_cflow_projections(db, slug, scenario)
    n_banca = compute_banca_projections(db, slug, scenario)
    return {
        "case_id": slug,
        "ce_rows": n_ce,
        "sp_rows": n_sp,
        "cflow_rows": n_cflow,
        "banca_rows": n_banca,
    }


@router.get("/cases/{slug}/ce-projections")
def read_ce(slug: str, scenario: str = Query("base"), period_from: int = Query(0), period_to: int = Query(119), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    rows = get_ce_projections(db, slug, scenario, period_from, period_to)
    return {
        "case_id": slug,
        "projection_type": "CE",
        "count": len(rows),
        "lines": [
            {
                "id": r.id, "period_index": r.period_index,
                "line_code": r.line_code, "line_label": r.line_label,
                "section": r.section, "amount": float(r.amount or 0),
                "is_subtotal": r.is_subtotal,
            }
            for r in rows
        ],
    }


@router.get("/cases/{slug}/sp-projections")
def read_sp(slug: str, scenario: str = Query("base"), period_from: int = Query(0), period_to: int = Query(119), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    rows = get_sp_projections(db, slug, scenario, period_from, period_to)
    return {
        "case_id": slug,
        "projection_type": "SP",
        "count": len(rows),
        "lines": [
            {
                "id": r.id, "period_index": r.period_index,
                "line_code": r.line_code, "line_label": r.line_label,
                "section": r.section, "amount": float(r.amount or 0),
                "is_subtotal": r.is_subtotal,
            }
            for r in rows
        ],
    }


@router.get("/cases/{slug}/cflow-projections")
def read_cflow(slug: str, scenario: str = Query("base"), period_from: int = Query(0), period_to: int = Query(119), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    rows = get_cflow_projections(db, slug, scenario, period_from, period_to)
    return {
        "case_id": slug,
        "projection_type": "CFLOW",
        "count": len(rows),
        "lines": [
            {
                "id": r.id, "period_index": r.period_index,
                "line_code": r.line_code, "line_label": r.line_label,
                "section": r.section, "amount": float(r.amount or 0),
            }
            for r in rows
        ],
    }


@router.get("/cases/{slug}/banca-projections")
def read_banca(slug: str, scenario: str = Query("base"), period_from: int = Query(0), period_to: int = Query(119), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    rows = get_banca_projections(db, slug, scenario, period_from, period_to)
    return {
        "case_id": slug,
        "projection_type": "BANCA",
        "count": len(rows),
        "lines": [
            {
                "id": r.id, "period_index": r.period_index,
                "line_code": r.line_code, "line_label": r.line_label,
                "section": r.section, "amount": float(r.amount or 0),
            }
            for r in rows
        ],
    }
