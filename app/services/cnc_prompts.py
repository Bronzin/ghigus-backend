# app/services/cnc_prompts.py
"""
Prompt Builder per Commenti AI Professionali CNC

Costruisce prompt ottimizzati per OpenAI per generare analisi finanziarie
professionali nel contesto della Composizione Negoziata della Crisi (CNC).

Ported from ghigus-cnc/src/prompts.py.
"""
from typing import Optional


class PromptBuilder:
    """Costruttore di prompt per commenti AI professionali CNC"""

    def __init__(self) -> None:
        self.base_system = """Sei un consulente esperto in analisi economico-finanziaria
e Composizione Negoziata della Crisi (CNC) secondo il D.Lgs. 14/2019 (Codice della Crisi).

Il tuo ruolo è fornire analisi professionali, dettagliate e rigorosamente basate sui dati.

REGOLE FONDAMENTALI:
1. Cita SEMPRE numeri specifici dalla tabella (es. "ricavi pari a 1.234.567€")
2. Calcola variazioni percentuali precise (es. "incremento del 15,3%")
3. Usa formato numeri italiano (punto per migliaia, virgola per decimali)
4. Confronta sempre con periodi precedenti quando disponibili
5. Identifica trend, criticità e opportunità
6. Mantieni tono professionale ma accessibile
7. Struttura l'analisi in paragrafi chiari
8. Concludi con implicazioni per il piano di risanamento

NON FARE:
- Non usare frasi generiche senza numeri
- Non inventare dati non presenti nella tabella
- Non essere vago o approssimativo
- Non omettere criticità evidenti dai dati"""

        self.formatting_rules = """
FORMATTAZIONE OUTPUT:
- Usa paragrafi separati per ogni sezione
- Evidenzia i numeri chiave
- Lunghezza: 400-600 parole
- Stile: professionale, analitico, oggettivo"""

    def _format_table_for_prompt(self, table_data: list[list[str]]) -> str:
        """Formatta i dati tabella per inclusione nel prompt"""
        if not table_data:
            return "(Nessun dato disponibile)"

        lines = []
        for row in table_data:
            cells = [str(cell).strip() for cell in row if cell]
            if cells:
                lines.append(" | ".join(cells))

        return "\n".join(lines)

    def analisi_economica(self, table_data: list[list[str]], periodo: str) -> dict[str, str]:
        """Prompt per analisi del Conto Economico"""
        table_str = self._format_table_for_prompt(table_data)

        user_prompt = f"""Analizza il seguente Conto Economico riclassificato per il periodo {periodo}:

DATI TABELLA:
{table_str}

Fornisci un'analisi professionale (500-600 parole) strutturata come segue:

1. ANDAMENTO DEI RICAVI E VALORE DELLA PRODUZIONE
- Valore assoluto dei ricavi per ciascun anno
- Variazione percentuale anno su anno
- Trend complessivo (crescita, stabilità, contrazione)
- Composizione ricavi se disponibile

2. STRUTTURA DEI COSTI E MARGINI OPERATIVI
- Incidenza costi variabili su ricavi (in %)
- Evoluzione costi fissi in valore assoluto
- Margine Operativo Lordo (MOL/EBITDA): valore e % sui ricavi
- Confronto marginalità tra anni

3. RISULTATO OPERATIVO E GESTIONI ACCESSORIE
- Reddito Operativo (EBIT) e sua evoluzione
- Impatto gestione finanziaria (oneri/proventi finanziari)
- Gestione straordinaria se presente
- Imposte e risultato netto finale

4. INDICATORI DI CRITICITÀ
- Eventuali perdite e loro entità
- Margini negativi o in deterioramento
- Squilibri strutturali tra ricavi e costi
- Segnali di insostenibilità del modello di business

5. IMPLICAZIONI PER IL PIANO DI RISANAMENTO CNC
- Sostenibilità della struttura economica attuale
- Interventi correttivi necessari (riduzione costi, incremento ricavi)
- Previsioni di break-even
- Prospettive di ritorno all'equilibrio economico

{self.formatting_rules}

IMPORTANTE: Basa l'analisi ESCLUSIVAMENTE sui dati forniti nella tabella.
Cita i valori specifici e calcola le variazioni percentuali."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def analisi_finanziaria(self, table_data: list[list[str]], periodo: str) -> dict[str, str]:
        """Prompt per analisi del Rendiconto Finanziario"""
        table_str = self._format_table_for_prompt(table_data)

        user_prompt = f"""Analizza il seguente Rendiconto Finanziario per il periodo {periodo}:

DATI TABELLA:
{table_str}

Fornisci un'analisi professionale (500-600 parole) strutturata come segue:

1. FLUSSO DI CASSA DELLA GESTIONE OPERATIVA
- Cash flow operativo generato/assorbito per anno
- Variazioni del capitale circolante netto
- Capacità di autofinanziamento
- Trend della generazione di cassa operativa

2. FLUSSO DI CASSA DA ATTIVITÀ DI INVESTIMENTO
- Investimenti in immobilizzazioni (CAPEX)
- Disinvestimenti e dismissioni
- Saldo netto investimenti
- Strategia di investimento evidenziata

3. FLUSSO DI CASSA DA ATTIVITÀ FINANZIARIA
- Nuovi finanziamenti ottenuti
- Rimborsi di debiti finanziari
- Movimenti di capitale proprio
- Saldo netto finanziario

4. DINAMICA DELLA LIQUIDITÀ
- Variazione netta liquidità periodo
- Posizione di cassa iniziale e finale
- Tensioni di tesoreria evidenti
- Momenti critici di liquidità

5. VALUTAZIONE SOSTENIBILITÀ FINANZIARIA
- Capacità di generare cassa per servizio debito
- Dipendenza da nuova finanza
- Equilibrio tra flussi operativi e finanziari
- Implicazioni per piano CNC

{self.formatting_rules}

Cita valori specifici e calcola i rapporti finanziari rilevanti."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def stato_patrimoniale(self, table_data: list[list[str]], periodo: str) -> dict[str, str]:
        """Prompt per analisi dello Stato Patrimoniale"""
        table_str = self._format_table_for_prompt(table_data)

        user_prompt = f"""Analizza il seguente Stato Patrimoniale riclassificato per il periodo {periodo}:

DATI TABELLA:
{table_str}

Fornisci un'analisi professionale (500-600 parole) strutturata come segue:

1. STRUTTURA DELL'ATTIVO
- Composizione: immobilizzazioni vs attivo circolante (valori e %)
- Principali voci dell'attivo e loro peso
- Liquidità immediate e differite
- Evoluzione nel tempo delle principali voci

2. STRUTTURA DEL PASSIVO E PATRIMONIO NETTO
- Rapporto mezzi propri / mezzi terzi
- Composizione debiti (breve vs lungo termine)
- Evoluzione patrimonio netto
- Eventuali perdite accumulate

3. INDICI DI SOLIDITÀ PATRIMONIALE
- Current Ratio (Attivo Circolante / Passivo Corrente)
- Debt to Equity Ratio
- Indice di rigidità degli impieghi
- Margine di struttura

4. EQUILIBRIO FINANZIARIO STRUTTURALE
- Correlazione fonti/impieghi per scadenza
- Capitale Circolante Netto
- Posizione Finanziaria Netta
- Segnali di squilibrio patrimoniale

5. IMPLICAZIONI PER IL PIANO CNC
- Margini di manovra patrimoniali
- Asset potenzialmente liquidabili
- Rettifiche necessarie
- Ricostituzione patrimonio netto

{self.formatting_rules}

Calcola tutti gli indici e cita i valori assoluti dalla tabella."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def posizione_finanziaria_netta(self, table_data: list[list[str]], periodo: str) -> dict[str, str]:
        """Prompt per analisi della Posizione Finanziaria Netta"""
        table_str = self._format_table_for_prompt(table_data)

        user_prompt = f"""Analizza la Posizione Finanziaria Netta (PFN) per il periodo {periodo}:

DATI TABELLA:
{table_str}

Fornisci un'analisi professionale (400-500 parole) strutturata come segue:

