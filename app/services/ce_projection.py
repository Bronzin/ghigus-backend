# app/services/ce_projection.py
"""
Motore proiezione Conto Economico dettagliato.

Struttura CE (conforme al foglio CE-mese dell'Excel MDM, ~40 righe output):
  A) VALORE DELLA PRODUZIONE
     - Ricavi delle vendite
     - Variazione rimanenze PF
     - Variazione rimanenze MP
     - Capitalizzazione costi
     → Totale valore della produzione
  B) COSTI DELLA PRODUZIONE
     - Materie prime e merci
     - Servizi
     - Godimento beni di terzi
     - Costi del personale
     - Ammortamenti immateriali
     - Ammortamenti materiali
     - Accantonamenti
     - Oneri diversi di gestione
     - Canone affitto d'azienda (da assumptions)
     → Totale costi della produzione
  DIFFERENZA A-B (Reddito operativo / EBIT)
  C) PROVENTI E ONERI FINANZIARI
     - Proventi finanziari
     - Oneri finanziari
     → Totale gestione finanziaria
  D) PROVENTI E ONERI STRAORDINARI
     - Proventi straordinari
     - Oneri straordinari
     - Costi prededuzione (da pipeline)
     → Totale gestione straordinaria
  RISULTATO PRIMA DELLE IMPOSTE (EBT)
  E) IMPOSTE
     - IRES
     - IRAP
     → Totale imposte
  UTILE (PERDITA) DELL'ESERCIZIO

Ogni voce può avere:
  - growth_rates annui (%) dalle assumptions (CeDrivers)
  - seasonality mensile (12 coefficienti) dalle assumptions
  - base annua dal CE riclassificato (fin_ce_riclass)

I codici riclass letti dal DB sono quelli reali del maps_ce_ready.csv:
  RICAVI, RIMANENZE_PF, RIMANENZE_MP, CAPITALIZZAZIONE_COSTI,
  MATERIE_PRIME_E_MERCI, SERVIZI, GODIMENTO_BENI_TERZI,
  ONERI_DIVERSI_DI_GESTIONE, COSTI_PERSONALE,
  AMMORTAMENTI_IMMATERIALI, AMMORTAMENTI_MATERIALI, ACCANTONAMENTI,
  PROVENTI_STRAORDINARI, ONERI_STRAORDINARI,
  PROVENTI_FINANZIARI, ONERI_FINANZIARI, IMPOSTE
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict, Optional

from app.db.models.mdm_projections import MdmCeProjection
from app.db.models.final import CeRiclass, SpRiclass
from app.services.assumptions import get_assumptions_or_default
from app.services.prededuzione import get_prededuzione
from app.services.affitto import get_affitto
from app.schemas.assumptions import CeLineDriver

D = Decimal
ZERO = D(0)

# Tipo per override oneri finanziari (period_index → importo assoluto interesse)
InterestOverride = Optional[Dict[int, D]]

# ── Struttura delle righe CE ────────────────────────────────
# Ogni entry: (line_code, line_label, section, riclass_codes, sign, is_subtotal)
# riclass_codes: lista di codici riclass da sommare dal DB per ottenere la base annua.
#   Se vuoto, il valore viene calcolato (subtotal) o alimentato da altra fonte.
# sign: +1 = ricavo/positivo, -1 = costo/negativo nel CE

CE_STRUCTURE = [
    # ─── A) VALORE DELLA PRODUZIONE ───
    ("RICAVI",              "Ricavi delle vendite e delle prestazioni", "VALORE_PRODUZIONE", ["RICAVI"],               +1, False),
    ("RIMANENZE_PF",        "Variazione rimanenze prodotti finiti",     "VALORE_PRODUZIONE", ["RIMANENZE_PF"],          +1, False),
    ("RIMANENZE_MP",        "Variazione rimanenze materie prime",       "VALORE_PRODUZIONE", ["RIMANENZE_MP"],          +1, False),
    ("CAPITALIZZAZIONE",    "Incrementi immobilizzazioni per lavori interni", "VALORE_PRODUZIONE", ["CAPITALIZZAZIONE_COSTI"], +1, False),
    ("TOT_VALORE_PROD",     "Totale valore della produzione (A)",       "VALORE_PRODUZIONE", [],                        +1, True),

    # ─── B) COSTI DELLA PRODUZIONE ───
    ("MATERIE_PRIME",       "Materie prime, sussidiarie e merci",       "COSTI_PRODUZIONE", ["MATERIE_PRIME_E_MERCI"],  -1, False),
    ("SERVIZI",             "Costi per servizi",                        "COSTI_PRODUZIONE", ["SERVIZI"],                -1, False),
    ("GODIMENTO_TERZI",     "Costi per godimento beni di terzi",        "COSTI_PRODUZIONE", ["GODIMENTO_BENI_TERZI"],   -1, False),
    ("COSTI_PERSONALE",     "Costi del personale",                      "COSTI_PRODUZIONE", ["COSTI_PERSONALE"],        -1, False),
    ("AMMORT_IMMAT_ESISTENTI", "Ammort. immateriali da bilancio",          "COSTI_PRODUZIONE", [],                          -1, False),  # calcolato
    ("AMMORT_IMMAT_NUOVI",     "Nuovi ammort. immateriali",                "COSTI_PRODUZIONE", [],                          -1, False),  # calcolato
    ("AMMORT_MAT_ESISTENTI",   "Ammort. materiali da bilancio",            "COSTI_PRODUZIONE", [],                          -1, False),  # calcolato
    ("AMMORT_MAT_NUOVI",       "Nuovi ammort. materiali",                  "COSTI_PRODUZIONE", [],                          -1, False),  # calcolato
    ("ACCANTONAMENTI",      "Accantonamenti per rischi e oneri",         "COSTI_PRODUZIONE", ["ACCANTONAMENTI"],         -1, False),
    ("ONERI_DIVERSI",       "Oneri diversi di gestione",                 "COSTI_PRODUZIONE", ["ONERI_DIVERSI_DI_GESTIONE"], -1, False),
    ("COSTI_AFFITTO",       "Canone affitto d'azienda",                  "COSTI_PRODUZIONE", [],                         -1, False),  # da assumptions
    ("TOT_COSTI_PROD",      "Totale costi della produzione (B)",         "COSTI_PRODUZIONE", [],                         -1, True),

    # ─── MARGINI ───
    ("EBITDA",              "EBITDA (Margine operativo lordo)",          "MARGINI", [], +1, True),
    ("TOT_AMMORTAMENTI",    "Totale ammortamenti e accantonamenti",      "MARGINI", [], -1, True),
    ("EBIT",                "Differenza A-B (Reddito operativo)",        "MARGINI", [], +1, True),

    # ─── C) GESTIONE FINANZIARIA ───
    ("PROVENTI_FINANZIARI", "Proventi finanziari",                       "FINANZA", ["PROVENTI_FINANZIARI"], +1, False),
    ("ONERI_FINANZIARI",    "Oneri finanziari",                          "FINANZA", ["ONERI_FINANZIARI"],    -1, False),
    ("TOT_GEST_FIN",        "Totale gestione finanziaria (C)",           "FINANZA", [],                      +1, True),

    # ─── D) GESTIONE STRAORDINARIA ───
    ("PROVENTI_STRAORD",    "Proventi straordinari",                     "STRAORDINARIO", ["PROVENTI_STRAORDINARI"], +1, False),
    ("ONERI_STRAORD",       "Oneri straordinari",                        "STRAORDINARIO", ["ONERI_STRAORDINARI"],    -1, False),
    ("PREDEDUZIONI",        "Costi prededuzione procedura",              "STRAORDINARIO", [],                        -1, False),  # da pipeline
    ("TOT_GEST_STRAORD",    "Totale gestione straordinaria (D)",         "STRAORDINARIO", [],                        +1, True),

    # ─── RISULTATO ANTE IMPOSTE ───
    ("EBT",                 "Risultato prima delle imposte (A-B+C+D)",   "RISULTATO", [], +1, True),

    # ─── E) IMPOSTE ───
    ("IRES",                "IRES",                                      "IMPOSTE", [], -1, False),
    ("IRAP",                "IRAP",                                      "IMPOSTE", [], -1, False),
    ("TOT_IMPOSTE",         "Totale imposte (E)",                        "IMPOSTE", [], -1, True),

    # ─── RISULTATO NETTO ───
    ("UTILE_NETTO",         "Utile (Perdita) dell'esercizio",            "RISULTATO", [], +1, True),
]


def _get_growth_rate(driver: Optional[CeLineDriver], year_index: int) -> D:
    """Restituisce il tasso di crescita per l'anno dato."""
    if driver is None or not driver.growth_rates:
        return ZERO
    rates = driver.growth_rates
    idx = min(year_index, len(rates) - 1)
    return D(str(rates[idx])) / 100


