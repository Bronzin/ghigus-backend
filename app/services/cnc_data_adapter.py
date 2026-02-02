# app/services/cnc_data_adapter.py
"""
CNC Data Adapter — transforms DB models into list[list[str]] table format
for CNC PowerPoint slide generation.

Italian number formatting: dot for thousands, comma for decimals.
Each function returns list[list[str]] with header row + data rows.
"""

from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models.final import CeRiclass, SpRiclass
from app.db.models.mdm_attivo import MdmAttivoItem
from app.db.models.mdm_concordato import MdmConcordatoMonthly
from app.db.models.mdm_passivo import MdmPassivoItem, MdmPassivoTipologia
from app.db.models.mdm_projections import (
    MdmBancaProjection,
    MdmCeProjection,
    MdmCflowProjection,
    MdmSpProjection,
)
from app.db.models.mdm_affitto import MdmAffittoMonthly
from app.db.models.mdm_cessione import MdmCessioneMonthly
from app.db.models.mdm_prededuzione import MdmPrededuzioneMonthly
from app.services.pfn import compute_pfn_from_mdm

D = Decimal
ZERO = D(0)


# ---------------------------------------------------------------------------
# Number formatting helpers
# ---------------------------------------------------------------------------

def _fmt(value: Optional[Decimal], decimals: int = 0) -> str:
    """Format a Decimal to Italian string. None/zero → '-'."""
    if value is None:
        return ""
    v = D(str(value))
    if v == ZERO:
        return "-"
    if decimals == 0:
        formatted = f"{v:,.0f}"
    else:
        formatted = f"{v:,.{decimals}f}"
    # Convert from 1,234,567.89 → 1.234.567,89
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt2(value: Optional[Decimal]) -> str:
    """Format with 2 decimals."""
    return _fmt(value, decimals=2)


def _fmt_pct(value: Optional[Decimal]) -> str:
    """Format a percentage (0-100 scale, 2 decimals)."""
    if value is None:
        return ""
    v = D(str(value))
    if v == ZERO:
        return "-"
    formatted = f"{v:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".") + "%"


def _val(v: Optional[Decimal]) -> Decimal:
    """Coerce None to ZERO."""
    return D(str(v)) if v is not None else ZERO


# ---------------------------------------------------------------------------
# 1. get_analisi_economica
# ---------------------------------------------------------------------------

# CE line_codes of interest for the economic analysis table
_CE_LINES = [
    ("RICAVI", "Ricavi"),
    ("MATERIE_PRIME", "Materie prime e merci"),
    ("SERVIZI", "Servizi"),
    ("GODIMENTO_TERZI", "Godimento beni di terzi"),
    ("COSTI_PERSONALE", "Costi del personale"),
    ("ACCANTONAMENTO_TFR", "Accantonamento TFR"),
    ("ONERI_DIVERSI", "Oneri diversi di gestione"),
    ("TOT_COSTI_PROD", "Totale costi produzione"),
    ("EBITDA", "EBITDA"),
    ("TOT_AMMORTAMENTI", "Totale ammortamenti"),
    ("EBIT", "EBIT"),
    ("ONERI_FINANZIARI", "Oneri finanziari"),
    ("PROVENTI_FINANZIARI", "Proventi finanziari"),
    ("TOT_GEST_FIN", "Gestione finanziaria"),
    ("PROVENTI_STRAORD", "Proventi straordinari"),
    ("ONERI_STRAORD", "Oneri straordinari"),
    ("PREDEDUZIONI", "Prededuzioni"),
    ("EBT", "EBT"),
    ("TOT_IMPOSTE", "Totale imposte"),
    ("UTILE_NETTO", "Utile netto"),
]