1. COMPOSIZIONE DELLA PFN
- Disponibilità liquide
- Crediti finanziari correnti
- Debiti finanziari a breve termine
- Debiti finanziari a medio-lungo termine
- PFN risultante (valore assoluto)

2. EVOLUZIONE TEMPORALE
- Variazione PFN anno su anno (valore e %)
- Trend dell'indebitamento finanziario netto
- Fattori che hanno determinato le variazioni
- Confronto con anni precedenti

3. INDICATORI DI SOSTENIBILITÀ
- Rapporto PFN/EBITDA (se EBITDA disponibile)
- PFN/Patrimonio Netto
- Incidenza oneri finanziari su MOL
- Capacità di servizio del debito

4. ANALISI DEL RISCHIO FINANZIARIO
- Livello di leva finanziaria
- Concentrazione scadenze debito
- Esposizione a variazioni tassi
- Dipendenza dal sistema bancario

5. IMPLICAZIONI PER RISTRUTTURAZIONE
- Sostenibilità attuale del debito
- Necessità di rinegoziazione
- Target PFN post-ristrutturazione
- Manovre richieste (stralci, riscadenziamenti)

{self.formatting_rules}

Cita tutti i valori dalla tabella e calcola le variazioni percentuali."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def rettifiche_attivo(self, table_data: list[list[str]], anno_riferimento: str = "") -> dict[str, str]:
        """Prompt per analisi delle Rettifiche all'Attivo Patrimoniale"""
        table_str = self._format_table_for_prompt(table_data)

        user_prompt = f"""Analizza le Rettifiche applicate all'Attivo Patrimoniale{' al ' + anno_riferimento if anno_riferimento else ''}:

DATI TABELLA:
{table_str}

IMPORTANTE: Fornisci un'analisi DETTAGLIATA di 500-600 parole. Analizza in profondità
TUTTE le voci mostrate, non solo le principali. Se i valori sono a zero, analizza
la struttura delle voci e indica cosa dovrebbe essere rettificato e con quali criteri.

Struttura l'analisi come segue:

1. RIEPILOGO RETTIFICHE PER CATEGORIA
Per ciascuna voce dell'attivo rettificata, indica:
- Valore contabile originario
- Valore rettificato/di realizzo
- Importo della rettifica
- Motivazione tecnica (svalutazione, irrealizzabilità, valore di mercato)

2. IMMOBILIZZAZIONI
- Rettifiche su immobilizzazioni materiali (immobili, impianti, macchinari)
- Rettifiche su immobilizzazioni immateriali
- Rettifiche su partecipazioni e crediti finanziari
- Valore recuperabile stimato

3. ATTIVO CIRCOLANTE
- Svalutazione crediti commerciali (fondo rischi su crediti)
- Rettifica rimanenze (obsolescenza, valori di realizzo)
- Altre poste dell'attivo circolante
- Percentuale di svalutazione applicata

4. IMPATTO COMPLESSIVO
- Totale rettifiche attivo (valore assoluto)
- Percentuale di svalutazione complessiva
- Effetto su patrimonio netto
- Attivo rettificato finale

5. PIANO DI REALIZZO
- Asset destinati a liquidazione
- Tempistiche di realizzo previste
- Risorse disponibili per soddisfacimento creditori
- Priorità di smobilizzo

{self.formatting_rules}

Analizza OGNI voce rettificata con valori precisi. Obiettivo: 500-600 parole."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def rettifiche_passivo(self, table_data: list[list[str]], anno_riferimento: str = "") -> dict[str, str]:
        """Prompt per analisi delle Rettifiche al Passivo Patrimoniale"""
        table_str = self._format_table_for_prompt(table_data)

        user_prompt = f"""Analizza le Rettifiche applicate al Passivo Patrimoniale{' al ' + anno_riferimento if anno_riferimento else ''}:

DATI TABELLA:
{table_str}

IMPORTANTE: Fornisci un'analisi DETTAGLIATA di 500-600 parole. Analizza in profondità
TUTTE le voci mostrate, non solo le principali. Se i valori sono a zero, analizza
la struttura delle voci e indica cosa dovrebbe essere rettificato e con quali criteri.

Struttura l'analisi come segue:

