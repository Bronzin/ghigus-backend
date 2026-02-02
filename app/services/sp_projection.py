# app/services/sp_projection.py
"""
Motore proiezione Stato Patrimoniale con CCN dinamico (DSO/DPO/DIO).

Struttura SP conforme al foglio SP-mese dell'Excel MDM:
  ATTIVO CORRENTE:
    - Disponibilità liquide (cassa bilanciamento)
    - Crediti commerciali (dinamico via DSO)
    - Rimanenze (dinamico via DIO)
    - Ratei e risconti attivi
  ATTIVO FISSO:
    - Immobilizzazioni immateriali (nette di fondo ammortamento)
    - Immobilizzazioni materiali (nette di fondo ammortamento)
    - Immobilizzazioni finanziarie
    - Immobilizzazioni in leasing
  PASSIVO CORRENTE:
    - Debiti a breve termine (dinamico via DPO + quota prededuzioni)
  PASSIVO M/L:
    - Debiti a medio/lungo termine
    - Fondi (TFR e altri)
  PATRIMONIO NETTO:
    - Capitale sociale
    - Riserve
    - Utile/perdita esercizi precedenti
    - Utile/perdita esercizio corrente

Il totale attivo deve bilanciare con totale passivo + PN.
La cassa è la variabile di bilanciamento.

I codici riclass letti dal DB sono quelli reali da maps_sp_ready.csv:
  LIQUIDITA_E_ESIGIBILITA_IMMEDIATE, CREDITI, RIMANENZE, RATEI_E_RISCONTI,
  IMMOBILIZZAZIONI_IMMATERIALI, IMMOBILIZZAZIONI_MATERIALI,
  IMMOBILIZZAZIONI_FINANZIARIE, IMMOBILIZZAZIONI_LEASING,
  F_DO_AMM_TO_IMM_NI_IMMATERIALI, F_DO_AMM_TO_IMM_NI_MATERIALI,
  DEBITI, FONDI,
  CAPITALE, RISERVE, UTILE_PERDITA_ESERCIZIO, UTILE_PERDITA_A_NUOVO,
  CREDITI_X_AUMENTO_CAPITALE
"""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Dict

from app.db.models.mdm_projections import MdmSpProjection, MdmCeProjection
from app.db.models.final import SpRiclass
from app.services.assumptions import get_assumptions_or_default
from app.services.prededuzione import get_prededuzione

D = Decimal
ZERO = D(0)
THIRTY = D(30)


