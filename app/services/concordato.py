# app/services/concordato.py
"""
Piano concordatario con scheduling dettagliato per classe creditore.

Ogni classe creditore ha un proprio schedule di pagamento:
  - pct_soddisfazione_proposta: % del credito ammesso proposta dal piano
  - mese_inizio/fine: finestra temporale dei pagamenti (grace period + durata)
  - tipo_pagamento: RATEALE (rate costanti) o UNICO (lump sum)
  - priorita: ordine di distribuzione in caso di cassa insufficiente

Il motore:
  1. Calcola per ciascuna classe il pagamento totale proposto
  2. Calcola la rata mensile pianificata (costante per RATEALE, unica per UNICO)
  3. Per ogni mese, distribuisce la cassa disponibile in ordine di priorità
  4. Tiene traccia del pagamento cumulativo e % soddisfazione effettiva
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict

from app.db.models.mdm_concordato import MdmConcordatoMonthly
from app.db.models.mdm_passivo import MdmPassivoItem
from app.db.models.mdm_projections import MdmBancaProjection
from app.services.assumptions import get_assumptions_or_default
from app.schemas.assumptions import ClasseCreditoreSchedule

D = Decimal
ZERO = D(0)


def _compute_class_schedule(
    schedule: ClasseCreditoreSchedule,
    debito_ammesso: D,
    duration: int,
) -> Dict:
    """
    Pre-calcola lo schedule di pagamento per una classe creditore.
    Restituisce dict con: pagamento_proposto, rata_mensile, mese_inizio, mese_fine,
                          rate_per_month (dict period_index → rata pianificata).
    """
    pct = D(str(schedule.pct_soddisfazione_proposta)) / 100
    pagamento_proposto = (debito_ammesso * pct).quantize(D("0.01"))

    mese_inizio = schedule.mese_inizio_pagamento
    mese_fine = min(schedule.mese_fine_pagamento, duration - 1)

    rate_per_month: Dict[int, D] = {}

    if pagamento_proposto <= ZERO or mese_inizio > mese_fine:
        return {
            "pagamento_proposto": pagamento_proposto,
            "rata_mensile": ZERO,
            "mese_inizio": mese_inizio,
            "mese_fine": mese_fine,
            "rate_per_month": rate_per_month,
        }

    if schedule.tipo_pagamento == "UNICO":
        # Pagamento unico al mese_inizio
        rate_per_month[mese_inizio] = pagamento_proposto
        rata_mensile = pagamento_proposto
    else:
        # RATEALE: rate costanti nella finestra
        n_rate = mese_fine - mese_inizio + 1
        rata_base = (pagamento_proposto / n_rate).quantize(D("0.01"))
        # Distribuisci arrotondamento sull'ultima rata
        total_rate = rata_base * n_rate
        diff = pagamento_proposto - total_rate

        for pi in range(mese_inizio, mese_fine + 1):
            rate_per_month[pi] = rata_base
        # Aggiusta l'ultima rata per arrotondamento
        if diff != ZERO and mese_fine in rate_per_month:
            rate_per_month[mese_fine] += diff

        rata_mensile = rata_base

    return {
        "pagamento_proposto": pagamento_proposto,
        "rata_mensile": rata_mensile,
        "mese_inizio": mese_inizio,
        "mese_fine": mese_fine,
        "rate_per_month": rate_per_month,
    }


def compute_concordato(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Distribuzione mensile ai creditori con scheduling per classe.
    Pattern: delete-recompute-insert.
    """
    db.query(MdmConcordatoMonthly).filter(
        MdmConcordatoMonthly.case_id == case_id,
        MdmConcordatoMonthly.scenario_id == scenario_id,
    ).delete()

    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    duration = assumptions.piano.duration_months
    conc_params = assumptions.concordato
    usa_cassa = conc_params.usa_cassa_disponibile

    # ── 1. Debiti per classe creditore ──
    passivo_items = db.query(MdmPassivoItem).filter(
        MdmPassivoItem.case_id == case_id,
        MdmPassivoItem.scenario_id == scenario_id,
        MdmPassivoItem.category != "PATRIMONIO_NETTO",
    ).all()

    debiti_per_classe: Dict[str, D] = {}
    for item in passivo_items:
        classe = item.tipologia_creditore or "CHIROGRAFARIO"
        debiti_per_classe[classe] = debiti_per_classe.get(classe, ZERO) + abs(item.passivo_rettificato or ZERO)

    # ── 2. Pre-calcola schedule per ciascuna classe ──
    # Ordina per priorità
    classi_sorted = sorted(conc_params.classi, key=lambda c: c.priorita)

    class_schedules = []
    for sched in classi_sorted:
        debito = debiti_per_classe.get(sched.classe, ZERO)
        info = _compute_class_schedule(sched, debito, duration)
        info["classe"] = sched.classe
        info["debito_ammesso"] = debito
        info["priorita"] = sched.priorita
        class_schedules.append(info)

    # ── 3. Flusso netto per periodo dalla banca ──
    flusso_by_period: Dict[int, D] = {}
    if usa_cassa:
        banca_rows = (
            db.query(MdmBancaProjection)
            .filter(MdmBancaProjection.case_id == case_id,
                    MdmBancaProjection.scenario_id == scenario_id,
                    MdmBancaProjection.line_code == "SALDO_PROGRESSIVO")
            .all()
        )
        for r in banca_rows:
            flusso_by_period[r.period_index] = r.amount or ZERO

    # ── 4. Distribuzione mensile ──
    # Stato rolling per classe
    pagato_cumulativo: Dict[str, D] = {cs["classe"]: ZERO for cs in class_schedules}
    debiti_residui: Dict[str, D] = {cs["classe"]: cs["debito_ammesso"] for cs in class_schedules}

    count = 0

    for pi in range(duration):
        # Cassa disponibile per questo mese
        if usa_cassa:
            # Usa il saldo progressivo come indicatore di cassa disponibile
            cassa_mese = max(flusso_by_period.get(pi, ZERO), ZERO)
        else:
            cassa_mese = D("999999999")  # illimitata

        cassa_rimanente = cassa_mese

        for cs in class_schedules:
            classe = cs["classe"]
            debito_ammesso = cs["debito_ammesso"]
            pagamento_proposto = cs["pagamento_proposto"]
            rata_pianificata = cs["rate_per_month"].get(pi, ZERO)
            debito_inizio = debiti_residui[classe]

            # Il pagamento è il minore tra: rata pianificata, debito residuo, cassa disponibile
            pagamento_effettivo = min(rata_pianificata, debito_inizio)
            if usa_cassa:
                pagamento_effettivo = min(pagamento_effettivo, cassa_rimanente)

            cassa_rimanente -= pagamento_effettivo
            pagato_cumulativo[classe] += pagamento_effettivo
            debiti_residui[classe] = debito_inizio - pagamento_effettivo

            pct = (pagato_cumulativo[classe] / debito_ammesso * 100).quantize(D("0.01")) if debito_ammesso > ZERO else ZERO

            db.add(MdmConcordatoMonthly(
                case_id=case_id,
                scenario_id=scenario_id,
                period_index=pi,
                creditor_class=classe,
                debito_iniziale=debito_inizio,
                pagamento_proposto=pagamento_proposto,
                rata_pianificata=rata_pianificata,
                pagamento=pagamento_effettivo,
                pagamento_cumulativo=pagato_cumulativo[classe],
                debito_residuo=debiti_residui[classe],
                pct_soddisfazione=pct,
            ))
            count += 1

    db.commit()
    return count


def get_concordato(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmConcordatoMonthly]:
    return (
        db.query(MdmConcordatoMonthly)
        .filter(
            MdmConcordatoMonthly.case_id == case_id,
            MdmConcordatoMonthly.scenario_id == scenario_id,
        )
        .order_by(MdmConcordatoMonthly.period_index, MdmConcordatoMonthly.id)
        .all()
    )
