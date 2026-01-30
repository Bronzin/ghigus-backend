# app/services/passivo.py
"""Service per l'analisi del Passivo rettificato e tipologie creditore."""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict

from app.db.models.mdm_passivo import MdmPassivoItem, MdmPassivoTipologia
from app.db.models.mdm_attivo import MdmAttivoItem
from app.db.models.final import SpRiclass

# ── Categorie del passivo (15 categorie standard) ───────────
PASSIVO_CATEGORIES = [
    "DEBITI_VS_BANCHE_BREVE",
    "DEBITI_VS_BANCHE_LUNGO",
    "DEBITI_VS_FORNITORI",
    "DEBITI_TRIBUTARI",
    "DEBITI_VS_ISTITUTI_PREV",
    "DEBITI_VS_DIPENDENTI",
    "DEBITI_VS_CONTROLLATE",
    "DEBITI_VS_COLLEGATE",
    "DEBITI_VS_CONTROLLANTI",
    "ALTRI_DEBITI",
    "TFR",
    "FONDI_RISCHI",
    "RATEI_RISCONTI_PASSIVI",
    "PATRIMONIO_NETTO",
    "ALTRO_PASSIVO",
]

# Mapping riclass_code prefix -> passivo category
_RICLASS_TO_CATEGORY: Dict[str, str] = {
    "P1.1": "DEBITI_VS_BANCHE_BREVE",
    "P1.2": "DEBITI_VS_FORNITORI",
    "P1.3": "DEBITI_TRIBUTARI",
    "P1.4": "DEBITI_VS_ISTITUTI_PREV",
    "P1.5": "DEBITI_VS_DIPENDENTI",
    "P1.6": "ALTRI_DEBITI",
    "P1.7": "RATEI_RISCONTI_PASSIVI",
    "P2.1": "DEBITI_VS_BANCHE_LUNGO",
    "P2.2": "TFR",
    "P2.3": "FONDI_RISCHI",
    "PN":   "PATRIMONIO_NETTO",
}


def _map_riclass_to_category(riclass_code: str) -> str:
    for prefix, cat in sorted(_RICLASS_TO_CATEGORY.items(), key=lambda x: -len(x[0])):
        if riclass_code.startswith(prefix):
            return cat
    if riclass_code.startswith("P"):
        return "ALTRO_PASSIVO"
    return "ALTRO_PASSIVO"


def seed_passivo_from_riclass(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Popola mdm_passivo_items dal SP riclassificato (passivo + PN).
    Pattern: delete-recompute-insert.
    """
    db.query(MdmPassivoItem).filter(
        MdmPassivoItem.case_id == case_id,
        MdmPassivoItem.scenario_id == scenario_id,
    ).delete()

    riclass_rows = (
        db.query(SpRiclass)
        .filter(
            SpRiclass.case_id == case_id,
            (SpRiclass.riclass_code.startswith("P")) | (SpRiclass.riclass_code.startswith("PN")),
        )
        .all()
    )

    count = 0
    for row in riclass_rows:
        category = _map_riclass_to_category(row.riclass_code)
        item = MdmPassivoItem(
            case_id=case_id,
            scenario_id=scenario_id,
            category=category,
            item_label=row.riclass_desc or row.riclass_code,
            saldo_contabile=row.amount or Decimal(0),
        )
        _compute_passivo_item(item)
        db.add(item)
        count += 1

    db.commit()
    return count


def _compute_passivo_item(item: MdmPassivoItem) -> None:
    """Ricalcola i totali per un singolo item passivo."""
    saldo = item.saldo_contabile or Decimal(0)
    incrementi = item.incrementi or Decimal(0)
    decrementi = item.decrementi or Decimal(0)
    compensato = item.compensato or Decimal(0)
    fondo = item.fondo_rischi or Decimal(0)
    sanzioni = item.sanzioni_accessori or Decimal(0)
    interessi = item.interessi or Decimal(0)

    item.totale_rettifiche = incrementi - decrementi - compensato + fondo + sanzioni + interessi
    item.passivo_rettificato = saldo + item.totale_rettifiche


def apply_compensazioni_from_attivo(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Applica le compensazioni dall'attivo al passivo.
    Le cessioni/compensazioni dell'attivo riducono il passivo corrispondente.
    """
    attivo_items = db.query(MdmAttivoItem).filter(
        MdmAttivoItem.case_id == case_id,
        MdmAttivoItem.scenario_id == scenario_id,
    ).all()
    total_compensazioni = sum(
        (item.compensazioni or Decimal(0)) for item in attivo_items
    )

    # Distribuisce le compensazioni sui debiti del passivo
    passivo_items = (
        db.query(MdmPassivoItem)
        .filter(
            MdmPassivoItem.case_id == case_id,
            MdmPassivoItem.scenario_id == scenario_id,
            MdmPassivoItem.category != "PATRIMONIO_NETTO",
        )
        .all()
    )

    if not passivo_items or total_compensazioni == 0:
        return 0

    updated = 0
    remaining = total_compensazioni
    for item in passivo_items:
        if remaining <= 0:
            break
        saldo = item.saldo_contabile or Decimal(0)
        compensable = min(remaining, abs(saldo))
        item.compensato = (item.compensato or Decimal(0)) + compensable
        remaining -= compensable
        _compute_passivo_item(item)
        updated += 1

    db.commit()
    return updated


def compute_passivo_totals(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """Ricalcola i totali per tutti gli item passivo."""
    items = db.query(MdmPassivoItem).filter(
        MdmPassivoItem.case_id == case_id,
        MdmPassivoItem.scenario_id == scenario_id,
    ).all()
    for item in items:
        _compute_passivo_item(item)
    db.commit()
    return len(items)


def assign_tipologie(db: Session, case_id: str, scenario_id: str = "base", tipologie: List[dict] = None) -> int:
    """Salva le tipologie creditore (replace all)."""
    if tipologie is None:
        tipologie = []
    db.query(MdmPassivoTipologia).filter(
        MdmPassivoTipologia.case_id == case_id,
        MdmPassivoTipologia.scenario_id == scenario_id,
    ).delete()
    count = 0
    for t in tipologie:
        db.add(MdmPassivoTipologia(
            case_id=case_id,
            scenario_id=scenario_id,
            sezione=t["sezione"],
            slot_order=t["slot_order"],
            classe=t["classe"],
            specifica=t.get("specifica"),
            codice_ordinamento=t.get("codice_ordinamento"),
        ))
        count += 1
    db.commit()
    return count


def get_passivo_items(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmPassivoItem]:
    return (
        db.query(MdmPassivoItem)
        .filter(
            MdmPassivoItem.case_id == case_id,
            MdmPassivoItem.scenario_id == scenario_id,
        )
        .order_by(MdmPassivoItem.category, MdmPassivoItem.id)
        .all()
    )


def get_tipologie(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmPassivoTipologia]:
    return (
        db.query(MdmPassivoTipologia)
        .filter(
            MdmPassivoTipologia.case_id == case_id,
            MdmPassivoTipologia.scenario_id == scenario_id,
        )
        .order_by(MdmPassivoTipologia.sezione, MdmPassivoTipologia.slot_order)
        .all()
    )
