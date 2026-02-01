# app/services/mdm_engine.py
"""
Orchestratore pipeline MDM completa.
Esegue l'intera pipeline in ordine di dipendenza:
  1. Attivo + Passivo (da riclassificato)
  2. Liquidazione giudiziale + Test PIAT
  3. Prededuzioni + Affitto + Cessione (da assumptions)
  4. Proiezioni mensili: CE → SP → CFlow → Banca (con loop convergenza)
  5. Concordato (da banca + passivo)

Il loop di convergenza SP↔Banca (fase 4) itera fino a quando:
  - SP.CASSA ≈ Banca.SALDO_PROGRESSIVO (delta < threshold)
  - oppure si raggiunge il numero massimo di iterazioni

Ad ogni iterazione:
  - Si leggono i debiti M/L dallo SP
  - Si calcolano gli oneri finanziari dinamici = debito_ML × tasso / 12
  - Si ricalcola CE (con interest override) → SP → CFlow → Banca
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict

from app.db.models.mdm_projections import MdmSpProjection, MdmBancaProjection
from app.services.processing import compute_case
from app.services.attivo import seed_attivo_from_riclass, compute_attivo_totals
from app.services.passivo import (
    seed_passivo_from_riclass,
    apply_compensazioni_from_attivo,
    compute_passivo_totals,
)
from app.services.liquidazione import compute_liquidazione
from app.services.test_piat import compute_test_piat
from app.services.prededuzione import compute_prededuzione
from app.services.affitto import compute_affitto
from app.services.cessione import compute_cessione
from app.services.ce_projection import compute_ce_projections
from app.services.sp_projection import compute_sp_projections
from app.services.cflow_projection import compute_cflow_projections
from app.services.banca_projection import compute_banca_projections
from app.services.concordato import compute_concordato
from app.services.assumptions import get_assumptions_or_default

D = Decimal
ZERO = D(0)

# Parametri convergenza
MAX_CONVERGENCE_ITERATIONS = 5
CONVERGENCE_THRESHOLD = D("100")  # 100 EUR di tolleranza


def _read_line_by_period(db: Session, model, case_id: str, scenario_id: str, line_code: str) -> Dict[int, D]:
    """Legge una specifica line_code da un modello proiezione, raggruppata per period_index."""
    rows = (
        db.query(model)
        .filter(model.case_id == case_id, model.scenario_id == scenario_id, model.line_code == line_code)
        .all()
    )
    return {r.period_index: r.amount or ZERO for r in rows}


def _compute_max_delta(db: Session, case_id: str, scenario_id: str) -> float:
    """
    Calcola il massimo scostamento assoluto tra SP.CASSA e Banca.SALDO_PROGRESSIVO
    su tutti i periodi. Questo è il criterio di convergenza.
    """
    sp_cassa = _read_line_by_period(db, MdmSpProjection, case_id, scenario_id, "CASSA")
    banca_saldo = _read_line_by_period(db, MdmBancaProjection, case_id, scenario_id, "SALDO_PROGRESSIVO")
    if not sp_cassa or not banca_saldo:
        return 0.0
    max_delta = 0.0
    for pi in sp_cassa:
        delta = abs(float(sp_cassa.get(pi, ZERO)) - float(banca_saldo.get(pi, ZERO)))
        max_delta = max(max_delta, delta)
    return max_delta


def _compute_interest_override(db: Session, case_id: str, scenario_id: str, tasso_annuo: D) -> Dict[int, D]:
    """
    Calcola gli oneri finanziari dinamici per ogni periodo in base al debito M/L dallo SP.
    interest_monthly = debito_lungo × tasso_annuo / 12
    Restituisce {period_index: importo_assoluto_interesse}.
    """
    debiti_lungo = _read_line_by_period(db, MdmSpProjection, case_id, scenario_id, "DEBITI_LUNGO")
    tasso_mensile = tasso_annuo / 12
    override: Dict[int, D] = {}
    for pi, debt in debiti_lungo.items():
        override[pi] = (abs(debt) * tasso_mensile).quantize(D("0.01"))
    return override


def run_full_pipeline(db: Session, case_id: str, scenario_id: str = "base") -> dict:
    """
    Esegue l'intera pipeline MDM in ordine di dipendenza.
    Ritorna un dizionario con i conteggi per ogni fase e info convergenza.
    """
    result = {}

    # FASE 1: Riclassificazione SP/CE/KPI da TB e XBRL
    import logging
    _log = logging.getLogger(__name__)
    try:
        riclass = compute_case(db, case_id)
        result["riclass"] = riclass.get("datamart", {})
    except Exception as e:
        _log.warning("compute_case (riclassificazione) skipped: %s", e)
        db.rollback()
        result["riclass"] = {}

    # FASE 2: Attivo + Passivo
    result["attivo_seed"] = seed_attivo_from_riclass(db, case_id, scenario_id)
    result["attivo_computed"] = compute_attivo_totals(db, case_id, scenario_id)
    result["passivo_seed"] = seed_passivo_from_riclass(db, case_id, scenario_id)
    result["passivo_compensazioni"] = apply_compensazioni_from_attivo(db, case_id, scenario_id)
    result["passivo_computed"] = compute_passivo_totals(db, case_id, scenario_id)

    # FASE 3: Liquidazione + Test PIAT
    result["liquidazione"] = compute_liquidazione(db, case_id, scenario_id)
    result["test_piat"] = compute_test_piat(db, case_id, scenario_id)

    # FASE 4: Prededuzioni + Affitto + Cessione
    result["prededuzione"] = compute_prededuzione(db, case_id, scenario_id)
    result["affitto"] = compute_affitto(db, case_id, scenario_id)
    result["cessione"] = compute_cessione(db, case_id, scenario_id)

    # FASE 5: Proiezioni con loop di convergenza SP↔Banca
    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    tasso = D(str(assumptions.sp_drivers.tasso_interesse_debito)) / 100

    # Pass 1: CE (oneri finanziari statici da riclass) → SP → CFlow → Banca
    result["ce_projections"] = compute_ce_projections(db, case_id, scenario_id)
    result["sp_projections"] = compute_sp_projections(db, case_id, scenario_id)
    result["cflow_projections"] = compute_cflow_projections(db, case_id, scenario_id)
    result["banca_projections"] = compute_banca_projections(db, case_id, scenario_id)

    # Loop di convergenza
    iterations = 0
    max_delta = _compute_max_delta(db, case_id, scenario_id)

    while max_delta > float(CONVERGENCE_THRESHOLD) and iterations < MAX_CONVERGENCE_ITERATIONS:
        iterations += 1

        # Calcola oneri finanziari dinamici dal debito M/L dello SP
        interest_override = _compute_interest_override(db, case_id, scenario_id, tasso)

        # Ricalcola: CE (con override) → SP → CFlow → Banca
        result["ce_projections"] = compute_ce_projections(
            db, case_id, scenario_id, interest_override=interest_override,
        )
        result["sp_projections"] = compute_sp_projections(db, case_id, scenario_id)
        result["cflow_projections"] = compute_cflow_projections(db, case_id, scenario_id)
        result["banca_projections"] = compute_banca_projections(db, case_id, scenario_id)

        max_delta = _compute_max_delta(db, case_id, scenario_id)

    result["convergence"] = {
        "iterations": iterations,
        "max_delta_eur": round(max_delta, 2),
        "converged": max_delta <= float(CONVERGENCE_THRESHOLD),
        "threshold_eur": float(CONVERGENCE_THRESHOLD),
    }

    # FASE 6: Concordato
    result["concordato"] = compute_concordato(db, case_id, scenario_id)

    return result
