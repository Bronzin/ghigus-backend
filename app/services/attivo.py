# app/services/attivo.py
"""Service per l'analisi dell'Attivo rettificato."""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict

from app.db.models.mdm_attivo import MdmAttivoItem
from app.db.models.final import SpRiclass

# ── Categorie dell'attivo (21 categorie standard) ───────────
ATTIVO_CATEGORIES = [
    "IMMOBILIZZAZIONI_IMMATERIALI",
    "IMMOBILIZZAZIONI_MATERIALI",
    "IMMOBILIZZAZIONI_FINANZIARIE",
    "RIMANENZE",
    "CREDITI_COMMERCIALI",
    "CREDITI_VS_CONTROLLATE",
    "CREDITI_VS_COLLEGATE",
    "CREDITI_VS_CONTROLLANTI",
    "CREDITI_TRIBUTARI",
    "CREDITI_IMPOSTE_ANTICIPATE",
    "CREDITI_VS_ALTRI",
    "ATTIVITA_FINANZIARIE",
    "DISPONIBILITA_LIQUIDE",
    "RATEI_RISCONTI_ATTIVI",
    "CASSA",
    "BANCA_CC",
    "TITOLI",
    "PARTECIPAZIONI",
    "AVVIAMENTO",
    "ALTRI_BENI_IMMATERIALI",
    "ALTRO_ATTIVO",
]

# Mapping riclass_code (senza prefisso SP_) -> attivo category
# Supporta sia codici flat (CREDITI, RIMANENZE) sia gerarchici (A1.1, A2.2)
_RICLASS_TO_CATEGORY: Dict[str, str] = {
    # Codici flat (dal maps_sp_ready.csv)
    "LIQUIDITA_E_ESIGIBILITA_IMMEDIATE": "DISPONIBILITA_LIQUIDE",
    "CREDITI": "CREDITI_COMMERCIALI",
    "RIMANENZE": "RIMANENZE",
    "RATEI_E_RISCONTI": "RATEI_RISCONTI_ATTIVI",
    "IMMOBILIZZAZIONI_IMMATERIALI": "IMMOBILIZZAZIONI_IMMATERIALI",
    "IMMOBILIZZAZIONI_MATERIALI": "IMMOBILIZZAZIONI_MATERIALI",
    "IMMOBILIZZAZIONI_FINANZIARIE": "IMMOBILIZZAZIONI_FINANZIARIE",
    "IMMOBILIZZAZIONI_LEASING": "IMMOBILIZZAZIONI_MATERIALI",
    "F_DO_AMM_TO_IMM_NI_IMMATERIALI": "IMMOBILIZZAZIONI_IMMATERIALI",
    "F_DO_AMM_TO_IMM_NI_MATERIALI": "IMMOBILIZZAZIONI_MATERIALI",
    # Codici gerarchici (legacy)
    "A1.1": "DISPONIBILITA_LIQUIDE",
    "A1.2": "CREDITI_COMMERCIALI",
    "A1.3": "RIMANENZE",
    "A1.4": "ATTIVITA_FINANZIARIE",
    "A1.5": "CREDITI_TRIBUTARI",
    "A1.6": "CREDITI_VS_ALTRI",
    "A1.7": "RATEI_RISCONTI_ATTIVI",
    "A2.1": "IMMOBILIZZAZIONI_IMMATERIALI",
    "A2.2": "IMMOBILIZZAZIONI_MATERIALI",
    "A2.3": "IMMOBILIZZAZIONI_FINANZIARIE",
    "A2.4": "PARTECIPAZIONI",
    "A2.5": "AVVIAMENTO",
}

# Codici riclass che rappresentano attivo (senza prefisso SP_)
_ATTIVO_CODES = set([
    "LIQUIDITA_E_ESIGIBILITA_IMMEDIATE", "CREDITI", "RIMANENZE",
    "RATEI_E_RISCONTI", "IMMOBILIZZAZIONI_IMMATERIALI", "IMMOBILIZZAZIONI_MATERIALI",
    "IMMOBILIZZAZIONI_FINANZIARIE", "IMMOBILIZZAZIONI_LEASING",
    "F_DO_AMM_TO_IMM_NI_IMMATERIALI", "F_DO_AMM_TO_IMM_NI_MATERIALI",
])


