# app/schemas/assumptions.py
"""Pydantic models per le Assumptions del piano MDM."""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ── Parametri singoli ────────────────────────────────────────

class SpesaProcedura(BaseModel):
    """Costi della procedura (imponibile, contributo cassa 4%, IVA 22%)."""
    compenso_curatore: float = 0.0
    compenso_attestatore: float = 0.0
    compenso_advisor: float = 0.0
    spese_giustizia: float = 0.0
    altre_spese: float = 0.0


class FondoFunzionamento(BaseModel):
    """Fondo per la continuità aziendale."""
    importo_mensile: float = 0.0
    durata_mesi: int = 12


class ParametriAffitto(BaseModel):
    """Parametri per il calcolo dell'affitto d'azienda."""
    canone_annuo: float = 0.0
    aliquota_iva: float = 22.0       # percentuale
    mesi_dilazione_incasso: int = 1   # ritardo incasso vs fatturazione
    mese_inizio: int = 1             # period_index di inizio affitto
    mese_fine: int = 120             # period_index di fine affitto


class ParametriCessione(BaseModel):
    """Parametri per la cessione d'azienda."""
    importo_lordo: float = 0.0
    accollo_tfr: float = 0.0
    accollo_debiti: float = 0.0
    mese_cessione: int = 60          # period_index in cui avviene la cessione


class ParametriPiano(BaseModel):
    """Parametri generali del piano."""
    start_year: int = 2025
    start_month: int = 1
    duration_months: int = 120
    aliquota_ires: float = 24.0
    aliquota_irap: float = 3.9
    aliquota_iva_vendite: float = 22.0
    aliquota_iva_acquisti: float = 22.0


class SpDrivers(BaseModel):
    """
    Driver di proiezione per lo Stato Patrimoniale.

    DSO/DPO/DIO determinano l'evoluzione dinamica del CCN (Capital Circolante Netto):
      crediti = ricavi_mensili × DSO / 30
      rimanenze = costo_venduto_mensile × DIO / 30
      debiti_fornitori = acquisti_mensili × DPO / 30

    pct_debiti_breve: % dei debiti iniziali classificati a breve (il resto è M/L).
    tasso_interesse_debito: tasso annuo % sugli oneri finanziari, usato nel loop di
        convergenza SP↔Banca per calcolare dinamicamente gli interessi sul debito M/L.
    """
    dso: float = 60.0             # Days Sales Outstanding (giorni incasso crediti)
    dpo: float = 60.0             # Days Payable Outstanding (giorni pagamento fornitori)
    dio: float = 30.0             # Days Inventory Outstanding (giorni giacenza rimanenze)
    pct_debiti_breve: float = 40.0  # % debiti totali classificati a breve termine
    tasso_interesse_debito: float = 3.0  # tasso annuo % oneri finanziari su debito M/L


class ParametriLiquidazione(BaseModel):
    """
    Parametri per la liquidazione giudiziale con distribuzione per masse.

    Le masse rappresentano i gruppi di attivo realizzato:
      Massa 1 (Immobiliare): immobilizzazioni materiali (immobili)
      Massa 2 (Mobiliare): beni mobili, crediti, rimanenze, immateriali, finanziarie
      Massa 3 (Generale): disponibilità liquide e cassa

    La waterfall di distribuzione segue l'ordine:
      1. Prededuzioni (pro-rata su tutte le masse)
      2. Ipotecari (da massa 1 - immobiliare)
      3. Privilegiati (da massa 2 - mobiliare + residuo massa 1)
      4. Chirografari (da residuo generale)

    categorie_massa_1/2/3: categorie attivo che confluiscono in ciascuna massa.
    pct_spese_liquidazione: % detratta dal realizzo lordo per spese di liquidazione.
    """
    categorie_massa_1: List[str] = Field(
        default_factory=lambda: ["IMMOBILIZZAZIONI_MATERIALI"],
        description="Categorie attivo → Massa Immobiliare",
    )
    categorie_massa_2: List[str] = Field(
        default_factory=lambda: [
            "IMMOBILIZZAZIONI_IMMATERIALI", "IMMOBILIZZAZIONI_FINANZIARIE",
            "RIMANENZE", "CREDITI_COMMERCIALI", "CREDITI_VS_CONTROLLATE",
            "CREDITI_VS_COLLEGATE", "CREDITI_VS_CONTROLLANTI",
            "CREDITI_TRIBUTARI", "CREDITI_IMPOSTE_ANTICIPATE", "CREDITI_VS_ALTRI",
            "ATTIVITA_FINANZIARIE", "RATEI_RISCONTI_ATTIVI",
            "TITOLI", "PARTECIPAZIONI", "AVVIAMENTO", "ALTRI_BENI_IMMATERIALI",
            "ALTRO_ATTIVO",
        ],
        description="Categorie attivo → Massa Mobiliare",
    )
    categorie_massa_3: List[str] = Field(
        default_factory=lambda: ["DISPONIBILITA_LIQUIDE", "CASSA", "BANCA_CC"],
        description="Categorie attivo → Massa Generale (liquida)",
    )
    pct_spese_liquidazione: float = 10.0  # % di spese detratte dal realizzo lordo


