# app/services/banca_projection.py
"""
Proiezione Banca - Metodo diretto:
  Entrate (incassi clienti, vendite, finanziamenti, affitto, cessione)
  - Uscite (fornitori, personale, tasse, debiti, prededuzioni, IVA)
  = Saldo disponibile
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict, List

from app.db.models.mdm_projections import MdmBancaProjection, MdmCeProjection
from app.services.assumptions import get_assumptions_or_default
from app.services.prededuzione import get_prededuzione
from app.services.affitto import get_affitto
from app.services.cessione import get_cessione
from app.services.iva_settlement import compute_iva_monthly
from app.services.finanziamenti import get_all_finanziamenti_by_period
from app.db.models.mdm_attivo_schedule import MdmAttivoSchedule

D = Decimal
ZERO = D(0)


def compute_banca_projections(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Computa le proiezioni Banca su 120 mesi.
    Pattern: delete-recompute-insert.
    """
    db.query(MdmBancaProjection).filter(MdmBancaProjection.case_id == case_id).filter(MdmBancaProjection.scenario_id == scenario_id).delete()

    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    piano = assumptions.piano
    duration = piano.duration_months
    aliq_iva_vendite = D(str(piano.aliquota_iva_vendite)) / 100
    aliq_iva_acquisti = D(str(piano.aliquota_iva_acquisti)) / 100

    # CE per periodo
    ce_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmCeProjection).filter(MdmCeProjection.case_id == case_id).filter(MdmCeProjection.scenario_id == scenario_id).all():
        ce_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    # Prededuzioni
    preded_rows = get_prededuzione(db, case_id, scenario_id)
    preded_by_period: Dict[int, D] = {}
    for r in preded_rows:
        preded_by_period[r.period_index] = preded_by_period.get(r.period_index, ZERO) + (r.importo_periodo or ZERO)

    # Affitto (incasso)
    affitto_rows = get_affitto(db, case_id, scenario_id)
    affitto_incasso: Dict[int, D] = {}
    for r in affitto_rows:
        affitto_incasso[r.period_index] = r.incasso or ZERO

    # Cessione (netto)
    cessione_rows = get_cessione(db, case_id, scenario_id)
    cessione_by_period: Dict[int, D] = {}
    for r in cessione_rows:
        if r.component == "NETTO":
            cessione_by_period[r.period_index] = r.amount or ZERO

    # IVA mensile
    iva_debito_list = []
    iva_credito_list = []
    for pi in range(duration):
        ce = ce_map.get(pi, {})
        ricavi = abs(ce.get("RICAVI", ZERO))
        # Acquisti soggetti IVA: materie prime + servizi + godimento beni terzi
        costi_mp = abs(ce.get("MATERIE_PRIME", ZERO))
        costi_serv = abs(ce.get("SERVIZI", ZERO))
        costi_god = abs(ce.get("GODIMENTO_TERZI", ZERO))
        iva_debito_list.append(ricavi * aliq_iva_vendite)
        iva_credito_list.append((costi_mp + costi_serv + costi_god) * aliq_iva_acquisti)

    iva_pagamenti = compute_iva_monthly(iva_debito_list, iva_credito_list, delay_months=1)

    # Nuovi finanziamenti: erogazioni (entrate) e rate (uscite)
    fin_by_period = get_all_finanziamenti_by_period(db, case_id, scenario_id)

    # Attivo schedule: incassi mensili programmati per le voci attivo del caso
    from app.db.models.mdm_attivo import MdmAttivoItem
    attivo_item_ids = [
        r.id for r in db.query(MdmAttivoItem.id).filter(
            MdmAttivoItem.case_id == case_id,
            MdmAttivoItem.scenario_id == scenario_id,
        ).all()
    ]
    attivo_sched_by_period: Dict[int, D] = {}
    if attivo_item_ids:
        sched_rows = db.query(MdmAttivoSchedule).filter(
            MdmAttivoSchedule.attivo_item_id.in_(attivo_item_ids)
        ).all()
        for r in sched_rows:
            attivo_sched_by_period[r.period_index] = (
                attivo_sched_by_period.get(r.period_index, ZERO) + (r.importo or ZERO)
            )

    count = 0
    saldo_progressivo = ZERO

    for pi in range(duration):
        ce = ce_map.get(pi, {})

        # ── ENTRATE ──
        incasso_clienti = abs(ce.get("RICAVI", ZERO))
        incasso_affitto = affitto_incasso.get(pi, ZERO)
        incasso_cessione = cessione_by_period.get(pi, ZERO)
        fin_period = fin_by_period.get(pi, {})
        erogazione_fin = fin_period.get("erogazione", ZERO)
        incasso_attivo_sched = attivo_sched_by_period.get(pi, ZERO)
        totale_entrate = incasso_clienti + incasso_affitto + incasso_cessione + erogazione_fin + incasso_attivo_sched

        entrate_lines = [
            ("INCASSO_CLIENTI", "Incassi da clienti", incasso_clienti),
            ("INCASSO_AFFITTO", "Incasso affitto azienda", incasso_affitto),
            ("INCASSO_CESSIONE", "Incasso cessione azienda", incasso_cessione),
            ("EROGAZIONE_FIN", "Erogazione nuovi finanziamenti", erogazione_fin),
            ("INCASSO_ATTIVO", "Incassi attivo schedulati", incasso_attivo_sched),
            ("TOTALE_ENTRATE", "Totale entrate", totale_entrate),
        ]

        for code, label, amount in entrate_lines:
            db.add(MdmBancaProjection(
                case_id=case_id, scenario_id=scenario_id, period_index=pi,
                line_code=code, line_label=label,
                section="ENTRATE",
                amount=amount.quantize(D("0.01")),
            ))
            count += 1

        # ── USCITE ──
        # Fornitori = materie prime + servizi + godimento beni terzi
        pag_fornitori = abs(ce.get("MATERIE_PRIME", ZERO)) + abs(ce.get("SERVIZI", ZERO)) + abs(ce.get("GODIMENTO_TERZI", ZERO))
        pag_personale = abs(ce.get("COSTI_PERSONALE", ZERO))
        pag_altri = abs(ce.get("ONERI_DIVERSI", ZERO)) + abs(ce.get("COSTI_AFFITTO", ZERO))
        pag_prededuzione = preded_by_period.get(pi, ZERO)
        pag_imposte = abs(ce.get("TOT_IMPOSTE", ZERO))
        pag_iva = max(iva_pagamenti[pi], ZERO) if pi < len(iva_pagamenti) else ZERO
        pag_oneri_fin = abs(ce.get("ONERI_FINANZIARI", ZERO))

        rata_fin = fin_period.get("rata", ZERO)
        totale_uscite = pag_fornitori + pag_personale + pag_altri + pag_prededuzione + pag_imposte + pag_iva + pag_oneri_fin + rata_fin

        uscite_lines = [
            ("PAG_FORNITORI", "Pagamenti fornitori", pag_fornitori),
            ("PAG_PERSONALE", "Pagamenti personale", pag_personale),
            ("PAG_ALTRI", "Altri pagamenti operativi", pag_altri),
            ("PAG_PREDEDUZIONI", "Pagamenti prededuzioni", pag_prededuzione),
            ("PAG_IMPOSTE", "Pagamenti imposte", pag_imposte),
            ("PAG_IVA", "Pagamento IVA", pag_iva),
            ("PAG_ONERI_FIN", "Pagamenti oneri finanziari", pag_oneri_fin),
            ("RATA_FINANZIAMENTI", "Rate nuovi finanziamenti", rata_fin),
            ("TOTALE_USCITE", "Totale uscite", totale_uscite),
        ]

        for code, label, amount in uscite_lines:
            db.add(MdmBancaProjection(
                case_id=case_id, scenario_id=scenario_id, period_index=pi,
                line_code=code, line_label=label,
                section="USCITE",
                amount=amount.quantize(D("0.01")),
            ))
            count += 1

        # ── SALDI ──
        flusso_netto = totale_entrate - totale_uscite
        saldo_progressivo += flusso_netto

        saldi_lines = [
            ("FLUSSO_NETTO", "Flusso netto periodo", flusso_netto),
            ("SALDO_PROGRESSIVO", "Saldo progressivo", saldo_progressivo),
        ]

        for code, label, amount in saldi_lines:
            db.add(MdmBancaProjection(
                case_id=case_id, scenario_id=scenario_id, period_index=pi,
                line_code=code, line_label=label,
                section="SALDI",
                amount=amount.quantize(D("0.01")),
            ))
            count += 1

    db.commit()
    return count


def get_banca_projections(db: Session, case_id: str, scenario_id: str = "base", period_from: int = 0, period_to: int = 119) -> list:
    return (
        db.query(MdmBancaProjection)
        .filter(
            MdmBancaProjection.case_id == case_id,
            MdmBancaProjection.scenario_id == scenario_id,
            MdmBancaProjection.period_index >= period_from,
            MdmBancaProjection.period_index <= period_to,
        )
        .order_by(MdmBancaProjection.period_index, MdmBancaProjection.id)
        .all()
    )