def _get_seasonality(driver: Optional[CeLineDriver], month: int) -> D:
    """Restituisce il coefficiente di stagionalità per il mese (1-12)."""
    if driver is None or not driver.seasonality or len(driver.seasonality) != 12:
        return D(1)
    coeffs = [D(str(s)) for s in driver.seasonality]
    total = sum(coeffs)
    if total == 0:
        return D(1)
    # Normalizza: coefficiente × 12 / somma_coefficienti
    normalized = coeffs[month - 1] * 12 / total
    return normalized


def _compute_monthly_amount(
    base_annual: D,
    period_index: int,
    start_month: int,
    driver: Optional[CeLineDriver],
) -> D:
    """
    Calcola l'importo mensile partendo dalla base annua, applicando:
    1. Growth rate cumulativo fino all'anno corrente
    2. Coefficiente di stagionalità per il mese
    """
    if base_annual == ZERO:
        return ZERO

    # Determina anno e mese correnti
    year_index = period_index // 12
    month_in_year = period_index % 12
    current_month = ((start_month - 1 + month_in_year) % 12) + 1  # 1-12

    # Applica crescita cumulativa
    grown_annual = base_annual
    for y in range(year_index):
        rate = _get_growth_rate(driver, y)
        grown_annual = grown_annual * (1 + rate)

    # Importo mensile base = annuo / 12
    monthly_base = grown_annual / 12

    # Applica stagionalità
    seasonality = _get_seasonality(driver, current_month)
    monthly_amount = (monthly_base * seasonality).quantize(D("0.01"))

    return monthly_amount