def compute_sp_projections(db: Session, case_id: str, scenario_id: str = "base") -> int:
    """
    Computa le proiezioni SP su N mesi (default 120).
    Richiede che le proiezioni CE siano già calcolate.
    Pattern: delete-recompute-insert.

    CCN dinamico:
      crediti = ricavi_mensili × DSO / 30
      rimanenze = costo_mat_mensile × DIO / 30
      debiti_fornitori = acquisti_mensili × DPO / 30
    """
    db.query(MdmSpProjection).filter(MdmSpProjection.case_id == case_id).filter(MdmSpProjection.scenario_id == scenario_id).delete()

    assumptions = get_assumptions_or_default(db, case_id, scenario_id)
    piano = assumptions.piano
    duration = piano.duration_months
    sp_drv = assumptions.sp_drivers

    dso = D(str(sp_drv.dso))
    dpo = D(str(sp_drv.dpo))
    dio = D(str(sp_drv.dio))
    pct_breve = D(str(sp_drv.pct_debiti_breve)) / 100

    # ── 1. Carica SP riclassificato (valori iniziali) ──
    # I codici nel DB hanno prefisso "SP_" (es. SP_CREDITI) → lo rimuoviamo
    sp_data: Dict[str, D] = {}
    for row in db.query(SpRiclass).filter(SpRiclass.case_id == case_id).all():
        code = row.riclass_code
        if code.startswith("SP_"):
            code = code[3:]
        sp_data[code] = sp_data.get(code, ZERO) + (row.amount or ZERO)

    def sp_get(code: str) -> D:
        return sp_data.get(code, ZERO)

    # Attivo corrente
    cassa_iniziale = sp_get("LIQUIDITA_E_ESIGIBILITA_IMMEDIATE")
    crediti_iniziale = sp_get("CREDITI")
    rimanenze_iniziale = sp_get("RIMANENZE")
    ratei_risconti_iniziale = sp_get("RATEI_E_RISCONTI")

    # Attivo fisso (lordo - fondo ammortamento = netto)
    immob_immat_iniziale = sp_get("IMMOBILIZZAZIONI_IMMATERIALI") + sp_get("F_DO_AMM_TO_IMM_NI_IMMATERIALI")
    immob_mat_iniziale = sp_get("IMMOBILIZZAZIONI_MATERIALI") + sp_get("F_DO_AMM_TO_IMM_NI_MATERIALI")
    immob_fin_iniziale = sp_get("IMMOBILIZZAZIONI_FINANZIARIE")
    immob_leasing_iniziale = sp_get("IMMOBILIZZAZIONI_LEASING")

    # Passivo (valori negativi in SP → abs)
    debiti_totali_iniziale = abs(sp_get("DEBITI"))
    debiti_breve_iniziale = (debiti_totali_iniziale * pct_breve).quantize(D("0.01"))
    debiti_lungo_iniziale = debiti_totali_iniziale - debiti_breve_iniziale
    fondi_iniziale = abs(sp_get("FONDI"))

    # Patrimonio netto
    capitale_iniziale = sp_get("CAPITALE")
    riserve_iniziale = sp_get("RISERVE") + sp_get("CREDITI_X_AUMENTO_CAPITALE")
    utile_a_nuovo_iniziale = sp_get("UTILE_PERDITA_A_NUOVO")
    utile_esercizio_iniziale = sp_get("UTILE_PERDITA_ESERCIZIO")

    # ── 2. Carica dati CE per DSO/DPO/DIO ──
    ce_map: Dict[int, Dict[str, D]] = {}
    for row in db.query(MdmCeProjection).filter(MdmCeProjection.case_id == case_id).filter(MdmCeProjection.scenario_id == scenario_id).all():
        ce_map.setdefault(row.period_index, {})[row.line_code] = row.amount or ZERO

    # Ammortamento per tipo dal CE
    def ce_get(pi: int, code: str) -> D:
        return ce_map.get(pi, {}).get(code, ZERO)

    # ── 3. Prededuzioni come riduzione debiti ──
    preded_rows = get_prededuzione(db, case_id, scenario_id)
    preded_by_period: Dict[int, D] = {}
    for r in preded_rows:
        preded_by_period[r.period_index] = preded_by_period.get(r.period_index, ZERO) + (r.importo_periodo or ZERO)

    # ── 4. Proiezione rolling ──
    count = 0

    # Variabili rolling
    immob_immat = immob_immat_iniziale
    immob_mat = immob_mat_iniziale
    immob_fin = immob_fin_iniziale
    immob_leasing = immob_leasing_iniziale
    ratei_risconti = ratei_risconti_iniziale

    debiti_breve = debiti_breve_iniziale
    debiti_lungo = debiti_lungo_iniziale
    fondi = fondi_iniziale

    capitale = capitale_iniziale
    riserve = riserve_iniziale
    utile_a_nuovo = utile_a_nuovo_iniziale + utile_esercizio_iniziale  # anno 0: utile esercizio passa a riporto
    utile_esercizio_cumulato = ZERO  # utile dell'anno corrente (reset ogni 12 mesi)

    for pi in range(duration):
        utile_mese = ce_get(pi, "UTILE_NETTO")
        # Sum all 4 depreciation lines (existing + new for each asset type)
        ammort_immat = (
            abs(ce_get(pi, "AMMORT_IMMAT_ESISTENTI"))
            + abs(ce_get(pi, "AMMORT_IMMAT_NUOVI"))
        )
        ammort_mat = (
            abs(ce_get(pi, "AMMORT_MAT_ESISTENTI"))
            + abs(ce_get(pi, "AMMORT_MAT_NUOVI"))
        )
        preded_pag = preded_by_period.get(pi, ZERO)

        # ── Immobilizzazioni: si riducono per ammortamento ──
        immob_immat = max(immob_immat - ammort_immat, ZERO)
        immob_mat = max(immob_mat - ammort_mat, ZERO)
        # immob_fin e leasing restano costanti (semplificazione)

        # ── Debiti breve: si riducono per prededuzioni ──
        debiti_breve = max(debiti_breve - preded_pag, ZERO)

        # ── CCN dinamico via DSO/DPO/DIO ──
        ricavi_mese = abs(ce_get(pi, "RICAVI"))
        mat_prime_mese = abs(ce_get(pi, "MATERIE_PRIME"))
        servizi_mese = abs(ce_get(pi, "SERVIZI"))
        godimento_mese = abs(ce_get(pi, "GODIMENTO_TERZI"))
        acquisti_mese = mat_prime_mese + servizi_mese + godimento_mese

        # Crediti commerciali: funzione del DSO
        if ricavi_mese > ZERO:
            crediti = (ricavi_mese * dso / THIRTY).quantize(D("0.01"))
        else:
            crediti = crediti_iniziale if pi == 0 else ZERO

        # Rimanenze: funzione del DIO (basato sul costo materie prime)
        if mat_prime_mese > ZERO:
            rimanenze = (mat_prime_mese * dio / THIRTY).quantize(D("0.01"))
        else:
            rimanenze = rimanenze_iniziale if pi == 0 else ZERO

        # Debiti fornitori: funzione del DPO (aggiunto ai debiti breve strutturali)
        if acquisti_mese > ZERO:
            debiti_fornitori = (acquisti_mese * dpo / THIRTY).quantize(D("0.01"))
        else:
            debiti_fornitori = ZERO

        # ── Patrimonio Netto: utile si cumula nell'anno ──
        utile_esercizio_cumulato += utile_mese

        # A fine anno (ogni 12 mesi), utile esercizio passa a utile a nuovo
        if pi > 0 and (pi + 1) % 12 == 0:
            utile_a_nuovo += utile_esercizio_cumulato
            utile_esercizio_cumulato = ZERO

        # ── Totali per sezione ──
        totale_attivo_fisso = immob_immat + immob_mat + immob_fin + immob_leasing
        totale_attivo_corrente_no_cassa = crediti + rimanenze + ratei_risconti

        debiti_breve_totale = debiti_breve + debiti_fornitori
        totale_passivo_corrente = debiti_breve_totale
        totale_passivo_ml = debiti_lungo + fondi
        pn = capitale + riserve + utile_a_nuovo + utile_esercizio_cumulato
        totale_passivo_pn = totale_passivo_corrente + totale_passivo_ml + pn

        # ── Bilanciamento: cassa = totale_passivo_pn - attivo_fisso - attivo_corrente_no_cassa ──
        cassa = totale_passivo_pn - totale_attivo_fisso - totale_attivo_corrente_no_cassa

        totale_attivo_corrente = cassa + crediti + rimanenze + ratei_risconti
        totale_attivo = totale_attivo_fisso + totale_attivo_corrente

        # ── Output lines ──
        lines = [
            # ATTIVO CORRENTE
            ("CASSA", "Disponibilità liquide", "ATTIVO_CORRENTE", cassa, False),
            ("CREDITI_COMM", "Crediti commerciali", "ATTIVO_CORRENTE", crediti, False),
            ("RIMANENZE", "Rimanenze", "ATTIVO_CORRENTE", rimanenze, False),
            ("RATEI_RISCONTI_A", "Ratei e risconti attivi", "ATTIVO_CORRENTE", ratei_risconti, False),
            ("TOT_ATTIVO_CORRENTE", "Totale attivo corrente", "ATTIVO_CORRENTE", totale_attivo_corrente, True),

            # ATTIVO FISSO
            ("IMMOB_IMMATERIALI", "Immobilizzazioni immateriali", "ATTIVO_FISSO", immob_immat, False),
            ("IMMOB_MATERIALI", "Immobilizzazioni materiali", "ATTIVO_FISSO", immob_mat, False),
            ("IMMOB_FINANZIARIE", "Immobilizzazioni finanziarie", "ATTIVO_FISSO", immob_fin, False),
            ("IMMOB_LEASING", "Immobilizzazioni in leasing", "ATTIVO_FISSO", immob_leasing, False),
            ("TOT_ATTIVO_FISSO", "Totale attivo fisso", "ATTIVO_FISSO", totale_attivo_fisso, True),

            ("TOTALE_ATTIVO", "TOTALE ATTIVO", "TOTALE", totale_attivo, True),

            # PASSIVO CORRENTE
            ("DEBITI_BREVE", "Debiti a breve termine", "PASSIVO_CORRENTE", debiti_breve_totale, False),
            ("TOT_PASSIVO_CORRENTE", "Totale passivo corrente", "PASSIVO_CORRENTE", totale_passivo_corrente, True),

            # PASSIVO M/L
            ("DEBITI_LUNGO", "Debiti a medio/lungo termine", "PASSIVO_ML", debiti_lungo, False),
            ("TFR", "Fondi (TFR e altri)", "PASSIVO_ML", fondi, False),
            ("TOT_PASSIVO_ML", "Totale passivo M/L", "PASSIVO_ML", totale_passivo_ml, True),

            # PATRIMONIO NETTO
            ("CAPITALE", "Capitale sociale", "PN", capitale, False),
            ("RISERVE", "Riserve", "PN", riserve, False),
            ("UTILE_A_NUOVO", "Utile/perdita esercizi precedenti", "PN", utile_a_nuovo, False),
            ("UTILE_ESERCIZIO", "Utile/perdita esercizio", "PN", utile_esercizio_cumulato, False),
            ("PATRIMONIO_NETTO", "Totale patrimonio netto", "PN", pn, True),

            ("TOTALE_PASSIVO_PN", "TOTALE PASSIVO + PN", "TOTALE", totale_passivo_pn, True),
        ]

        for code, label, section, amount, is_sub in lines:
            val = amount.quantize(D("0.01")) if isinstance(amount, D) else D(str(amount)).quantize(D("0.01"))
            db.add(MdmSpProjection(
                case_id=case_id,
                scenario_id=scenario_id,
                period_index=pi,
                line_code=code,
                line_label=label,
                section=section,
                amount=val,
                is_subtotal=is_sub,
            ))
            count += 1

    db.commit()
    return count


def get_sp_projections(db: Session, case_id: str, scenario_id: str = "base", period_from: int = 0, period_to: int = 119) -> list:
    return (
        db.query(MdmSpProjection)
        .filter(
            MdmSpProjection.case_id == case_id,
            MdmSpProjection.scenario_id == scenario_id,
            MdmSpProjection.period_index >= period_from,
            MdmSpProjection.period_index <= period_to,
        )
        .order_by(MdmSpProjection.period_index, MdmSpProjection.id)
        .all()
    )