def get_analisi_economica(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """CE riclass multi-year. Aggregates monthly CE projections into annual totals."""
    rows = db.query(MdmCeProjection).filter(
        MdmCeProjection.case_id == case_id,
        MdmCeProjection.scenario_id == scenario_id,
    ).all()

    if not rows:
        return [["Voce"]]

    # Aggregate by line_code and year (period_index // 12)
    data: Dict[str, Dict[int, Decimal]] = defaultdict(lambda: defaultdict(lambda: ZERO))
    years_set: set = set()
    for r in rows:
        year = r.period_index // 12 + 1  # Year 1, 2, ...
        years_set.add(year)
        data[r.line_code][year] += _val(r.amount)

    years = sorted(years_set)

    # Build header
    header = ["Voce"] + [f"Anno {y}" for y in years]
    table: List[List[str]] = [header]

    for code, label in _CE_LINES:
        row = [label]
        for y in years:
            row.append(_fmt(data[code][y]))
        table.append(row)

    return table


# ---------------------------------------------------------------------------
# 2. get_analisi_finanziaria
# ---------------------------------------------------------------------------

_CFLOW_LINES = [
    ("UTILE_NETTO", "Utile netto"),
    ("AMMORTAMENTI", "Ammortamenti"),
    ("DELTA_CREDITI", "Variazione crediti"),
    ("DELTA_RIMANENZE", "Variazione rimanenze"),
    ("DELTA_DEBITI_BREVE", "Variazione debiti a breve"),
    ("FLUSSO_GESTIONE_REDD", "Flusso gestione reddituale"),
    ("DELTA_IMMOBILIZZAZIONI", "Variazione immobilizzazioni"),
    ("FLUSSO_INVESTIMENTO", "Flusso investimento"),
    ("DELTA_DEBITI_ML", "Variazione debiti M/L"),
    ("DELTA_TFR", "Variazione TFR"),
    ("FLUSSO_FINANZIAMENTO", "Flusso finanziamento"),
    ("FLUSSO_NETTO", "Variazione liquidita'"),
]


def get_analisi_finanziaria(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Cash flow annual from MdmCflowProjection (aggregate 12-month periods)."""
    rows = db.query(MdmCflowProjection).filter(
        MdmCflowProjection.case_id == case_id,
        MdmCflowProjection.scenario_id == scenario_id,
    ).all()

    if not rows:
        return [["Voce"]]

    data: Dict[str, Dict[int, Decimal]] = defaultdict(lambda: defaultdict(lambda: ZERO))
    years_set: set = set()
    for r in rows:
        year = r.period_index // 12 + 1
        years_set.add(year)
        data[r.line_code][year] += _val(r.amount)

    years = sorted(years_set)
    header = ["Voce"] + [f"Anno {y}" for y in years]
    table: List[List[str]] = [header]

    for code, label in _CFLOW_LINES:
        row = [label]
        for y in years:
            row.append(_fmt(data[code][y]))
        table.append(row)

    return table


# ---------------------------------------------------------------------------
# 3. get_stato_patrimoniale
# ---------------------------------------------------------------------------

_SP_LINES = [
    ("CASSA", "Disponibilita' liquide"),
    ("CREDITI_COMM", "Crediti commerciali"),
    ("RIMANENZE", "Rimanenze"),
    ("RATEI_RISCONTI_A", "Ratei e risconti attivi"),
    ("TOT_ATTIVO_CORRENTE", "Totale attivo corrente"),
    ("IMMOB_IMMATERIALI", "Immobilizzazioni immateriali"),
    ("IMMOB_MATERIALI", "Immobilizzazioni materiali"),
    ("IMMOB_FINANZIARIE", "Immobilizzazioni finanziarie"),
    ("IMMOB_LEASING", "Immobilizzazioni in leasing"),
    ("TOT_ATTIVO_FISSO", "Totale attivo fisso"),
    ("TOTALE_ATTIVO", "TOTALE ATTIVO"),
    ("DEBITI_BREVE", "Debiti a breve termine"),
    ("TOT_PASSIVO_CORRENTE", "Totale passivo corrente"),
    ("DEBITI_LUNGO", "Debiti a medio/lungo termine"),
    ("TFR", "TFR"),
    ("TOT_PASSIVO_ML", "Totale passivo M/L"),
    ("CAPITALE", "Capitale sociale"),
    ("RISERVE", "Riserve"),
    ("UTILE_A_NUOVO", "Utile a nuovo"),
    ("UTILE_ESERCIZIO", "Utile d'esercizio"),
    ("PATRIMONIO_NETTO", "Patrimonio netto"),
    ("TOTALE_PASSIVO_PN", "TOTALE PASSIVO + PN"),
]


def get_stato_patrimoniale(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """SP riclass multi-year from MdmSpProjection (end-of-year snapshots)."""
    rows = db.query(MdmSpProjection).filter(
        MdmSpProjection.case_id == case_id,
        MdmSpProjection.scenario_id == scenario_id,
    ).all()

    if not rows:
        return [["Voce"]]

    # Take last month of each year as the year-end snapshot
    by_code_period: Dict[str, Dict[int, Decimal]] = defaultdict(dict)
    max_period: Dict[int, int] = {}  # year -> max period_index seen
    for r in rows:
        year = r.period_index // 12 + 1
        pi = r.period_index
        if year not in max_period or pi > max_period[year]:
            max_period[year] = pi
        by_code_period[r.line_code][(r.period_index)] = _val(r.amount)

    years = sorted(max_period.keys())

    header = ["Voce"] + [f"Anno {y}" for y in years]
    table: List[List[str]] = [header]

    for code, label in _SP_LINES:
        row = [label]
        for y in years:
            pi = max_period[y]
            val = by_code_period.get(code, {}).get(pi, ZERO)
            row.append(_fmt(val))
        table.append(row)

    return table


# ---------------------------------------------------------------------------
# 4. get_pfn_table
# ---------------------------------------------------------------------------

def get_pfn_table(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """PFN table from compute_pfn_from_mdm."""
    pfn = compute_pfn_from_mdm(db, case_id, scenario_id)

    header = ["Voce", "Importo"]
    table: List[List[str]] = [header]
    table.append(["Liquidita'", _fmt2(D(str(pfn["liquidita"])))])
    table.append(["Attivita' finanziarie", _fmt2(D(str(pfn["attivita_finanziarie"])))])
    table.append(["Debiti finanziari BT", _fmt2(D(str(pfn["debiti_finanziari_bt"])))])
    table.append(["Debiti finanziari MLT", _fmt2(D(str(pfn["debiti_finanziari_mlt"])))])
    table.append(["PFN", _fmt2(D(str(pfn["pfn"])))])
    table.append(["Interpretazione", pfn["interpretation"]])

    return table


# ---------------------------------------------------------------------------
# 5. get_rettifiche_attivo
# ---------------------------------------------------------------------------

def get_rettifiche_attivo(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Asset adjustments from MdmAttivoItem."""
    items = db.query(MdmAttivoItem).filter(
        MdmAttivoItem.case_id == case_id,
        MdmAttivoItem.scenario_id == scenario_id,
    ).order_by(MdmAttivoItem.category, MdmAttivoItem.id).all()

    header = [
        "Categoria", "Descrizione", "Saldo contabile",
        "Cessioni", "Compensazioni", "Rettifiche economiche",
        "Rettifica patrimoniale", "Fondo svalutazione",
        "Totale rettifiche", "Attivo rettificato",
    ]
    table: List[List[str]] = [header]

    if not items:
        return table

    for item in items:
        table.append([
            item.category or "",
            item.item_label or "",
            _fmt2(item.saldo_contabile),
            _fmt2(item.cessioni),
            _fmt2(item.compensazioni),
            _fmt2(item.rettifiche_economiche),
            _fmt2(item.rettifica_patrimoniale),
            _fmt2(item.fondo_svalutazione),
            _fmt2(item.totale_rettifiche),
            _fmt2(item.attivo_rettificato),
        ])

    # Totals row
    tot_saldo = sum(_val(i.saldo_contabile) for i in items)
    tot_rett = sum(_val(i.totale_rettifiche) for i in items)
    tot_att_rett = sum(_val(i.attivo_rettificato) for i in items)
    table.append([
        "TOTALE", "", _fmt2(tot_saldo),
        "", "", "", "", "",
        _fmt2(tot_rett), _fmt2(tot_att_rett),
    ])

    return table


# ---------------------------------------------------------------------------
# 6. get_rettifiche_passivo
# ---------------------------------------------------------------------------

def get_rettifiche_passivo(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Liability adjustments from MdmPassivoItem."""
    items = db.query(MdmPassivoItem).filter(
        MdmPassivoItem.case_id == case_id,
        MdmPassivoItem.scenario_id == scenario_id,
    ).order_by(MdmPassivoItem.category, MdmPassivoItem.id).all()

    header = [
        "Categoria", "Descrizione", "Saldo contabile",
        "Incrementi", "Decrementi", "Compensato",
        "Fondo rischi", "Sanzioni/accessori", "Interessi",
        "Totale rettifiche", "Passivo rettificato",
        "Tipologia creditore", "Classe creditore",
    ]
    table: List[List[str]] = [header]

    if not items:
        return table

    for item in items:
        table.append([
            item.category or "",
            item.item_label or "",
            _fmt2(item.saldo_contabile),
            _fmt2(item.incrementi),
            _fmt2(item.decrementi),
            _fmt2(item.compensato),
            _fmt2(item.fondo_rischi),
            _fmt2(item.sanzioni_accessori),
            _fmt2(item.interessi),
            _fmt2(item.totale_rettifiche),
            _fmt2(item.passivo_rettificato),
            item.tipologia_creditore or "",
            item.classe_creditore or "",
        ])

    # Totals row
    tot_saldo = sum(_val(i.saldo_contabile) for i in items)
    tot_rett = sum(_val(i.totale_rettifiche) for i in items)
    tot_pass_rett = sum(_val(i.passivo_rettificato) for i in items)
    table.append([
        "TOTALE", "", _fmt2(tot_saldo),
        "", "", "", "", "", "",
        _fmt2(tot_rett), _fmt2(tot_pass_rett), "", "",
    ])

    return table


# ---------------------------------------------------------------------------
# 7. get_flusso_anno1
# ---------------------------------------------------------------------------

_BANCA_LINES = [
    ("INCASSO_CLIENTI", "Incasso clienti"),
    ("INCASSO_AFFITTO", "Incasso affitto"),
    ("INCASSO_CESSIONE", "Incasso cessione"),
    ("EROGAZIONE_FIN", "Erogazione finanziamenti"),
    ("INCASSO_ATTIVO", "Incasso attivo"),
    ("DISINVESTIMENTI_FIN", "Disinvestimenti finanziari"),
    ("TOTALE_ENTRATE", "TOTALE ENTRATE"),
    ("PAG_FORNITORI", "Pagamento fornitori"),
    ("PAG_PERSONALE", "Pagamento personale"),
    ("PAG_ALTRI", "Pagamento altri"),
    ("PAG_PREDEDUZIONI", "Pagamento prededuzioni"),
    ("PAG_IMPOSTE", "Pagamento imposte"),
    ("PAG_IVA", "Pagamento IVA"),
    ("PAG_ONERI_FIN", "Pagamento oneri finanziari"),
    ("RATA_FINANZIAMENTI", "Rata finanziamenti"),
    ("RATA_TRIBUTARI", "Rata tributari"),
    ("INVESTIMENTI_FIN", "Investimenti finanziari"),
    ("TOTALE_USCITE", "TOTALE USCITE"),
    ("FLUSSO_NETTO", "Flusso netto"),
    ("SALDO_PROGRESSIVO", "Saldo progressivo"),
]


def get_flusso_anno1(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Monthly banca year 1 from MdmBancaProjection (period 0-11)."""
    rows = db.query(MdmBancaProjection).filter(
        MdmBancaProjection.case_id == case_id,
        MdmBancaProjection.scenario_id == scenario_id,
        MdmBancaProjection.period_index < 12,
    ).all()

    if not rows:
        return [["Voce"]]

    # Build lookup: line_code -> {period_index -> amount}
    data: Dict[str, Dict[int, Decimal]] = defaultdict(lambda: defaultdict(lambda: ZERO))
    for r in rows:
        data[r.line_code][r.period_index] = _val(r.amount)

    months = list(range(12))
    header = ["Voce"] + [f"Mese {m + 1}" for m in months]
    table: List[List[str]] = [header]

    for code, label in _BANCA_LINES:
        row = [label]
        for m in months:
            row.append(_fmt(data[code][m]))
        table.append(row)

    return table


# ---------------------------------------------------------------------------
# 8. get_soddisfacimento_creditori
# ---------------------------------------------------------------------------

def get_soddisfacimento_creditori(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Concordato monthly last-period snapshot per creditor class."""
    rows = db.query(MdmConcordatoMonthly).filter(
        MdmConcordatoMonthly.case_id == case_id,
        MdmConcordatoMonthly.scenario_id == scenario_id,
    ).all()

    header = [
        "Classe creditore", "Debito iniziale", "Pagamento proposto",
        "Pagamento cumulativo", "Debito residuo", "% Soddisfazione",
    ]
    table: List[List[str]] = [header]

    if not rows:
        return table

    # Find last period per class
    last_per_class: Dict[str, MdmConcordatoMonthly] = {}
    for r in rows:
        key = r.creditor_class
        if key not in last_per_class or r.period_index > last_per_class[key].period_index:
            last_per_class[key] = r

    # Ordered classes
    class_order = ["PREDEDUZIONE", "IPOTECARIO", "PRIVILEGIATO", "CHIROGRAFARIO"]
    for cls in class_order:
        if cls not in last_per_class:
            continue
        r = last_per_class[cls]
        table.append([
            cls,
            _fmt2(r.debito_iniziale),
            _fmt2(r.pagamento_proposto),
            _fmt2(r.pagamento_cumulativo),
            _fmt2(r.debito_residuo),
            _fmt_pct(r.pct_soddisfazione),
        ])

    return table


# ---------------------------------------------------------------------------
# 9. get_dati_sintesi
# ---------------------------------------------------------------------------

def get_dati_sintesi(
    db: Session, case_id: str, scenario_id: str = "base"
) -> Dict[str, str]:
    """Summary dict with key metrics."""
    # Totale attivo rettificato
    attivo_items = db.query(MdmAttivoItem).filter(
        MdmAttivoItem.case_id == case_id,
        MdmAttivoItem.scenario_id == scenario_id,
    ).all()
    totale_attivo = sum(_val(i.attivo_rettificato) for i in attivo_items)

    # Totale passivo rettificato
    passivo_items = db.query(MdmPassivoItem).filter(
        MdmPassivoItem.case_id == case_id,
        MdmPassivoItem.scenario_id == scenario_id,
    ).all()
    totale_passivo = sum(_val(i.passivo_rettificato) for i in passivo_items)

    # Pct soddisfazione medio from concordato
    concordato = db.query(MdmConcordatoMonthly).filter(
        MdmConcordatoMonthly.case_id == case_id,
        MdmConcordatoMonthly.scenario_id == scenario_id,
    ).all()

    # Last period per class for average satisfaction
    last_per_class: Dict[str, MdmConcordatoMonthly] = {}
    max_period = 0
    for r in concordato:
        key = r.creditor_class
        if key not in last_per_class or r.period_index > last_per_class[key].period_index:
            last_per_class[key] = r
        if r.period_index > max_period:
            max_period = r.period_index

    if last_per_class:
        pct_vals = [_val(v.pct_soddisfazione) for v in last_per_class.values() if v.pct_soddisfazione]
        pct_medio = sum(pct_vals) / len(pct_vals) if pct_vals else ZERO
    else:
        pct_medio = ZERO

    durata_mesi = max_period + 1 if concordato else 0

    # Anno analisi: from CeRiclass periods
    ce_periods = db.query(CeRiclass.period).filter(
        CeRiclass.case_id == case_id,
    ).distinct().all()
    anni = sorted([p[0] for p in ce_periods if p[0]])
    anno_analisi = anni[-1] if anni else ""

    return {
        "totale_attivo_rettificato": _fmt2(totale_attivo),
        "totale_passivo": _fmt2(totale_passivo),
        "pct_soddisfazione_medio": _fmt_pct(pct_medio),
        "durata_piano_mesi": str(durata_mesi),
        "anno_analisi": anno_analisi,
    }


# ---------------------------------------------------------------------------
# 10. get_creditori_non_aderenti
# ---------------------------------------------------------------------------

def get_creditori_non_aderenti(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Non-adhering creditors from MdmPassivoTipologia (sezione=NON_ADERENTE)."""
    items = db.query(MdmPassivoTipologia).filter(
        MdmPassivoTipologia.case_id == case_id,
        MdmPassivoTipologia.scenario_id == scenario_id,
        MdmPassivoTipologia.sezione == "NON_ADERENTE",
    ).order_by(MdmPassivoTipologia.slot_order).all()

    header = ["#", "Classe", "Specifica", "Codice ordinamento"]
    table: List[List[str]] = [header]

    for item in items:
        table.append([
            str(item.slot_order),
            item.classe or "",
            item.specifica or "",
            item.codice_ordinamento or "",
        ])

    return table


# ---------------------------------------------------------------------------
# 11. get_creditori_aderenti
# ---------------------------------------------------------------------------

def get_creditori_aderenti(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Adhering creditors from MdmPassivoTipologia (sezione=ADERENTE)."""
    items = db.query(MdmPassivoTipologia).filter(
        MdmPassivoTipologia.case_id == case_id,
        MdmPassivoTipologia.scenario_id == scenario_id,
        MdmPassivoTipologia.sezione == "ADERENTE",
    ).order_by(MdmPassivoTipologia.slot_order).all()

    header = ["#", "Classe", "Specifica", "Codice ordinamento"]
    table: List[List[str]] = [header]

    for item in items:
        table.append([
            str(item.slot_order),
            item.classe or "",
            item.specifica or "",
            item.codice_ordinamento or "",
        ])

    return table


# ---------------------------------------------------------------------------
# 12. get_affitto_table
# ---------------------------------------------------------------------------

def get_affitto_table(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Monthly rental schedule from MdmAffittoMonthly."""
    rows = db.query(MdmAffittoMonthly).filter(
        MdmAffittoMonthly.case_id == case_id,
        MdmAffittoMonthly.scenario_id == scenario_id,
    ).order_by(MdmAffittoMonthly.period_index).all()

    header = ["Mese", "Canone", "IVA", "Totale", "Incasso"]
    table: List[List[str]] = [header]

    if not rows:
        return table

    for r in rows:
        table.append([
            str(r.period_index + 1),
            _fmt2(r.canone),
            _fmt2(r.iva),
            _fmt2(r.totale),
            _fmt2(r.incasso),
        ])

    return table


# ---------------------------------------------------------------------------
# 13. get_cessione_table
# ---------------------------------------------------------------------------

def get_cessione_table(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Monthly business sale schedule from MdmCessioneMonthly."""
    rows = db.query(MdmCessioneMonthly).filter(
        MdmCessioneMonthly.case_id == case_id,
        MdmCessioneMonthly.scenario_id == scenario_id,
    ).order_by(MdmCessioneMonthly.period_index, MdmCessioneMonthly.component).all()

    header = ["Mese", "Componente", "Importo"]
    table: List[List[str]] = [header]

    if not rows:
        return table

    for r in rows:
        table.append([
            str(r.period_index + 1),
            r.component or "",
            _fmt2(r.amount),
        ])

    return table


# ---------------------------------------------------------------------------
# 14. get_prededuzioni_table
# ---------------------------------------------------------------------------

def get_prededuzioni_table(
    db: Session, case_id: str, scenario_id: str = "base"
) -> List[List[str]]:
    """Monthly pre-deduction payments from MdmPrededuzioneMonthly."""
    rows = db.query(MdmPrededuzioneMonthly).filter(
        MdmPrededuzioneMonthly.case_id == case_id,
        MdmPrededuzioneMonthly.scenario_id == scenario_id,
    ).order_by(MdmPrededuzioneMonthly.voce_type, MdmPrededuzioneMonthly.period_index).all()

    header = ["Voce", "Mese", "Importo totale", "Importo periodo", "Debito residuo"]
    table: List[List[str]] = [header]

    if not rows:
        return table

    for r in rows:
        table.append([
            r.voce_type or "",
            str(r.period_index + 1),
            _fmt2(r.importo_totale),
            _fmt2(r.importo_periodo),
            _fmt2(r.debito_residuo),
        ])

    return table
