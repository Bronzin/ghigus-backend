# app/services/cflow_projection.py
"""
Proiezione Cash Flow - Metodo indiretto OIC 10:
  Utile netto + ammortamenti (non-cash) + delta CCN
  + flussi investimento + flussi finanziamento
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict

from app.db.models.mdm_projections import MdmCflowProjection, MdmCeProjection, MdmSpProjection

D = Decimal
ZERO = D(0)


def compute_cflow_projections(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Computa le proiezioni Cash Flow su 120 mesi.
    Richiede CE e SP già calcolati.
    Pattern: delete-recompute-insert.
    """
    db.query(MdmCflowProjection).filter(MdmCflowProjection.case_id == case_id).filter(MdmCflowProjection.scenario_id == scenario_id).delete()

    # Carica dati CE per periodo
    ce_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmCeProjection).filter(MdmCeProjection.case_id == case_id).filter(MdmCeProjection.scenario_id == scenario_id).all():
        ce_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    # Carica dati SP per periodo
    sp_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmSpProjection).filter(MdmSpProjection.case_id == case_id).filter(MdmSpProjection.scenario_id == scenario_id).all():
        sp_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    if not ce_map:
        db.commit()
        return 0

    duration = max(ce_map.keys()) + 1
    count = 0

    for pi in range(duration):
        ce = ce_map.get(pi, {})
        sp = sp_map.get(pi, {})
        sp_prev = sp_map.get(pi - 1, {}) if pi > 0 else {}

        # ── Gestione reddituale ──
        utile = ce.get("UTILE_NETTO", ZERO)
        ammort = abs(ce.get("TOT_AMMORTAMENTI", ZERO))

        # Delta CCN (variazione crediti, rimanenze, debiti)
        delta_crediti = sp.get("CREDITI_COMM", ZERO) - sp_prev.get("CREDITI_COMM", ZERO)
        delta_rimanenze = sp.get("RIMANENZE", ZERO) - sp_prev.get("RIMANENZE", ZERO)
        delta_debiti_breve = sp.get("DEBITI_BREVE", ZERO) - sp_prev.get("DEBITI_BREVE", ZERO)
        delta_ccn = -delta_crediti - delta_rimanenze + delta_debiti_breve

        flusso_reddituale = utile + ammort + delta_ccn

        lines_redd = [
            ("UTILE_NETTO", "Utile netto", utile),
            ("AMMORTAMENTI", "Ammortamenti (add-back)", ammort),
            ("DELTA_CREDITI", "Variazione crediti commerciali", -delta_crediti),
            ("DELTA_RIMANENZE", "Variazione rimanenze", -delta_rimanenze),
            ("DELTA_DEBITI_BREVE", "Variazione debiti a breve", delta_debiti_breve),
            ("FLUSSO_GESTIONE_REDD", "Flusso gestione reddituale", flusso_reddituale),
        ]

        for code, label, amount in lines_redd:
            db.add(MdmCflowProjection(
                case_id=case_id, scenario_id=scenario_id, period_index=pi,
                line_code=code, line_label=label,
                section="GESTIONE_REDDITUALE",
                amount=amount.quantize(D("0.01")),
            ))
            count += 1

        # ── Investimenti ──
        delta_immob = (
            (sp.get("IMMOB_MATERIALI", ZERO) + sp.get("IMMOB_IMMATERIALI", ZERO) + sp.get("IMMOB_FINANZIARIE", ZERO))
            - (sp_prev.get("IMMOB_MATERIALI", ZERO) + sp_prev.get("IMMOB_IMMATERIALI", ZERO) + sp_prev.get("IMMOB_FINANZIARIE", ZERO))
            + ammort  # ammortamento già dedotto, ri-aggiungiamo per isolarne il flusso di investimento
        )
        flusso_invest = -delta_immob

        lines_invest = [
            ("DELTA_IMMOBILIZZAZIONI", "Investimenti in immobilizzazioni", -delta_immob),
            ("FLUSSO_INVESTIMENTO", "Flusso attività di investimento", flusso_invest),
        ]

        for code, label, amount in lines_invest:
            db.add(MdmCflowProjection(
                case_id=case_id, scenario_id=scenario_id, period_index=pi,
                line_code=code, line_label=label,
                section="INVESTIMENTO",
                amount=amount.quantize(D("0.01")),
            ))
            count += 1

        # ── Finanziamento ──
        delta_debiti_lungo = sp.get("DEBITI_LUNGO", ZERO) - sp_prev.get("DEBITI_LUNGO", ZERO)
        delta_tfr = sp.get("TFR", ZERO) - sp_prev.get("TFR", ZERO)
        flusso_finanz = delta_debiti_lungo + delta_tfr

        lines_fin = [
            ("DELTA_DEBITI_ML", "Variazione debiti M/L", delta_debiti_lungo),
            ("DELTA_TFR", "Variazione TFR", delta_tfr),
            ("FLUSSO_FINANZIAMENTO", "Flusso attività di finanziamento", flusso_finanz),
        ]

        for code, label, amount in lines_fin:
            db.add(MdmCflowProjection(
                case_id=case_id, scenario_id=scenario_id, period_index=pi,
                line_code=code, line_label=label,
                section="FINANZIAMENTO",
                amount=amount.quantize(D("0.01")),
            ))
            count += 1

        # ── Flusso netto totale ──
        flusso_netto = flusso_reddituale + flusso_invest + flusso_finanz
        db.add(MdmCflowProjection(
            case_id=case_id, scenario_id=scenario_id, period_index=pi,
            line_code="FLUSSO_NETTO", line_label="Flusso di cassa netto",
            section="TOTALE",
            amount=flusso_netto.quantize(D("0.01")),
        ))
        count += 1

    db.commit()
    return count


def get_cflow_projections(db: Session, case_id: str, scenario_id: str = "base", period_from: int = 0, period_to: int = 119) -> list:
    return (
        db.query(MdmCflowProjection)
        .filter(
            MdmCflowProjection.case_id == case_id,
            MdmCflowProjection.scenario_id == scenario_id,
            MdmCflowProjection.period_index >= period_from,
            MdmCflowProjection.period_index <= period_to,
        )
        .order_by(MdmCflowProjection.period_index, MdmCflowProjection.id)
        .all()
    )
