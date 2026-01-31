# app/services/pfn.py
"""Posizione Finanziaria Netta (PFN / Net Financial Position)."""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict, Optional

from app.db.models.final import SpRiclass
from app.db.models.mdm_attivo import MdmAttivoItem
from app.db.models.mdm_passivo import MdmPassivoItem
from app.db.models.mdm_projections import MdmSpProjection

D = Decimal
ZERO = D(0)

# Categorie attivo finanziario (riducono la PFN)
_ATTIVO_FIN_CATEGORIES = {
    "DISPONIBILITA_LIQUIDE", "CASSA", "BANCA_CC",
    "ATTIVITA_FINANZIARIE", "TITOLI",
}

# Categorie passivo finanziario (aumentano la PFN)
_PASSIVO_FIN_BT_CATEGORIES = {"DEBITI_VS_BANCHE_BREVE"}
_PASSIVO_FIN_MLT_CATEGORIES = {"DEBITI_VS_BANCHE_LUNGO"}


def compute_pfn_from_mdm(db: Session, case_id: str, scenario_id: str = "base") -> Dict:
    """
    Calcola la PFN dal dato MDM rettificato (attivo/passivo).

    PFN = Debiti finanziari BT + Debiti finanziari MLT - Liquidita' - Attivita' finanziarie
    PFN positiva = indebitamento netto, negativa = posizione finanziaria positiva.
    """
    attivo_items = db.query(MdmAttivoItem).filter(
        MdmAttivoItem.case_id == case_id,
        MdmAttivoItem.scenario_id == scenario_id,
    ).all()

    passivo_items = db.query(MdmPassivoItem).filter(
        MdmPassivoItem.case_id == case_id,
        MdmPassivoItem.scenario_id == scenario_id,
    ).all()

    liquidita = sum(
        (i.attivo_rettificato or ZERO)
        for i in attivo_items
        if i.category in _ATTIVO_FIN_CATEGORIES
    )

    debiti_fin_bt = sum(
        abs(i.passivo_rettificato or ZERO)
        for i in passivo_items
        if i.category in _PASSIVO_FIN_BT_CATEGORIES
    )

    debiti_fin_mlt = sum(
        abs(i.passivo_rettificato or ZERO)
        for i in passivo_items
        if i.category in _PASSIVO_FIN_MLT_CATEGORIES
    )

    pfn = debiti_fin_bt + debiti_fin_mlt - liquidita

    return {
        "liquidita": float(liquidita),
        "attivita_finanziarie": 0.0,  # TODO: attivita' finanziarie separate
        "debiti_finanziari_bt": float(debiti_fin_bt),
        "debiti_finanziari_mlt": float(debiti_fin_mlt),
        "pfn": float(pfn),
        "interpretation": _interpret_pfn(pfn, liquidita, debiti_fin_bt + debiti_fin_mlt),
    }


def compute_pfn_from_projections(db: Session, case_id: str, scenario_id: str = "base") -> list:
    """
    Calcola PFN per ogni periodo dalle proiezioni SP.
    Ritorna lista di {period_index, debiti_bt, debiti_mlt, cassa, pfn}.
    """
    sp_rows = db.query(MdmSpProjection).filter(
        MdmSpProjection.case_id == case_id,
        MdmSpProjection.scenario_id == scenario_id,
    ).all()

    by_period: Dict[int, Dict[str, D]] = {}
    for r in sp_rows:
        pi = r.period_index
        if pi not in by_period:
            by_period[pi] = {}
        by_period[pi][r.line_code] = r.amount or ZERO

    result = []
    for pi in sorted(by_period.keys()):
        data = by_period[pi]
        cassa = data.get("CASSA", ZERO)
        debiti_bt = abs(data.get("DEBITI_BREVE", ZERO))
        debiti_mlt = abs(data.get("DEBITI_LUNGO", ZERO))
        pfn = debiti_bt + debiti_mlt - cassa

        result.append({
            "period_index": pi,
            "cassa": float(cassa),
            "debiti_finanziari_bt": float(debiti_bt),
            "debiti_finanziari_mlt": float(debiti_mlt),
            "pfn": float(pfn),
        })

    return result


def _interpret_pfn(pfn: D, liquidita: D, debiti: D) -> str:
    if pfn <= ZERO:
        return "POSIZIONE FINANZIARIA NETTA POSITIVA - L'azienda ha piu' liquidita' che debiti finanziari"
    ratio = float(pfn / liquidita) if liquidita > ZERO else float("inf")
    if ratio < 1:
        return "INDEBITAMENTO MODERATO - PFN inferiore alla liquidita' disponibile"
    elif ratio < 3:
        return "INDEBITAMENTO SIGNIFICATIVO - PFN superiore alla liquidita'"
    else:
        return "INDEBITAMENTO ELEVATO - PFN molto superiore alla liquidita' disponibile"
