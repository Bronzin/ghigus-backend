# app/api/routers/auxiliary.py
"""Router per PreDeduzione, Affitto, Cessione."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.db.session import get_db
from app.services.prededuzione import compute_prededuzione, get_prededuzione
from app.services.affitto import compute_affitto, get_affitto
from app.services.cessione import compute_cessione, get_cessione

router = APIRouter(tags=["auxiliary"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


# ── PreDeduzione ──

@router.post("/cases/{slug}/compute-prededuzione")
def run_prededuzione(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    count = compute_prededuzione(db, slug, scenario)
    return {"case_id": slug, "rows_computed": count}


@router.get("/cases/{slug}/prededuzione")
def read_prededuzione(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    rows = get_prededuzione(db, slug, scenario)
    return {
        "case_id": slug,
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "voce_type": r.voce_type,
                "voce_code": r.voce_code,
                "importo_totale": float(r.importo_totale or 0),
                "period_index": r.period_index,
                "importo_periodo": float(r.importo_periodo or 0),
                "debito_residuo": float(r.debito_residuo or 0),
            }
            for r in rows
        ],
    }


# ── Affitto ──

@router.post("/cases/{slug}/compute-affitto")
def run_affitto(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    count = compute_affitto(db, slug, scenario)
    return {"case_id": slug, "rows_computed": count}


@router.get("/cases/{slug}/affitto")
def read_affitto(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    rows = get_affitto(db, slug, scenario)
    return {
        "case_id": slug,
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "period_index": r.period_index,
                "canone": float(r.canone or 0),
                "iva": float(r.iva or 0),
                "totale": float(r.totale or 0),
                "incasso": float(r.incasso or 0),
            }
            for r in rows
        ],
    }


# ── Cessione ──

@router.post("/cases/{slug}/compute-cessione")
def run_cessione(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    count = compute_cessione(db, slug, scenario)
    return {"case_id": slug, "rows_computed": count}


@router.get("/cases/{slug}/cessione")
def read_cessione(slug: str, scenario: str = Query("base"), db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    rows = get_cessione(db, slug, scenario)
    return {
        "case_id": slug,
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "period_index": r.period_index,
                "component": r.component,
                "amount": float(r.amount or 0),
            }
            for r in rows
        ],
    }
