# app/services/confronto.py
"""Confronto Liquidazione vs Concordato per classe creditore."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import List, Dict

from app.db.models.mdm_liquidazione import MdmLiquidazione
from app.db.models.mdm_concordato import MdmConcordatoMonthly

D = Decimal
ZERO = D(0)

# Mapping delle classi creditore
CREDITOR_CLASSES = ["PREDEDUZIONE", "IPOTECARIO", "PRIVILEGIATO", "CHIROGRAFARIO"]


def compute_confronto(db: Session, case_id: str, scenario_id: str = "base") -> Dict:
    """
    Per ogni classe creditore:
    - debito_totale
    - soddisfazione_liquidazione (importo + %)
    - soddisfazione_concordato (importo + %)
    - delta (concordato - liquidazione)
    - concordato_migliore: bool
    """

    # ── Liquidazione: legge righe DISTRIBUZIONE_* per ogni classe ──
    liq_rows = (
        db.query(MdmLiquidazione)
        .filter(
            MdmLiquidazione.case_id == case_id,
            MdmLiquidazione.scenario_id == scenario_id,
            MdmLiquidazione.line_code.like("DISTRIBUZIONE_%"),
        )
        .all()
    )
    liq_by_class: Dict[str, Dict] = {}
    for r in liq_rows:
        # Extract class from line_code: DISTRIBUZIONE_PREDEDUZIONE → PREDEDUZIONE
        classe = r.line_code.replace("DISTRIBUZIONE_", "")
        if classe in CREDITOR_CLASSES:
            liq_by_class[classe] = {
                "importo": float(r.importo_totale or 0),
                "pct": float(r.pct_soddisfazione or 0),
            }

    # Debito totale per classe dalla liquidazione (righe CREDITO_*)
    credito_rows = (
        db.query(MdmLiquidazione)
        .filter(
            MdmLiquidazione.case_id == case_id,
            MdmLiquidazione.scenario_id == scenario_id,
            MdmLiquidazione.line_code.like("CREDITO_%"),
        )
        .all()
    )
    debito_by_class: Dict[str, float] = {}
    for r in credito_rows:
        classe = r.line_code.replace("CREDITO_", "")
        if classe in CREDITOR_CLASSES:
            debito_by_class[classe] = float(r.importo_totale or 0)

    # ── Concordato: aggregare pagamento_cumulativo max per classe ──
    # L'ultimo periodo per ogni classe ha il pagamento_cumulativo finale
    conc_agg = (
        db.query(
            MdmConcordatoMonthly.creditor_class,
            func.max(MdmConcordatoMonthly.pagamento_cumulativo).label("tot_pagato"),
        )
        .filter(
            MdmConcordatoMonthly.case_id == case_id,
            MdmConcordatoMonthly.scenario_id == scenario_id,
        )
        .group_by(MdmConcordatoMonthly.creditor_class)
        .all()
    )
    conc_by_class: Dict[str, float] = {}
    for row in conc_agg:
        conc_by_class[row.creditor_class] = float(row.tot_pagato or 0)

    # ── Build confronto rows ──
    classi = []
    all_concordato_better = True
    any_concordato_better = False

    for classe in CREDITOR_CLASSES:
        debito = debito_by_class.get(classe, 0.0)
        liq_info = liq_by_class.get(classe, {"importo": 0.0, "pct": 0.0})
        conc_importo = conc_by_class.get(classe, 0.0)
        conc_pct = (conc_importo / debito * 100) if debito > 0 else 0.0

        delta_importo = conc_importo - liq_info["importo"]
        delta_pct = conc_pct - liq_info["pct"]
        concordato_migliore = conc_importo >= liq_info["importo"]

        if debito > 0:
            if not concordato_migliore:
                all_concordato_better = False
            else:
                any_concordato_better = True

        classi.append({
            "creditor_class": classe,
            "debito_totale": debito,
            "soddisfazione_liq_importo": liq_info["importo"],
            "soddisfazione_liq_pct": liq_info["pct"],
            "soddisfazione_conc_importo": conc_importo,
            "soddisfazione_conc_pct": round(conc_pct, 2),
            "delta_importo": round(delta_importo, 2),
            "delta_pct": round(delta_pct, 2),
            "concordato_migliore": concordato_migliore,
        })

    if all_concordato_better and any_concordato_better:
        esito = "CONCORDATO_CONVENIENTE"
    elif not any_concordato_better:
        esito = "LIQUIDAZIONE_CONVENIENTE"
    else:
        esito = "PARI"

    return {
        "case_id": case_id,
        "scenario_id": scenario_id,
        "classi": classi,
        "esito": esito,
    }
