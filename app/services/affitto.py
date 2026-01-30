# app/services/affitto.py
"""
Calcolo affitto d'azienda:
  canone mensile = canone_annuo / 12
  IVA = canone × aliquota_iva / 100
  totale = canone + IVA
  incasso = totale con dilazione di N mesi
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from app.db.models.mdm_affitto import MdmAffittoMonthly
from app.services.assumptions import get_assumptions_or_default


def compute_affitto(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Calcola l'affitto mensile a partire dalle assumptions.
    Pattern: delete-recompute-insert.
    """
    db.query(MdmAffittoMonthly).filter(
        MdmAffittoMonthly.case_id == case_id,
        MdmAffittoMonthly.scenario_id == scenario_id,
    ).delete()

    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    params = assumptions.affitto
    piano = assumptions.piano

    canone_annuo = Decimal(str(params.canone_annuo))
    if canone_annuo <= 0:
        db.commit()
        return 0

    canone_mensile = (canone_annuo / 12).quantize(Decimal("0.01"))
    aliquota_iva = Decimal(str(params.aliquota_iva)) / 100
    dilazione = params.mesi_dilazione_incasso
    mese_inizio = params.mese_inizio
    mese_fine = params.mese_fine
    duration = piano.duration_months

    # Pre-calcola totali mensili
    totali = []
    for pi in range(duration):
        if mese_inizio <= pi <= mese_fine:
            canone = canone_mensile
            iva = (canone * aliquota_iva).quantize(Decimal("0.01"))
            totale = canone + iva
        else:
            canone = Decimal(0)
            iva = Decimal(0)
            totale = Decimal(0)
        totali.append((canone, iva, totale))

    count = 0
    for pi in range(duration):
        canone, iva, totale = totali[pi]
        # Incasso con dilazione
        source_pi = pi - dilazione
        if 0 <= source_pi < duration:
            incasso = totali[source_pi][2]  # totale del periodo precedente
        else:
            incasso = Decimal(0)

        db.add(MdmAffittoMonthly(
            case_id=case_id,
            scenario_id=scenario_id,
            period_index=pi,
            canone=canone,
            iva=iva,
            totale=totale,
            incasso=incasso,
        ))
        count += 1

    db.commit()
    return count


def get_affitto(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmAffittoMonthly]:
    return (
        db.query(MdmAffittoMonthly)
        .filter(
            MdmAffittoMonthly.case_id == case_id,
            MdmAffittoMonthly.scenario_id == scenario_id,
        )
        .order_by(MdmAffittoMonthly.period_index)
        .all()
    )