class ClasseCreditoreSchedule(BaseModel):
    """
    Schedule di pagamento per una singola classe di creditori nel concordato.

    classe: identificativo (PREDEDUZIONE, IPOTECARIO, PRIVILEGIATO, CHIROGRAFARIO,
            oppure sottoclassi come PRIVILEGIATO_A, CHIROGRAFARIO_1, etc.)
    pct_soddisfazione_proposta: % del credito ammesso che il piano propone di pagare.
    mese_inizio_pagamento: period_index del primo pagamento (grace period / dilazione).
    mese_fine_pagamento: period_index dell'ultimo pagamento.
    tipo_pagamento: RATEALE (rate costanti) o UNICO (lump sum a mese_inizio).
    priorita: ordine di pagamento (0 = massima priorità). In caso di cassa insufficiente,
              le classi con priorità più alta vengono servite per prime.
    """
    classe: str
    pct_soddisfazione_proposta: float = 100.0
    mese_inizio_pagamento: int = 0
    mese_fine_pagamento: int = 119
    tipo_pagamento: str = "RATEALE"   # RATEALE | UNICO
    priorita: int = 0


class ParametriConcordato(BaseModel):
    """
    Parametri per il piano concordatario: scheduling dei pagamenti per classe creditore.

    classi: lista di schedule per ciascuna classe. Se vuota, viene usato un default
            con 4 classi standard (prededuzione 100%, ipotecario 100%, privilegiato 80%,
            chirografario 20%).
    usa_cassa_disponibile: se True, i pagamenti mensili sono limitati dalla cassa
            disponibile (flusso netto positivo dalla proiezione banca).
            Se False, i pagamenti seguono lo schedule indipendentemente dalla cassa.
    """
    classi: List[ClasseCreditoreSchedule] = Field(default_factory=lambda: [
        ClasseCreditoreSchedule(classe="PREDEDUZIONE", pct_soddisfazione_proposta=100.0,
                                mese_inizio_pagamento=0, mese_fine_pagamento=23,
                                tipo_pagamento="RATEALE", priorita=0),
        ClasseCreditoreSchedule(classe="IPOTECARIO", pct_soddisfazione_proposta=100.0,
                                mese_inizio_pagamento=12, mese_fine_pagamento=84,
                                tipo_pagamento="RATEALE", priorita=1),
        ClasseCreditoreSchedule(classe="PRIVILEGIATO", pct_soddisfazione_proposta=80.0,
                                mese_inizio_pagamento=12, mese_fine_pagamento=84,
                                tipo_pagamento="RATEALE", priorita=2),
        ClasseCreditoreSchedule(classe="CHIROGRAFARIO", pct_soddisfazione_proposta=20.0,
                                mese_inizio_pagamento=24, mese_fine_pagamento=119,
                                tipo_pagamento="RATEALE", priorita=3),
    ])
    usa_cassa_disponibile: bool = True


class CeLineDriver(BaseModel):
    """
    Driver di proiezione per una singola voce CE.

    growth_rates: lista di tassi di crescita annui (%) applicati anno per anno.
                  Es. [5.0, 3.0, 2.0] = +5% anno 1, +3% anno 2, +2% anno 3+
                  Se la lista è più corta della durata, l'ultimo valore viene ripetuto.
    seasonality:  12 coefficienti mensili (gen-dic), default tutti 1.0 = distribuzione uniforme.
                  Es. [0.8, 0.9, 1.0, 1.0, 1.1, 1.2, 1.2, 0.7, 1.0, 1.1, 1.0, 1.0]
                  I coefficienti vengono normalizzati in modo che la somma = 12.
    override_amount: se valorizzato, sostituisce il valore dal riclassificato come base annua.
    """
    growth_rates: List[float] = Field(default_factory=list)
    seasonality: List[float] = Field(default_factory=lambda: [1.0] * 12)
    override_amount: Optional[float] = None


class CeDrivers(BaseModel):
    """
    Drivers di proiezione CE per tutte le voci riclassificate.
    Le chiavi sono i riclass_code dal fin_ce_riclass:
      RICAVI, RIMANENZE_PF, RIMANENZE_MP, CAPITALIZZAZIONE_COSTI,
      MATERIE_PRIME_E_MERCI, SERVIZI, GODIMENTO_BENI_TERZI,
      ONERI_DIVERSI_DI_GESTIONE, COSTI_PERSONALE,
      AMMORTAMENTI_IMMATERIALI, AMMORTAMENTI_MATERIALI, ACCANTONAMENTI,
      PROVENTI_STRAORDINARI, ONERI_STRAORDINARI,
      PROVENTI_FINANZIARI, ONERI_FINANZIARI, IMPOSTE
    """
    lines: Dict[str, CeLineDriver] = Field(default_factory=dict)


# ── Modello complessivo ─────────────────────────────────────

class AssumptionsData(BaseModel):
    """Struttura completa delle assumptions salvate in JSON."""
    piano: ParametriPiano = Field(default_factory=ParametriPiano)
    spese_procedura: SpesaProcedura = Field(default_factory=SpesaProcedura)
    fondo_funzionamento: FondoFunzionamento = Field(default_factory=FondoFunzionamento)
    affitto: ParametriAffitto = Field(default_factory=ParametriAffitto)
    cessione: ParametriCessione = Field(default_factory=ParametriCessione)
    ce_drivers: CeDrivers = Field(default_factory=CeDrivers)
    sp_drivers: SpDrivers = Field(default_factory=SpDrivers)
    liquidazione: ParametriLiquidazione = Field(default_factory=ParametriLiquidazione)
    concordato: ParametriConcordato = Field(default_factory=ParametriConcordato)
    custom: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


# ── Request / Response ───────────────────────────────────────

class AssumptionsResponse(BaseModel):
    case_id: str
    data: AssumptionsData

    class Config:
        from_attributes = True


class AssumptionsUpdate(BaseModel):
    data: AssumptionsData
