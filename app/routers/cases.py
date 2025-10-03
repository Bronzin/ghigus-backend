# app/routers/cases.py
from __future__ import annotations

import logging
from typing import Any, Dict, Generator, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select, text
from sqlalchemy.orm import Session

from ..db.deps import get_db
from app.core.db import SessionLocal
from app.models.case import Case

# Se usi storage/ingest negli altri endpoint, tieni questi import;
# non sono usati nel compute ma li lascio per compatibilità col file originale.
try:
    from app.services.storage import download_bytes  # noqa: F401
    from app.services.ingest import parse_csv_bytes  # noqa: F401
except Exception:
    pass

router = APIRouter(prefix="/cases", tags=["cases"])
log = logging.getLogger(__name__)


# ----------------------------
# Helpers
# ----------------------------
def _get_case_by_any(db: Session, case_id: str) -> Optional[Case]:
    """
    Recupera la pratica sia per slug che per UUID interno.
    """
    # prova per slug
    stmt = select(Case).where(Case.slug == case_id)
    case = db.execute(stmt).scalars().first()
    if case:
        return case

    # prova per id (se il campo esiste)
    try:
        stmt = select(Case).where(Case.id == case_id)
        case = db.execute(stmt).scalars().first()
        if case:
            return case
    except Exception:
        # se Case.id non è stringa/UUID compat, ignora
        pass

    return None


# ----------------------------
# Endpoint: elenco pratiche (facoltativo)
# ----------------------------
@router.get("", response_model=List[Dict[str, Any]])
def list_cases(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    try:
        stmt = select(Case).order_by(desc(Case.created_at))
        rows = db.execute(stmt).scalars().all()
    except Exception as ex:
        log.exception("Errore in list_cases: %s", ex)
        raise HTTPException(status_code=500, detail="Errore caricamento pratiche")

    return [
        {
            "id": str(c.id) if hasattr(c, "id") else None,
            "slug": c.slug,
            "name": getattr(c, "name", c.slug),
            "created_at": getattr(c, "created_at", None),
        }
        for c in rows
    ]


# ----------------------------
# Endpoint: crea pratica (facoltativo)
# ----------------------------
@router.post("", status_code=status.HTTP_201_CREATED)
def create_case(name: Optional[str] = None, db: Session = Depends(get_db)) -> Dict[str, Any]:
    slug = (name or str(uuid4()))[:64]
    c = Case(slug=slug, name=name or slug)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": str(getattr(c, "id", "")), "slug": c.slug, "name": c.name}


# ----------------------------
# Endpoint: compute
# ----------------------------
@router.get("/{case_id}/compute")
def compute_from_canonical(case_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Esegue il 'compute' per la pratica:
    - KPI/placeholder come da versione precedente
    - Compute SP in DB con fallback periodo tramite funzione SQL gh_compute_sp(:slug)
    Ritorna anche fin_sp_rows per feedback rapido.
    """
    case = _get_case_by_any(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # ----------------------------
    # KPI/placeholder (come nel file originale)
    # Qui usiamo una base euristica: numero righe TB * 1.0
    # Se preferisci altra metrica, sostituisci la query.
    # ----------------------------
    try:
        tb_count = db.execute(
            text("SELECT COUNT(*) FROM stg_tb_entries WHERE case_id = :slug"),
            {"slug": case.slug},
        ).scalar()
    except Exception:
        tb_count = 0

    base = float(tb_count or 0)

    kpis = [
        {"label": "Totale passivo", "value": round(base * 100.0, 2)},
        {"label": "Totale attivo", "value": round(base * 100.0, 2)},
        {"label": "Debito finanziario", "value": round(base * 50.0, 2)},
    ]
    cnc = [
        {"label": "N° Fornitori", "value": int(base)},
        {"label": "N° Dipendenti", "value": int(base / 2) if base else 0},
        {"label": "N° Banche", "value": int(max(base - 1, 0))},
    ]
    lg = [
        {"label": "Privilegiati", "percent": 0.5, "amount": round(base * 100.0 * 0.5, 2)},
        {"label": "Chirografari", "percent": 0.2, "amount": round(base * 100.0 * 0.2, 2)},
        {"label": "Altri", "percent": 0.1, "amount": round(base * 100.0 * 0.1, 2)},
    ]

    # ----------------------------
    # NEW: Compute SP in DB con fallback periodo
    # - La funzione gh_compute_sp applica:
    #   * se TUTTI i period_end sono NULL -> niente filtro per periodo (fallback)
    #   * altrimenti filtra su MAX(period_end)
    #   * mapping per prefisso più lungo (stg_map_sp) e scrive in fin_sp_riclass
    # ----------------------------
    try:
        db.execute(text("SELECT gh_compute_sp(:slug)"), {"slug": case.slug})
        db.commit()
    except Exception as ex:
        log.exception("Errore durante gh_compute_sp(%s): %s", case.slug, ex)
        raise HTTPException(status_code=500, detail="Errore compute SP")

    # Feedback rapido: quante righe SP sono state scritte
    try:
        sp_rows = db.execute(
            text("SELECT COUNT(*) FROM fin_sp_riclass WHERE case_id = :slug"),
            {"slug": case.slug},
        ).scalar() or 0
    except Exception:
        sp_rows = 0

    return {"kpis": kpis, "cnc": cnc, "lg": lg, "fin_sp_rows": sp_rows}


# ----------------------------
# Endpoint: report (stub)
# ----------------------------
@router.post("/{case_id}/report", status_code=status.HTTP_201_CREATED)
def generate_report(case_id: str, db: Session = Depends(get_db)) -> dict:
    case = _get_case_by_any(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    # Qui potrai in futuro generare il report vero; per ora coda una richiesta fittizia.
    return {"case_id": case.slug, "status": "queued"}