def _normalize_code(riclass_code: str) -> str:
    """Rimuove il prefisso SP_ se presente."""
    if riclass_code.startswith("SP_"):
        return riclass_code[3:]
    return riclass_code


def _is_attivo_code(riclass_code: str) -> bool:
    """Determina se un riclass_code è un attivo."""
    code = _normalize_code(riclass_code)
    return code in _ATTIVO_CODES or code.startswith("A")


def _map_riclass_to_category(riclass_code: str) -> str:
    """Mappa un riclass_code alla categoria attivo più specifica."""
    code = _normalize_code(riclass_code)
    # Lookup diretto
    if code in _RICLASS_TO_CATEGORY:
        return _RICLASS_TO_CATEGORY[code]
    # Prefix match (per codici gerarchici)
    for prefix, cat in sorted(_RICLASS_TO_CATEGORY.items(), key=lambda x: -len(x[0])):
        if code.startswith(prefix):
            return cat
    return "ALTRO_ATTIVO"


def seed_attivo_from_riclass(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Popola mdm_attivo_items dal SP riclassificato (fin_sp_riclass).
    Pattern: delete-recompute-insert.
    """
    db.query(MdmAttivoItem).filter(
        MdmAttivoItem.case_id == case_id,
        MdmAttivoItem.scenario_id == scenario_id,
    ).delete()

    riclass_rows = db.query(SpRiclass).filter(SpRiclass.case_id == case_id).all()

    count = 0
    for row in riclass_rows:
        if not _is_attivo_code(row.riclass_code):
            continue
        category = _map_riclass_to_category(row.riclass_code)
        item = MdmAttivoItem(
            case_id=case_id,
            scenario_id=scenario_id,
            category=category,
            item_label=row.riclass_desc or row.riclass_code,
            saldo_contabile=row.amount or Decimal(0),
        )
        _compute_attivo_item(item)
        db.add(item)
        count += 1

    db.commit()
    return count


def _compute_attivo_item(item: MdmAttivoItem) -> None:
    """Ricalcola i totali per un singolo item attivo."""
    saldo = item.saldo_contabile or Decimal(0)
    cessioni = item.cessioni or Decimal(0)
    compensazioni = item.compensazioni or Decimal(0)
    rett_eco = item.rettifiche_economiche or Decimal(0)
    rett_patr = item.rettifica_patrimoniale or Decimal(0)
    fondo = item.fondo_svalutazione or Decimal(0)

    item.totale_rettifiche = cessioni + compensazioni + rett_eco + rett_patr + fondo
    item.attivo_rettificato = saldo - item.totale_rettifiche

    if item.continuita_realizzo is None or item.continuita_realizzo == 0:
        item.continuita_realizzo = item.attivo_rettificato


def compute_attivo_totals(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """Ricalcola i totali per tutti gli item attivo di un caso."""
    items = db.query(MdmAttivoItem).filter(
        MdmAttivoItem.case_id == case_id,
        MdmAttivoItem.scenario_id == scenario_id,
    ).all()
    for item in items:
        _compute_attivo_item(item)
    db.commit()
    return len(items)


def upsert_attivo_item(db: Session, item_id: int, updates: dict) -> MdmAttivoItem:
    """Aggiorna un singolo item attivo e ricalcola i totali."""
    item = db.query(MdmAttivoItem).filter(MdmAttivoItem.id == item_id).first()
    if not item:
        raise ValueError(f"Attivo item {item_id} non trovato")
    for key, val in updates.items():
        if val is not None and hasattr(item, key):
            setattr(item, key, Decimal(str(val)))
    _compute_attivo_item(item)
    db.commit()
    return item


def get_attivo_items(db: Session, case_id: str, scenario_id: str = "base") -> List[MdmAttivoItem]:
    return (
        db.query(MdmAttivoItem)
        .filter(
            MdmAttivoItem.case_id == case_id,
            MdmAttivoItem.scenario_id == scenario_id,
        )
        .order_by(MdmAttivoItem.category, MdmAttivoItem.id)
        .all()
    )
