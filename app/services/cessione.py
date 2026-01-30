# app/services/cessione.py
"""
Calcolo cessione d'azienda:
  Importo lordo - accollo TFR - accollo debiti = netto
  Scheduling nel mese di cessione.
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from app.db.models.mdm_cessione import MdmCessioneMonthly
from app.services.assumptions import get_assumptions_or_default


def compute_cessione(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Calcola la cessione d'azienda a partire dalle assumptions.
    Pattern: delete-recompute-insert.
    """
    db.query(MdmCessioneMonthly).filter(
        MdmCessioneMonthly.case_id == case_id,
        MdmCessioneMonthly.scenario_id == scenario_id,
    ).delete()

    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    params = assumptions.cessione
    piano = assumptions.piano

    lordo = Decimal(str(params.importo_lordo))
    if lordo <= 0:
        db.commit()
        return 0

    accollo_tfr = Decimal(str(params.accollo_tfr))
    accollo_debiti = Decimal(str(params.accollo_debiti))
    netto = lordo - accollo_tfr - accollo_debiti
    mese_cessione = params.mese_cessione
    duration = piano.duration_months

    components = [
        ("LORDO", lordo),
        ("ACCOLLO_TFR", -accollo_tfr),
        ("ACCOLLO_DEBITI", -accollo_debiti),
        ("NETTO", netto),
    ]

    count = 0
    for pi in range(duration):
        for comp_name, comp_amount in components:
            amount = comp_amount if pi == mese_cessione else Decimal(0)
            db.add(MdmCessioneMonthly(
                case_id=case_id,
                scenario_id=scenario_id,
                period_index=pi,
                component=comp_name,
                amount=amount,
            ))
            count += 1

    db.commit()
    return count


def get_cessione(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmCessioneMonthly]:
    return (
        db.query(MdmCessioneMonthly)
        .filter(
            MdmCessioneMonthly.case_id == case_id,
            MdmCessioneMonthly.scenario_id == scenario_id,
        )
        .order_by(MdmCessioneMonthly.period_index, MdmCessioneMonthly.component)
        .all()
    )
