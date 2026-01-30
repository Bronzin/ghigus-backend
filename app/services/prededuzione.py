# app/services/prededuzione.py
"""
Calcolo costi di procedura (prededuzioni):
  imponibile × 1.04 (contributo cassa) × 1.22 (IVA) = costo lordo
  Scheduling su 120 mesi.
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from app.db.models.mdm_prededuzione import MdmPrededuzioneMonthly
from app.services.assumptions import get_assumptions_or_default

# Aliquote standard
CONTRIBUTO_CASSA = Decimal("1.04")
ALIQUOTA_IVA = Decimal("1.22")


def compute_prededuzione(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Calcola le prededuzioni mensili a partire dalle assumptions.
    Pattern: delete-recompute-insert.
    """
    db.query(MdmPrededuzioneMonthly).filter(
        MdmPrededuzioneMonthly.case_id == case_id,
        MdmPrededuzioneMonthly.scenario_id == scenario_id,
    ).delete()

    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    sp = assumptions.spese_procedura
    piano = assumptions.piano

    # Voci di costo
    voci = [
        ("COMPENSO_CURATORE", "Compenso Curatore", Decimal(str(sp.compenso_curatore))),
        ("COMPENSO_ATTESTATORE", "Compenso Attestatore", Decimal(str(sp.compenso_attestatore))),
        ("COMPENSO_ADVISOR", "Compenso Advisor", Decimal(str(sp.compenso_advisor))),
        ("SPESE_GIUSTIZIA", "Spese di Giustizia", Decimal(str(sp.spese_giustizia))),
        ("ALTRE_SPESE", "Altre Spese", Decimal(str(sp.altre_spese))),
    ]

    # Fondo funzionamento
    ff = assumptions.fondo_funzionamento
    fondo_mensile = Decimal(str(ff.importo_mensile))
    fondo_durata = ff.durata_mesi

    count = 0
    duration = piano.duration_months

    for voce_type, voce_code, imponibile in voci:
        if imponibile <= 0:
            continue
        lordo = imponibile * CONTRIBUTO_CASSA * ALIQUOTA_IVA
        # Distribuisce equamente su tutti i mesi
        mensile = (lordo / duration).quantize(Decimal("0.01"))
        residuo = lordo

        for pi in range(duration):
            pagamento = min(mensile, residuo)
            residuo -= pagamento
            db.add(MdmPrededuzioneMonthly(
                case_id=case_id,
                scenario_id=scenario_id,
                voce_type=voce_type,
                voce_code=voce_code,
                importo_totale=lordo,
                period_index=pi,
                importo_periodo=pagamento,
                debito_residuo=max(residuo, Decimal(0)),
            ))
            count += 1

    # Fondo funzionamento: pagamento mensile per durata specificata
    if fondo_mensile > 0:
        totale_fondo = fondo_mensile * fondo_durata
        residuo = totale_fondo
        for pi in range(duration):
            if pi < fondo_durata:
                pagamento = fondo_mensile
            else:
                pagamento = Decimal(0)
            residuo -= pagamento
            db.add(MdmPrededuzioneMonthly(
                case_id=case_id,
                scenario_id=scenario_id,
                voce_type="FONDO_FUNZIONAMENTO",
                voce_code="Fondo Funzionamento",
                importo_totale=totale_fondo,
                period_index=pi,
                importo_periodo=pagamento,
                debito_residuo=max(residuo, Decimal(0)),
            ))
            count += 1

    db.commit()
    return count


def get_prededuzione(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmPrededuzioneMonthly]:
    return (
        db.query(MdmPrededuzioneMonthly)
        .filter(
            MdmPrededuzioneMonthly.case_id == case_id,
            MdmPrededuzioneMonthly.scenario_id == scenario_id,
        )
        .order_by(MdmPrededuzioneMonthly.voce_type, MdmPrededuzioneMonthly.period_index)
        .all()
    )
