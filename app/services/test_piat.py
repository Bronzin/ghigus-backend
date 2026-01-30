# app/services/test_piat.py
"""
Test di perseguibilità (PIAT): rapporto A/B con soglie interpretative.
  A = risorse disponibili per i creditori nel piano concordatario
  B = risorse disponibili nella liquidazione giudiziale
  Se A/B > 1 → il concordato è più conveniente della liquidazione
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Tuple

from app.db.models.mdm_liquidazione import MdmLiquidazione, MdmTestPiat
from app.db.models.mdm_attivo import MdmAttivoItem
from app.db.models.mdm_passivo import MdmPassivoItem


def _interpret_ratio(ratio: Decimal) -> str:
    """Interpreta il rapporto A/B."""
    if ratio >= Decimal("1.2"):
        return "CONCORDATO NETTAMENTE PREFERIBILE - Il piano offre soddisfazione significativamente superiore alla liquidazione"
    elif ratio >= Decimal("1.0"):
        return "CONCORDATO PREFERIBILE - Il piano offre soddisfazione superiore alla liquidazione"
    elif ratio >= Decimal("0.8"):
        return "MARGINALE - Il piano offre soddisfazione leggermente inferiore alla liquidazione"
    else:
        return "LIQUIDAZIONE PREFERIBILE - La liquidazione offre soddisfazione superiore al piano"


def compute_test_piat(db: Session, case_id: str, scenario_id: str = "base") -> dict:
    """
    Calcola il test di perseguibilità A/B.
    Pattern: delete-recompute-insert.
    """
    db.query(MdmTestPiat).filter(
        MdmTestPiat.case_id == case_id,
        MdmTestPiat.scenario_id == scenario_id,
    ).delete()

    # ── Sezione A: risorse del concordato ──
    # Attivo continuità realizzo
    attivo_items = db.query(MdmAttivoItem).filter(
        MdmAttivoItem.case_id == case_id,
        MdmAttivoItem.scenario_id == scenario_id,
    ).all()
    continuita = sum((i.continuita_realizzo or Decimal(0)) for i in attivo_items)

    a_lines: List[Tuple[str, str, int, Decimal]] = [
        ("A_CONTINUITA", "Realizzo in continuità", 1, continuita),
    ]

    total_a = sum(sign * amount for _, _, sign, amount in a_lines)

    for code, label, sign, amount in a_lines:
        db.add(MdmTestPiat(
            case_id=case_id,
            scenario_id=scenario_id,
            section="A",
            line_code=code,
            line_label=label,
            sign=sign,
            amount=amount,
            total_a=total_a,
        ))

    # ── Sezione B: risorse della liquidazione (realizzo netto) ──
    liq_netto = (
        db.query(MdmLiquidazione)
        .filter(
            MdmLiquidazione.case_id == case_id,
            MdmLiquidazione.scenario_id == scenario_id,
            MdmLiquidazione.line_code == "REALIZZO_NETTO",
        )
        .first()
    )
    realizzo_liq = (liq_netto.importo_totale or Decimal(0)) if liq_netto else Decimal(0)

    b_lines: List[Tuple[str, str, int, Decimal]] = [
        ("B_REALIZZO_LIQ", "Realizzo in liquidazione", 1, realizzo_liq),
    ]

    total_b = sum(sign * amount for _, _, sign, amount in b_lines)

    for code, label, sign, amount in b_lines:
        db.add(MdmTestPiat(
            case_id=case_id,
            scenario_id=scenario_id,
            section="B",
            line_code=code,
            line_label=label,
            sign=sign,
            amount=amount,
            total_b=total_b,
        ))

    # ── Calcolo rapporto ──
    ratio = (total_a / total_b) if total_b > 0 else Decimal(0)
    interpretation = _interpret_ratio(ratio)

    # Aggiorna tutte le righe con i totali finali
    all_rows = db.query(MdmTestPiat).filter(
        MdmTestPiat.case_id == case_id,
        MdmTestPiat.scenario_id == scenario_id,
    ).all()
    for row in all_rows:
        row.total_a = total_a
        row.total_b = total_b
        row.ratio_ab = ratio
        row.interpretation = interpretation

    db.commit()
    return {
        "total_a": float(total_a),
        "total_b": float(total_b),
        "ratio_ab": float(ratio),
        "interpretation": interpretation,
    }


def get_test_piat(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmTestPiat]:
    return (
        db.query(MdmTestPiat)
        .filter(
            MdmTestPiat.case_id == case_id,
            MdmTestPiat.scenario_id == scenario_id,
        )
        .order_by(MdmTestPiat.section, MdmTestPiat.id)
        .all()
    )
