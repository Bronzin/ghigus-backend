# app/services/cruscotto.py
"""
Cruscotto: aggregazione dati per dashboard.
  CE riassunto per N periodi, cash flow summary, DSCR, SP sintetico.
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict, List

from app.db.models.mdm_projections import (
    MdmCeProjection, MdmSpProjection,
    MdmCflowProjection, MdmBancaProjection,
)
from app.services.assumptions import get_assumptions_or_default
from app.services.timeline import build_timeline

D = Decimal
ZERO = D(0)


def get_cruscotto(db: Session, case_id: str, scenario_id: str = "base", num_periods: int = 10) -> dict:
    """
    Genera dati aggregati per il cruscotto.

    Args:
        scenario_id: scenario da visualizzare
        num_periods: numero di periodi annuali da mostrare (default 10)
    """
    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    piano = assumptions.piano
    timeline = build_timeline(piano.start_year, piano.start_month, piano.duration_months)

    # ── CE per periodo ──
    ce_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmCeProjection).filter(
        MdmCeProjection.case_id == case_id, MdmCeProjection.scenario_id == scenario_id
    ).all():
        ce_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    # ── Banca per periodo ──
    banca_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmBancaProjection).filter(
        MdmBancaProjection.case_id == case_id, MdmBancaProjection.scenario_id == scenario_id
    ).all():
        banca_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    # ── CFlow per periodo ──
    cflow_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmCflowProjection).filter(
        MdmCflowProjection.case_id == case_id, MdmCflowProjection.scenario_id == scenario_id
    ).all():
        cflow_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    # Aggrega per anno (12 mesi ciascuno)
    periods = []
    months_per_period = 12
    total_ricavi = ZERO
    total_ebitda = ZERO
    total_utile = ZERO
    total_flusso = ZERO
    total_fcfo = ZERO
    total_servizio_debito = ZERO

    for year_idx in range(num_periods):
        start_pi = year_idx * months_per_period
        end_pi = start_pi + months_per_period

        ricavi = ZERO
        ebitda = ZERO
        utile = ZERO
        flusso = ZERO
        saldo = ZERO
        fcfo = ZERO
        servizio_debito = ZERO

        for pi in range(start_pi, min(end_pi, len(timeline))):
            ce = ce_map.get(pi, {})
            banca = banca_map.get(pi, {})
            cflow = cflow_map.get(pi, {})

            ricavi += ce.get("RICAVI", ZERO)
            ebitda += ce.get("EBITDA", ZERO)
            utile += ce.get("UTILE_NETTO", ZERO)
            flusso += banca.get("FLUSSO_NETTO", ZERO)
            saldo = banca.get("SALDO_PROGRESSIVO", ZERO)

            fcfo += cflow.get("FLUSSO_GESTIONE_REDD", ZERO)
            servizio_debito += abs(ce.get("ONERI_FINANZIARI", ZERO))

        total_ricavi += ricavi
        total_ebitda += ebitda
        total_utile += utile
        total_flusso += flusso
        total_fcfo += fcfo
        total_servizio_debito += servizio_debito

        label = f"Anno {year_idx + 1}"
        if start_pi < len(timeline):
            t = timeline[start_pi]
            label = f"{t.year}"

        periods.append({
            "period_index": year_idx,
            "label": label,
            "ricavi": float(ricavi),
            "ebitda": float(ebitda),
            "utile_netto": float(utile),
            "flusso_cassa": float(flusso),
            "saldo_banca": float(saldo),
        })

    # DSCR = FCFO / Servizio Debito
    dscr = float(total_fcfo / total_servizio_debito) if total_servizio_debito > 0 else 0.0

    # SP sintetico (ultimo periodo)
    last_pi = len(timeline) - 1
    sp_rows = (
        db.query(MdmSpProjection)
        .filter(
            MdmSpProjection.case_id == case_id,
            MdmSpProjection.scenario_id == scenario_id,
            MdmSpProjection.period_index == last_pi,
            MdmSpProjection.is_subtotal == True,
        )
        .all()
    )
    sp_sintetico = {row.line_code: float(row.amount or 0) for row in sp_rows}

    return {
        "case_id": case_id,
        "scenario_id": scenario_id,
        "periods": periods,
        "dscr": dscr,
        "sp_sintetico": sp_sintetico,
        "totali": {
            "ricavi": float(total_ricavi),
            "ebitda": float(total_ebitda),
            "utile_netto": float(total_utile),
            "flusso_cassa": float(total_flusso),
        },
    }
