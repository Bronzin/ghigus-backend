# app/api/routers/xbrl_facts.py
"""Endpoint per accesso ai fatti XBRL e dati riclassificati multi-anno."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func, extract
from typing import Optional, List
from collections import defaultdict

from app.db.session import get_db
from app.db.models.staging import XbrlFact
from app.db.models.final import SpRiclass, CeRiclass, KpiStandard
from app.schemas.xbrl import (
    XbrlFactOut, XbrlFactsResponse,
    XbrlSummaryRow, XbrlKpiRow, XbrlSummaryResponse,
    XbrlUnmappedResponse, XbrlUnmappedConcept,
)
from app.services.xbrl_mapping import classify_xbrl_fact

router = APIRouter(tags=["xbrl"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


# ── GET xbrl-facts ───────────────────────────────────────────────
@router.get("/cases/{slug}/xbrl-facts", response_model=XbrlFactsResponse)
def list_xbrl_facts(
    slug: str,
    year: Optional[int] = Query(None, description="Filtra per anno (instant o end_date)"),
    concept: Optional[str] = Query(None, description="Filtro LIKE sul concept"),
    numeric_only: bool = Query(False, description="Solo fatti con valore numerico"),
    db: Session = Depends(get_db),
):
    _ensure_case(db, slug)
    q = db.query(XbrlFact).filter(XbrlFact.case_id == slug)

    if year is not None:
        q = q.filter(
            (extract("year", XbrlFact.instant) == year) |
            (extract("year", XbrlFact.end_date) == year)
        )

    if concept:
        q = q.filter(XbrlFact.concept.ilike(f"%{concept}%"))

    if numeric_only:
        q = q.filter(XbrlFact.value.isnot(None))

    facts = q.order_by(XbrlFact.concept, XbrlFact.id).all()
    return XbrlFactsResponse(case_id=slug, facts=facts, count=len(facts))


# ── GET xbrl-summary ────────────────────────────────────────────
@router.get("/cases/{slug}/xbrl-summary", response_model=XbrlSummaryResponse)
def xbrl_summary(
    slug: str,
    db: Session = Depends(get_db),
):
    """Dati riclassificati SP/CE/KPI raggruppati per anno (solo righe con period != None)."""
    _ensure_case(db, slug)

    # Raccogli tutti i period distinti
    sp_periods = {r[0] for r in db.query(SpRiclass.period).filter(
        SpRiclass.case_id == slug, SpRiclass.period.isnot(None)
    ).distinct().all()}
    ce_periods = {r[0] for r in db.query(CeRiclass.period).filter(
        CeRiclass.case_id == slug, CeRiclass.period.isnot(None)
    ).distinct().all()}
    kpi_periods = {r[0] for r in db.query(KpiStandard.period).filter(
        KpiStandard.case_id == slug, KpiStandard.period.isnot(None)
    ).distinct().all()}

    all_periods = sorted(sp_periods | ce_periods | kpi_periods, reverse=True)

    # SP rows
    sp_rows_raw = db.query(SpRiclass).filter(
        SpRiclass.case_id == slug, SpRiclass.period.isnot(None)
    ).all()
    sp_map: dict[str, XbrlSummaryRow] = {}
    for r in sp_rows_raw:
        if r.riclass_code not in sp_map:
            sp_map[r.riclass_code] = XbrlSummaryRow(
                riclass_code=r.riclass_code,
                riclass_desc=r.riclass_desc,
                amounts={},
            )
        sp_map[r.riclass_code].amounts[r.period] = float(r.amount) if r.amount else None

    # CE rows
    ce_rows_raw = db.query(CeRiclass).filter(
        CeRiclass.case_id == slug, CeRiclass.period.isnot(None)
    ).all()
    ce_map: dict[str, XbrlSummaryRow] = {}
    for r in ce_rows_raw:
        if r.riclass_code not in ce_map:
            ce_map[r.riclass_code] = XbrlSummaryRow(
                riclass_code=r.riclass_code,
                riclass_desc=r.riclass_desc,
                amounts={},
            )
        ce_map[r.riclass_code].amounts[r.period] = float(r.amount) if r.amount else None

    # KPI rows
    kpi_rows_raw = db.query(KpiStandard).filter(
        KpiStandard.case_id == slug, KpiStandard.period.isnot(None)
    ).all()
    kpi_map: dict[str, XbrlKpiRow] = {}
    for r in kpi_rows_raw:
        if r.name not in kpi_map:
            kpi_map[r.name] = XbrlKpiRow(name=r.name, unit=r.unit, values={})
        kpi_map[r.name].values[r.period] = float(r.value) if r.value else None

    return XbrlSummaryResponse(
        case_id=slug,
        periods=all_periods,
        sp=list(sp_map.values()),
        ce=list(ce_map.values()),
        kpi=list(kpi_map.values()),
    )


# ── GET xbrl-unmapped ──────────────────────────────────────────
@router.get("/cases/{slug}/xbrl-unmapped", response_model=XbrlUnmappedResponse)
def xbrl_unmapped(
    slug: str,
    numeric_only: bool = Query(True, description="Solo concept con valore numerico"),
    db: Session = Depends(get_db),
):
    """Concept distinti in stg_xbrl_facts che non hanno corrispondenza in xbrl_mapping."""
    _ensure_case(db, slug)

    q = db.query(
        XbrlFact.concept,
        func.count(XbrlFact.id).label("count"),
    ).filter(XbrlFact.case_id == slug)

    if numeric_only:
        q = q.filter(XbrlFact.value.isnot(None))

    rows = q.group_by(XbrlFact.concept).order_by(func.count(XbrlFact.id).desc()).all()

    unmapped = []
    mapped_count = 0
    for concept, cnt in rows:
        result = classify_xbrl_fact(concept)
        if result is None:
            unmapped.append(XbrlUnmappedConcept(concept=concept, count=cnt))
        else:
            mapped_count += 1

    return XbrlUnmappedResponse(
        case_id=slug,
        unmapped=unmapped,
        unmapped_count=len(unmapped),
        mapped_count=mapped_count,
    )
