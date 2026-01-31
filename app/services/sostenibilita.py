# app/services/sostenibilita.py
"""Indicatore di sostenibilita' del piano in tempo reale.

Verifica mese per mese se la cassa disponibile copre i pagamenti previsti
dal concordato. Ritorna un semaforo per ogni mese.
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict

from app.db.models.mdm_projections import MdmBancaProjection
from app.db.models.mdm_concordato import MdmConcordatoMonthly

D = Decimal
ZERO = D(0)


def compute_sostenibilita(db: Session, case_id: str, scenario_id: str = "base") -> Dict:
    """
    Calcola l'indicatore di sostenibilita' mese per mese.

    Per ogni mese:
      - saldo_banca: saldo progressivo dalla proiezione banca
      - pagamenti_concordato: somma pagamenti effettivi concordato
      - avanzo: saldo_banca - pagamenti_concordato_cumulativi
      - status: GREEN (avanzo > 5%), YELLOW (0-5%), RED (negativo)

    Ritorna:
      - months: lista di {period_index, saldo_banca, pagamenti, avanzo, status}
      - overall: GREEN / YELLOW / RED
      - first_red: primo mese in cui va in rosso (o null)
      - min_avanzo: avanzo minimo nel piano
    """
    # Saldo progressivo banca
    banca_rows = (
        db.query(MdmBancaProjection)
        .filter(MdmBancaProjection.case_id == case_id,
                MdmBancaProjection.scenario_id == scenario_id,
                MdmBancaProjection.line_code == "SALDO_PROGRESSIVO")
        .order_by(MdmBancaProjection.period_index)
        .all()
    )
    saldo_by_period: Dict[int, D] = {r.period_index: r.amount or ZERO for r in banca_rows}

    # Pagamenti concordato per periodo
    conc_rows = (
        db.query(MdmConcordatoMonthly)
        .filter(MdmConcordatoMonthly.case_id == case_id,
                MdmConcordatoMonthly.scenario_id == scenario_id)
        .all()
    )
    pagamenti_by_period: Dict[int, D] = {}
    for r in conc_rows:
        pagamenti_by_period[r.period_index] = (
            pagamenti_by_period.get(r.period_index, ZERO) + (r.pagamento or ZERO)
        )

    if not saldo_by_period:
        return {
            "months": [],
            "overall": "GREY",
            "first_red": None,
            "min_avanzo": None,
        }

    months = []
    first_red = None
    min_avanzo = None
    pagamenti_cumulativi = ZERO

    for pi in sorted(saldo_by_period.keys()):
        saldo = saldo_by_period[pi]
        pag = pagamenti_by_period.get(pi, ZERO)
        pagamenti_cumulativi += pag
        avanzo = saldo - pagamenti_cumulativi

        if min_avanzo is None or avanzo < min_avanzo:
            min_avanzo = avanzo

        # Semaforo
        if avanzo < ZERO:
            status = "RED"
            if first_red is None:
                first_red = pi
        elif saldo > ZERO and avanzo / saldo < D("0.05"):
            status = "YELLOW"
        else:
            status = "GREEN"

        months.append({
            "period_index": pi,
            "saldo_banca": float(saldo),
            "pagamenti": float(pag),
            "pagamenti_cumulativi": float(pagamenti_cumulativi),
            "avanzo": float(avanzo),
            "status": status,
        })

    # Overall
    statuses = [m["status"] for m in months]
    if "RED" in statuses:
        overall = "RED"
    elif "YELLOW" in statuses:
        overall = "YELLOW"
    else:
        overall = "GREEN"

    return {
        "months": months,
        "overall": overall,
        "first_red": first_red,
        "min_avanzo": float(min_avanzo) if min_avanzo is not None else None,
    }