def compute_ce_projections(
    db: Session, case_id: str, scenario_id: str = "base",
    interest_override: InterestOverride = None,
) -> int:
    """
    Computa le proiezioni CE dettagliate su N mesi (default 120).
    Pattern: delete-recompute-insert.

    Legge:
    - fin_ce_riclass: basi annue per ogni riclass_code
    - assumptions.ce_drivers: growth_rates e seasonality per codice
    - prededuzioni e affitto: costi aggiuntivi per periodo

    Args:
        interest_override: se fornito, dizionario {period_index: importo_assoluto}
            che sovrascrive il calcolo statico degli ONERI_FINANZIARI.
            Usato dal loop di convergenza SP↔Banca per calcolare dinamicamente
            gli interessi in base al debito effettivo dallo SP.
    """
    db.query(MdmCeProjection).filter(MdmCeProjection.case_id == case_id).filter(MdmCeProjection.scenario_id == scenario_id).delete()

    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    piano = assumptions.piano
    duration = piano.duration_months
    ires_rate = D(str(piano.aliquota_ires)) / 100
    irap_rate = D(str(piano.aliquota_irap)) / 100
    start_month = piano.start_month
    drivers = assumptions.ce_drivers.lines  # Dict[str, CeLineDriver]

    # ── 1. Carica basi annue dal CE riclassificato ──
    # I codici nel DB hanno prefisso "CE_" (es. CE_RICAVI) → lo rimuoviamo
    ce_base: Dict[str, D] = {}
    for row in db.query(CeRiclass).filter(CeRiclass.case_id == case_id).all():
        code = row.riclass_code
        if code.startswith("CE_"):
            code = code[3:]
        ce_base[code] = ce_base.get(code, ZERO) + (row.amount or ZERO)

    # Applica override dalle assumptions se presenti
    for code, driver in drivers.items():
        if driver.override_amount is not None:
            ce_base[code] = D(str(driver.override_amount))

    # ── 2. Carica dati ausiliari ──
    # Prededuzioni per periodo
    preded_rows = get_prededuzione(db, case_id, scenario_id)
    preded_by_period: Dict[int, D] = {}
    for r in preded_rows:
        preded_by_period[r.period_index] = preded_by_period.get(r.period_index, ZERO) + (r.importo_periodo or ZERO)

    # Affitto per periodo
    affitto_rows = get_affitto(db, case_id, scenario_id)
    affitto_by_period: Dict[int, D] = {}
    for r in affitto_rows:
        affitto_by_period[r.period_index] = r.canone or ZERO

    # ── 2b. Opening asset balances from SP riclass (for depreciation split) ──
    sp_data: Dict[str, D] = {}
    for row in db.query(SpRiclass).filter(SpRiclass.case_id == case_id).all():
        code = row.riclass_code
        if code.startswith("SP_"):
            code = code[3:]
        sp_data[code] = sp_data.get(code, ZERO) + (row.amount or ZERO)

    # Opening asset values (net of accumulated depreciation)
    immob_mat_opening = (
        sp_data.get("IMMOBILIZZAZIONI_MATERIALI", ZERO)
        + sp_data.get("F_DO_AMM_TO_IMM_NI_MATERIALI", ZERO)
    )
    immob_immat_opening = (
        sp_data.get("IMMOBILIZZAZIONI_IMMATERIALI", ZERO)
        + sp_data.get("F_DO_AMM_TO_IMM_NI_IMMATERIALI", ZERO)
    )

    # Depreciation rates from assumptions
    depr = assumptions.depreciation
    # Weighted average material rate (mid-point of fabbricati, impianti, attrezzature)
    aliquota_mat = D(str(depr.aliquota_ammort_impianti))
    aliquota_immat = D(str(depr.aliquota_ammort_immateriali))

    # Old-style base annual depreciation from CE riclass (used as fallback and for new depr via growth)
    ce_base_ammort_mat = abs(ce_base.get("AMMORTAMENTI_MATERIALI", ZERO))
    ce_base_ammort_immat = abs(ce_base.get("AMMORTAMENTI_IMMATERIALI", ZERO))

    # Rolling balances for existing asset depreciation
    remaining_mat = abs(immob_mat_opening)
    remaining_immat = abs(immob_immat_opening)

    # ── 3. Genera proiezioni per periodo ──
    count = 0

    for pi in range(duration):
        # Calcola tutti gli importi delle voci base (con growth + seasonality)
        amounts: Dict[str, D] = {}

        for line_code, _, _, riclass_codes, sign, is_subtotal in CE_STRUCTURE:
            if riclass_codes:
                # Voce base: somma dei riclass_codes con growth/seasonality
                total = ZERO
                for rc in riclass_codes:
                    base = abs(ce_base.get(rc, ZERO))
                    driver = drivers.get(rc)
                    monthly = _compute_monthly_amount(base, pi, start_month, driver)
                    total += monthly
                amounts[line_code] = total * sign

        # ── Depreciation: 4-line split ──
        # Existing depreciation = opening_balance × rate / 12, decreasing as assets deplete
        monthly_depr_mat_esist = min(
            (remaining_mat * aliquota_mat / 12).quantize(D("0.01")),
            remaining_mat,
        ) if remaining_mat > ZERO else ZERO
        monthly_depr_immat_esist = min(
            (remaining_immat * aliquota_immat / 12).quantize(D("0.01")),
            remaining_immat,
        ) if remaining_immat > ZERO else ZERO

        # Reduce remaining balances
        remaining_mat = max(remaining_mat - monthly_depr_mat_esist, ZERO)
        remaining_immat = max(remaining_immat - monthly_depr_immat_esist, ZERO)

        # New depreciation: driven by growth on old CE base (if growth_rates configured)
        # Total depreciation from growth-based projection
        driver_mat = drivers.get("AMMORTAMENTI_MATERIALI")
        driver_immat = drivers.get("AMMORTAMENTI_IMMATERIALI")
        total_proj_mat = _compute_monthly_amount(ce_base_ammort_mat, pi, start_month, driver_mat)
        total_proj_immat = _compute_monthly_amount(ce_base_ammort_immat, pi, start_month, driver_immat)

        # New = max(0, projected_total - existing)
        monthly_depr_mat_nuovi = max(total_proj_mat - monthly_depr_mat_esist, ZERO)
        monthly_depr_immat_nuovi = max(total_proj_immat - monthly_depr_immat_esist, ZERO)

        amounts["AMMORT_MAT_ESISTENTI"] = -monthly_depr_mat_esist
        amounts["AMMORT_MAT_NUOVI"] = -monthly_depr_mat_nuovi
        amounts["AMMORT_IMMAT_ESISTENTI"] = -monthly_depr_immat_esist
        amounts["AMMORT_IMMAT_NUOVI"] = -monthly_depr_immat_nuovi

        # ── Override oneri finanziari per convergenza SP↔Banca ──
        if interest_override is not None and pi in interest_override:
            amounts["ONERI_FINANZIARI"] = -abs(interest_override[pi])

        # ── Voci speciali (non da riclass) ──
        affitto_val = affitto_by_period.get(pi, ZERO)
        amounts["COSTI_AFFITTO"] = -affitto_val

        preded_val = preded_by_period.get(pi, ZERO)
        amounts["PREDEDUZIONI"] = -preded_val

        # ── Subtotali calcolati ──
        # A) Valore della produzione
        tot_valore_prod = (
            amounts.get("RICAVI", ZERO)
            + amounts.get("RIMANENZE_PF", ZERO)
            + amounts.get("RIMANENZE_MP", ZERO)
            + amounts.get("CAPITALIZZAZIONE", ZERO)
        )
        amounts["TOT_VALORE_PROD"] = tot_valore_prod

        # Total depreciation (sum of 4 lines, all negative)
        tot_ammort_lines = (
            amounts["AMMORT_MAT_ESISTENTI"]
            + amounts["AMMORT_MAT_NUOVI"]
            + amounts["AMMORT_IMMAT_ESISTENTI"]
            + amounts["AMMORT_IMMAT_NUOVI"]
        )

        # B) Costi della produzione (tutti negativi, il totale è la somma dei valori negativi)
        tot_costi_prod = (
            amounts.get("MATERIE_PRIME", ZERO)
            + amounts.get("SERVIZI", ZERO)
            + amounts.get("GODIMENTO_TERZI", ZERO)
            + amounts.get("COSTI_PERSONALE", ZERO)
            + tot_ammort_lines
            + amounts.get("ACCANTONAMENTI", ZERO)
            + amounts.get("ONERI_DIVERSI", ZERO)
            + amounts.get("COSTI_AFFITTO", ZERO)
        )
        amounts["TOT_COSTI_PROD"] = tot_costi_prod

        # EBITDA = Valore produzione + costi operativi (senza ammortamenti/accantonamenti)
        ebitda = tot_valore_prod + (
            amounts.get("MATERIE_PRIME", ZERO)
            + amounts.get("SERVIZI", ZERO)
            + amounts.get("GODIMENTO_TERZI", ZERO)
            + amounts.get("COSTI_PERSONALE", ZERO)
            + amounts.get("ONERI_DIVERSI", ZERO)
            + amounts.get("COSTI_AFFITTO", ZERO)
        )
        amounts["EBITDA"] = ebitda

        # Totale ammortamenti + accantonamenti
        tot_ammort = (
            tot_ammort_lines
            + amounts.get("ACCANTONAMENTI", ZERO)
        )
        amounts["TOT_AMMORTAMENTI"] = tot_ammort

        # EBIT = Valore produzione - Costi produzione (inclusi ammortamenti)
        ebit = tot_valore_prod + tot_costi_prod
        amounts["EBIT"] = ebit

        # C) Gestione finanziaria
        tot_gest_fin = amounts.get("PROVENTI_FINANZIARI", ZERO) + amounts.get("ONERI_FINANZIARI", ZERO)
        amounts["TOT_GEST_FIN"] = tot_gest_fin

        # D) Gestione straordinaria
        tot_gest_straord = (
            amounts.get("PROVENTI_STRAORD", ZERO)
            + amounts.get("ONERI_STRAORD", ZERO)
            + amounts.get("PREDEDUZIONI", ZERO)
        )
        amounts["TOT_GEST_STRAORD"] = tot_gest_straord

        # EBT
        ebt = ebit + tot_gest_fin + tot_gest_straord
        amounts["EBT"] = ebt

        # Imposte (solo su utile positivo)
        ires = (ebt * ires_rate).quantize(D("0.01")) if ebt > 0 else ZERO
        irap = (ebt * irap_rate).quantize(D("0.01")) if ebt > 0 else ZERO
        tot_imposte = ires + irap
        amounts["IRES"] = -ires
        amounts["IRAP"] = -irap
        amounts["TOT_IMPOSTE"] = -tot_imposte

        # Utile netto
        amounts["UTILE_NETTO"] = ebt - tot_imposte

        # ── Inserisci tutte le righe ──
        for line_code, line_label, section, _, _, is_subtotal in CE_STRUCTURE:
            amount = amounts.get(line_code, ZERO)
            db.add(MdmCeProjection(
                case_id=case_id,
                scenario_id=scenario_id,
                period_index=pi,
                line_code=line_code,
                line_label=line_label,
                section=section,
                amount=amount.quantize(D("0.01")) if isinstance(amount, D) else D(str(amount)).quantize(D("0.01")),
                is_subtotal=is_subtotal,
            ))
            count += 1

    db.commit()
    return count


def get_ce_projections(db: Session, case_id: str, scenario_id: str = "base", period_from: int = 0, period_to: int = 119) -> list:
    return (
        db.query(MdmCeProjection)
        .filter(
            MdmCeProjection.case_id == case_id,
            MdmCeProjection.scenario_id == scenario_id,
            MdmCeProjection.period_index >= period_from,
            MdmCeProjection.period_index <= period_to,
        )
        .order_by(MdmCeProjection.period_index, MdmCeProjection.id)
        .all()
    )