1. CLASSIFICAZIONE DEBITI PER CREDITORE
Per ciascuna categoria di creditore:
- Debito contabile originario
- Percentuale di soddisfacimento proposta
- Importo riconosciuto/pagato
- Stralcio/falcidia applicata

2. DEBITI PRIVILEGIATI
- Debiti verso dipendenti (TFR, retribuzioni)
- Debiti tributari e previdenziali
- Debiti con privilegio speciale
- Trattamento proposto (100% o transazione fiscale)

3. DEBITI CHIROGRAFARI
- Debiti verso fornitori
- Debiti verso banche (quota chirografaria)
- Altri debiti
- Percentuale falcidia proposta

4. IMPATTO FINANZIARIO DELLE RETTIFICHE
- Riduzione complessiva del debito
- Provento straordinario da stralcio
- Nuovo livello di indebitamento post-rettifiche
- Effetto su patrimonio netto

5. CONVENIENZA E SOSTENIBILITÀ
- Confronto soddisfacimento vs liquidazione giudiziale
- Sostenibilità piano pagamenti
- Margini di sicurezza
- Logica di trattamento differenziato

{self.formatting_rules}

Fornisci analisi per OGNI categoria di creditore con importi precisi. Obiettivo: 500-600 parole."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def piano_flussi(self, table_data: list[list[str]], anno: int) -> dict[str, str]:
        """Prompt per analisi del Piano dei Flussi Finanziari"""
        table_str = self._format_table_for_prompt(table_data)

        user_prompt = f"""Analizza il Piano dei Flussi Finanziari per l'Anno {anno}:

DATI TABELLA:
{table_str}

Fornisci un'analisi professionale (500-600 parole) strutturata come segue:

1. FLUSSI IN ENTRATA
- Incassi da attività operativa (mese per mese se disponibile)
- Incassi da realizzo asset (dismissioni, vendite)
- Nuova finanza prevista (finanziamenti, apporti soci)
- Altri proventi
- Totale entrate previste

2. FLUSSI IN USCITA
- Costi operativi (personale, fornitori, utenze)
- Investimenti necessari per continuità
- Spese prededucibili (professionisti, procedure)
- Imposte e contributi
- Totale uscite previste

3. DINAMICA MENSILE DI TESORERIA
- Saldo iniziale periodo
- Andamento mese per mese
- Identificazione picchi negativi
- Momenti di massima tensione finanziaria
- Margini di sicurezza

4. DISPONIBILITÀ PER CREDITORI
- Cassa generata disponibile per pagamenti
- Priorità: spese prededucibili
- Residuo per soddisfacimento creditori concordatari
- Copertura impegni assunti

5. ANALISI SOSTENIBILITÀ
- Adeguatezza flussi vs impegni
- Stress test (scenario pessimistico)
- Rischi e fattori di incertezza
- Azioni di mitigazione previste
- Fattibilità temporale del piano

{self.formatting_rules}

Analizza l'andamento MENSILE con valori specifici per ogni mese."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def piano_creditori(self, table_data: list[list[str]], anno: int) -> dict[str, str]:
        """Prompt per analisi del Piano di Soddisfacimento Creditori"""
        table_str = self._format_table_for_prompt(table_data)

        user_prompt = f"""Analizza il Piano di Soddisfacimento Creditori per l'Anno {anno}:

DATI TABELLA:
{table_str}

Fornisci un'analisi professionale (500-600 parole) strutturata come segue:

1. PAGAMENTI PER CATEGORIA DI CREDITORE
Per ciascuna classe:
- Importo totale dovuto
- Importo riconosciuto nel piano
- Percentuale soddisfacimento
- Tempistica pagamento (mesi)

2. SCADENZIARIO DEI PAGAMENTI
- Calendario pagamenti mensile
- Distribuzione temporale esborsi
- Concentrazione pagamenti (picchi)
- Coerenza con flussi disponibili

3. TRATTAMENTO CREDITORI PREDEDUCIBILI
- Spese di procedura
- Compensi professionisti
- Altri crediti prededucibili
- Tempistica pagamento (prioritario)

