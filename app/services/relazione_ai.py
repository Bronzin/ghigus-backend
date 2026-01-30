# app/services/relazione_ai.py
"""
Genera 7 tabelle strutturate per la generazione report AI
sulla relazione del commissario / attestatore.
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict, Any

from app.db.models.mdm_attivo import MdmAttivoItem
from app.db.models.mdm_passivo import MdmPassivoItem
from app.db.models.mdm_liquidazione import MdmLiquidazione, MdmTestPiat
from app.db.models.mdm_concordato import MdmConcordatoMonthly
from app.db.models.mdm_projections import MdmCeProjection, MdmBancaProjection
from app.services.assumptions import get_assumptions_or_default

D = Decimal
ZERO = D(0)


def _table(title: str, headers: List[str], rows: List[List[Any]]) -> dict:
    return {"title": title, "headers": headers, "rows": rows}


def get_relazione_ai(db: Session, case_id: str, scenario_id: str = "base") -> dict:
    """Genera le 7 tabelle strutturate per la relazione AI."""
    tables = []

    # ── 1. ANALISI ATTIVO ──
    attivo_items = (
        db.query(MdmAttivoItem)
        .filter(MdmAttivoItem.case_id == case_id, MdmAttivoItem.scenario_id == scenario_id)
        .order_by(MdmAttivoItem.category)
        .all()
    )
    rows_attivo = []
    for item in attivo_items:
        rows_attivo.append([
            item.category,
            item.item_label or "",
            float(item.saldo_contabile or 0),
            float(item.totale_rettifiche or 0),
            float(item.attivo_rettificato or 0),
            float(item.continuita_realizzo or 0),
        ])
    tables.append(_table(
        "Analisi Attivo Rettificato",
        ["Categoria", "Voce", "Saldo Contabile", "Totale Rettifiche", "Attivo Rettificato", "Continuità Realizzo"],
        rows_attivo,
    ))

    # ── 2. ANALISI PASSIVO ──
    passivo_items = (
        db.query(MdmPassivoItem)
        .filter(MdmPassivoItem.case_id == case_id, MdmPassivoItem.scenario_id == scenario_id)
        .order_by(MdmPassivoItem.category)
        .all()
    )
    rows_passivo = []
    for item in passivo_items:
        rows_passivo.append([
            item.category,
            item.item_label or "",
            float(item.saldo_contabile or 0),
            float(item.totale_rettifiche or 0),
            float(item.passivo_rettificato or 0),
            item.tipologia_creditore or "",
        ])
    tables.append(_table(
        "Analisi Passivo Rettificato",
        ["Categoria", "Voce", "Saldo Contabile", "Totale Rettifiche", "Passivo Rettificato", "Tipologia Creditore"],
        rows_passivo,
    ))

    # ── 3. LIQUIDAZIONE GIUDIZIALE ──
    liq_items = (
        db.query(MdmLiquidazione)
        .filter(MdmLiquidazione.case_id == case_id, MdmLiquidazione.scenario_id == scenario_id)
        .order_by(MdmLiquidazione.id)
        .all()
    )
    rows_liq = []
    for item in liq_items:
        rows_liq.append([
            item.section,
            item.line_label or item.line_code,
            float(item.importo_totale or 0),
            float(item.importo_massa_1 or 0),
            float(item.pct_soddisfazione or 0),
            float(item.credito_residuo or 0),
        ])
    tables.append(_table(
        "Liquidazione Giudiziale",
        ["Sezione", "Voce", "Importo Totale", "Pagato", "% Soddisfazione", "Credito Residuo"],
        rows_liq,
    ))

    # ── 4. TEST PERSEGUIBILITA ──
    piat_items = (
        db.query(MdmTestPiat)
        .filter(MdmTestPiat.case_id == case_id, MdmTestPiat.scenario_id == scenario_id)
        .order_by(MdmTestPiat.section, MdmTestPiat.id)
        .all()
    )
    rows_piat = []
    for item in piat_items:
        rows_piat.append([
            item.section,
            item.line_label or item.line_code,
            float(item.amount or 0),
        ])
    if piat_items:
        first = piat_items[0]
        rows_piat.append(["RISULTATO", "Totale A", float(first.total_a or 0)])
        rows_piat.append(["RISULTATO", "Totale B", float(first.total_b or 0)])
        rows_piat.append(["RISULTATO", "Rapporto A/B", float(first.ratio_ab or 0)])
        rows_piat.append(["RISULTATO", first.interpretation or "", 0])
    tables.append(_table(
        "Test di Perseguibilità (PIAT)",
        ["Sezione", "Voce", "Importo"],
        rows_piat,
    ))

    # ── 5. CE SINTETICO (annualizzato, primi 5 anni) ──
    ce_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmCeProjection).filter(
        MdmCeProjection.case_id == case_id, MdmCeProjection.scenario_id == scenario_id
    ).all():
        ce_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    key_lines_ce = ["RICAVI", "EBITDA", "EBIT", "EBT", "UTILE_NETTO"]
    rows_ce = []
    for code in key_lines_ce:
        row_data = [code]
        for year in range(5):
            total = sum(
                ce_map.get(year * 12 + m, {}).get(code, ZERO)
                for m in range(12)
            )
            row_data.append(float(total))
        rows_ce.append(row_data)

    tables.append(_table(
        "Conto Economico Sintetico (5 Anni)",
        ["Voce", "Anno 1", "Anno 2", "Anno 3", "Anno 4", "Anno 5"],
        rows_ce,
    ))

    # ── 6. CASH FLOW SINTETICO ──
    banca_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmBancaProjection).filter(
        MdmBancaProjection.case_id == case_id, MdmBancaProjection.scenario_id == scenario_id
    ).all():
        banca_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    key_lines_banca = ["TOTALE_ENTRATE", "TOTALE_USCITE", "FLUSSO_NETTO"]
    rows_banca = []
    for code in key_lines_banca:
        row_data = [code]
        for year in range(5):
            total = sum(
                banca_map.get(year * 12 + m, {}).get(code, ZERO)
                for m in range(12)
            )
            row_data.append(float(total))
        rows_banca.append(row_data)

    tables.append(_table(
        "Cash Flow Sintetico (5 Anni)",
        ["Voce", "Anno 1", "Anno 2", "Anno 3", "Anno 4", "Anno 5"],
        rows_banca,
    ))

    # ── 7. SODDISFAZIONE CREDITORI ──
    conc_items = (
        db.query(MdmConcordatoMonthly)
        .filter(MdmConcordatoMonthly.case_id == case_id, MdmConcordatoMonthly.scenario_id == scenario_id)
        .order_by(MdmConcordatoMonthly.period_index.desc(), MdmConcordatoMonthly.id)
        .all()
    )
    # Prendi l'ultimo periodo per ogni classe
    last_by_class: Dict[str, Any] = {}
    for item in conc_items:
        if item.creditor_class not in last_by_class:
            last_by_class[item.creditor_class] = item

    rows_conc = []
    for classe in ["PREDEDUZIONE", "IPOTECARIO", "PRIVILEGIATO", "CHIROGRAFARIO"]:
        item = last_by_class.get(classe)
        if item:
            rows_conc.append([
                classe,
                float(item.pagamento_proposto or 0),
                float(item.pagamento_cumulativo or 0),
                float(item.debito_residuo or 0),
                float(item.pct_soddisfazione or 0),
            ])
        else:
            rows_conc.append([classe, 0, 0, 0, 0])

    tables.append(_table(
        "Soddisfazione Creditori (Fine Piano)",
        ["Classe Creditore", "Pagamento Proposto", "Pagamento Cumulativo", "Debito Residuo", "% Soddisfazione"],
        rows_conc,
    ))

    return {"case_id": case_id, "scenario_id": scenario_id, "tables": tables}