4. TRATTAMENTO CREDITORI CONCORDATARI
- Creditori privilegiati: importi e tempi
- Creditori chirografari: falcidia e tempi
- Creditori non aderenti: pagamento integrale
- Logica di differenziazione

5. ANALISI CONVENIENZA E FATTIBILITÀ
- Confronto con percentuali da liquidazione
- Dimostrazione miglior soddisfacimento
- Copertura finanziaria impegni
- Margini di sicurezza
- Rischi e contingency plan

{self.formatting_rules}

Dettaglia i pagamenti per OGNI categoria con importi e tempistiche precise."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def conclusioni(self, dati_sintesi: dict[str, str]) -> dict[str, str]:
        """Prompt per le Conclusioni del Piano di Ristrutturazione"""
        dati_str = "\n".join(f"- {k}: {v}" for k, v in dati_sintesi.items())

        user_prompt = f"""Redigi le Conclusioni del Piano di Ristrutturazione dei Debiti (ADR Art. 57 CCII):

DATI CHIAVE DEL PIANO:
{dati_str}

Fornisci conclusioni professionali (600-700 parole) strutturate come segue:

1. SINTESI DELLA SITUAZIONE DI PARTENZA
- Stato di crisi dell'impresa (elementi oggettivi)
- Principali squilibri economico-patrimoniali-finanziari evidenziati
- Cause della crisi identificate
- Perimetro e gravità della situazione

2. STRATEGIA DI RISANAMENTO ADOTTATA
- Scelta dello strumento (ADR ex art. 57 CCII)
- Logica dell'intervento proposto
- Azioni correttive sulla struttura economica
- Rettifiche patrimoniali applicate (attivo e passivo)
- Nuovo equilibrio patrimoniale raggiunto

3. SOSTENIBILITÀ DEL PIANO ECONOMICO-FINANZIARIO
- Capacità di generazione di cassa dimostrata
- Adeguatezza flussi vs impegni
- Coerenza temporale del piano
- Margini di sicurezza previsti

4. SODDISFACIMENTO DEI CREDITORI
- Percentuali di soddisfacimento per categoria
- Confronto con scenario liquidatorio alternativo
- Dimostrazione del miglior soddisfacimento
- Trattamento equo delle diverse classi

5. CONVENIENZA E FATTIBILITÀ
- Vantaggi per i creditori vs liquidazione
- Preservazione continuità aziendale
- Salvaguardia livelli occupazionali
- Fattibilità tecnica ed economica dimostrata

6. RACCOMANDAZIONI CONCLUSIVE
- Richiesta di approvazione del piano
- Elementi a supporto dell'omologazione
- Impegni assunti dall'impresa
- Garanzie offerte ai creditori
- Monitoraggio previsto

{self.formatting_rules}

Tono: professionale, oggettivo ma persuasivo.
Obiettivo: convincere il Tribunale della validità del piano.
Includi riferimenti numerici chiave a supporto delle conclusioni."""

        return {
            "system": self.base_system,
            "user": user_prompt,
        }

    def get_prompt(self, prompt_type: str, **kwargs: object) -> dict[str, str]:
        """
        Metodo generico per ottenere un prompt per tipo.

        Args:
            prompt_type: tipo di prompt (analisi_economica, stato_patrimoniale, ecc.)
            **kwargs: parametri specifici per il tipo di prompt

        Returns:
            dict con 'system' e 'user' prompt
        """
        prompt_methods = {
            "analisi_economica": self.analisi_economica,
            "analisi_finanziaria": self.analisi_finanziaria,
            "stato_patrimoniale": self.stato_patrimoniale,
            "posizione_finanziaria_netta": self.posizione_finanziaria_netta,
            "rettifiche_attivo": self.rettifiche_attivo,
            "rettifiche_passivo": self.rettifiche_passivo,
            "piano_flussi": self.piano_flussi,
            "piano_creditori": self.piano_creditori,
            "conclusioni": self.conclusioni,
        }

        method = prompt_methods.get(prompt_type)
        if not method:
            raise ValueError(f"Tipo prompt non supportato: {prompt_type}")

        return method(**kwargs)  # type: ignore[arg-type]
