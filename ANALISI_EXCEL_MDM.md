# Analisi Funzionale - MDM Accordi di Ristrutturazione Debiti

## Panoramica

Il file Excel "MDM - Accordi di ristrutturazione debiti cont_indiretta.xlsx" e' uno strumento professionale per la gestione di procedure di ristrutturazione del debito aziendale (Accordi di Ristrutturazione dei Debiti - AdR, ex art. 182-bis L.F., ora artt. 57 e ss. CCII).

Il modello parte dal bilancio contabile dell'azienda in crisi, lo riclassifica, applica rettifiche all'attivo e al passivo, simula lo scenario di Liquidazione Giudiziale (LG) come benchmark, costruisce un piano concordatario/di ristrutturazione con proiezioni mensili (CE, SP, Cash Flow, Banca), e prepara i dati per la generazione di una relazione tramite AI.

**37 fogli**, organizzati in 7 aree funzionali:

---

## 1. CONFIGURAZIONE E ANAGRAFICA

### 1.1 Programma
- Foglio di pianificazione interna (agenda riunioni)
- Non funzionale per il sistema

### 1.2 MENU
- Parametri globali del modello
- **Data chiave**: data dell'ultima situazione contabile (cella B1)
- Identificativo azienda (B4: "AZIENDA 1")
- Elenco navigazione fogli

### 1.3 BCTool (Business Configuration Tool)
- Configurazione tecnica del modello
- Mappa ogni tipo di dato (CE, SP, Budget, Forecast, ecc.) al foglio di destinazione, colonna e riga di inserimento
- Parametri:
  - `J16`: Numero situazioni contabili infra-annuali (max 12)
  - `L17`: Nome modello ("Modello AdR")
  - `L18`: Gestione multiaziendale - numero aziende (1)
  - Supporto fino a N-4 esercizi storici (CE e SP)

### 1.4 SW_SP_CONTI - Piano dei Conti SP (116 conti)
- **Struttura**: Codice (5 cifre) | Descrizione | Categoria
- **Categorie attivo**: IMMOBILIZZAZIONI FINANZIARIE (10100-10800), IMMOBILIZZAZIONI IMMATERIALI (10900-11800, 11500), IMMOBILIZZAZIONI MATERIALI (11600-12400), RIMANENZE (20100-20600), IMMOBILIZZAZIONI LEASING (20200), CREDITI (30100-32500), LIQUIDITA' (32600-32800), RATEI E RISCONTI (32400-32500)
- **Categorie passivo**: FONDI (40000-40800), F.DO AMM.TO IMM.NI IMMATERIALI (50100-50700), F.DO AMM.TO IMM.NI MATERIALI (50200-51200), RISERVE (60000-60600), CAPITALE (60100), UTILE PERDITA ESERCIZIO (60700), UTILE PERDITA A NUOVO (60800), CREDITI X AUMENTO CAPITALE (60900), DEBITI (70000-72800)

### 1.5 SW_CE_CONTI - Piano dei Conti CE (161 conti)
- **Struttura**: Codice (6 cifre) | Descrizione | Categoria
- **Categorie**: RICAVI (501000-512000, 690000, 693000, 698000, 823000, 825000), RIMANENZE PF (550000-557000), RIMANENZE MP (558000-569000), CAPITALIZZAZIONE COSTI (570000-571000), MATERIE PRIME E MERCI (601000-606000, 653000, 689000), SERVIZI (650000-698000), GODIMENTO BENI TERZI (700000-711000), ONERI DIVERSI DI GESTIONE (708000-811000), COSTI PERSONALE (750000-758000), AMMORTAMENTI IMMATERIALI (770000-782000), AMMORTAMENTI MATERIALI (790000-796000), ACCANTONAMENTI (800000-801000), PROVENTI STRAORDINARI (820000-824000), ONERI STRAORDINARI (830000-853000), PROVENTI FINANZIARI (840000-843000), ONERI FINANZIARI (850000-854000), IMPOSTE (860000-862000)

---

## 2. DATA INGESTION (Fogli SW_*)

### 2.1 SW_SP_BIL-01 / SW_CE_BIL-01 (618/657 righe x 20 colonne)
- **Scopo**: Bilanci consuntivi SP e CE riclassificati per PdC
- Accolgono i dati storici (fino a 5 esercizi: N, N-1, N-2, N-3, N-4) nelle colonne E-T
- Ogni riga corrisponde a un conto del PdC
- Colonna B: codice conto, C: sottoconto, D: descrizione

### 2.2 SW_SP_REP-01 / SW_CE_REP-01 (3 righe x 21 colonne)
- Riassuntivi di SP e CE
- Colonna T contiene i totali piu' recenti usati dal foglio Raccordo

### 2.3 SW_FOR_TRI_OF-01 / SW_FOR_TRI_QC-01 (588/689 righe x 62 colonne)
- **Previsionali debiti tributari**: Oneri Finanziari (OF) e Quote Capitale (QC)
- Dettaglio per singola posizione tributaria con piano di rateizzazione
- 62 colonne = timeline mensile (circa 5 anni)

### 2.4 SW_FOR_FIN_OF-01 / SW_FOR_FIN_QC-01 (555/649 righe x 62 colonne)
- **Previsionali finanziamenti**: Oneri Finanziari e Quote Capitale
- Dettaglio per singolo finanziamento bancario
- Struttura analoga ai fogli tributari

### 2.5 SW_FORECAST-01 (128 righe x 62 colonne)
- Previsionali economici (CE proiezione)
- 62 colonne = timeline mensile

### 2.6 SW_BUDGET-01 (3 righe x 14 colonne)
- Budget annuale sintetico

---

## 3. RACCORDO E RICLASSIFICA

### 3.1 Riclassificato con Piano crisi (117 righe x 5 colonne)
- **Scopo**: Mappatura di ogni conto del PdC alla voce di bilancio dell'analisi di crisi
- Colonne A-C: linkate a SW_SP_CONTI (codice, descrizione, categoria originale)
- Colonna D: voce Attivo di destinazione (es. "Clienti", "Immobilizzazioni materiali", "Liquidita' immediate", "Crediti verso altri", "Rimanenze", etc.)
- Colonna E: voce Passivo di destinazione (es. "Banche - c/c passivi", "Debiti v/Fornitori", "Fondi e Rischi", "Capitale", "Riserve", etc.)
- **Funzione chiave**: e' il "dizionario di raccordo" che traduce il PdC aziendale nelle voci strutturate del piano di crisi

### 3.2 Raccordo (126 righe x 10 colonne)
- **Scopo**: Ponte tra bilancio importato e struttura di analisi
- Colonne:
  - A: Input (Attivo/Passivo)
  - B: Conto riclassificato (da SW_SP_REP-01)
  - C: Conto importato (da SW_SP_REP-01)
  - D: Descrizione
  - E: Riclassifica PdC (XLOOKUP su SW_SP_BIL-01)
  - F: Voce Attivo (VLOOKUP su "Riclassificato con Piano crisi")
  - G: Voce Passivo (VLOOKUP su "Riclassificato con Piano crisi")
  - H: Importo (SUMIF su SW_SP_REP-01 colonna T)
  - I: Rettifiche (manuale)
  - J: Valore netto = H + I
- **Formula chiave**: `=SUMIF('SW_SP_REP-01'!C:C,$C2,'SW_SP_REP-01'!T:T)` -- aggrega per sottoconto

### 3.3 Input (126 righe x 8 colonne)
- Foglio parametri di configurazione della pratica
- Contiene:
  - D9: Anno iniziale
  - D10: Mese iniziale
  - Parametri per le proiezioni

---

## 4. ANALISI ATTIVO E PASSIVO (Core del modello)

### 4.1 Attivo (319 righe x 77 colonne)
- **Scopo**: Dettaglio analitico di OGNI voce dell'attivo con rettifiche per il piano di crisi
- **Struttura per voce** (es. Clienti, righe 8-17):
  - Colonna A: Nome creditore/voce (es. "Cliente 1", "Cliente 2"...)
  - Colonna B: Saldo contabile (formula `=SUMIF(Raccordo!F:F,$A8,Raccordo!J:J)`)
  - Colonna C: Cessioni
  - Colonna D: Banca (nome banca per compensazione)
  - Colonna E: Compensazioni
  - Colonna F: Fornitore (nome fornitore per compensazione)
  - Colonna G: Rettifiche economiche
  - Colonna H: Rettifica patrimoniale
  - Colonna I: F.do Svalutazione (es. `=-B9*15%` per crediti, `=-B15*80%` per inesigibili)
  - Colonna J: Totale rettifiche = `C+E+H+I+G`
  - Colonna K: Attivo rettificato = `B+J`
  - Colonna L: Flag "Continuita'/Realizzo" (per immobilizzazioni e rimanenze)
  - Colonna M: Note
  - Colonna Q: Percentuale rettifica per immobilizzazioni (formula `=(B+J)*(1+Q)`)

- **Voci trattate** (ciascuna con sotto-dettaglio per singolo soggetto):
  1. **Liquidita' immediate** (r.5-7): Depositi bancari, Cassa
  2. **Clienti** (r.8-17): Fino a 8 clienti, svalutazione % variabile
  3. **Fatture da Emettere** (r.18-27): Dettaglio per soggetto
  4. **Crediti verso altri** (r.28-38): Svalutazione 50%
  5. **Anticipo da Fornitori** (r.39-42)
  6. **Fornitori NC da Ricevere** (r.43-46)
  7. **Crediti v/Imprese controllate** (r.47-50)
  8. **Crediti v/Imprese collegate** (r.51-54)
  9. **Crediti v/Imprese controllanti** (r.55-58)
  10. **Crediti v/Societa' del Gruppo** (r.59-62)
  11. **Credito IVA** (r.63-66): compensato con debito IVA
  12. **Crediti Tributari** (r.67-70): compensato con debiti tributari
  13. **Crediti verso Soci** (r.71-74)
  14. **Crediti vs Enti Previdenziali** (r.75-78)
  15. **Crediti vs Dipendenti** (r.79-82)
  16. **Ratei Attivi** (r.83-86)
  17. **Risconti Attivi** (r.87-90)
  18. **Rimanenze** (r.92-97): MP, semilavorati, PF, PF obsoleti -- con flag Continuita'/Realizzo e % rettifica
  19. **Immobilizzazioni immateriali** (r.99-104): Con flag Continuita'/Realizzo e % rettifica
  20. **Immobilizzazioni materiali** (r.105-113): Con flag Continuita'/Realizzo e % rettifica
  21. **Immobilizzazioni finanziarie** (r.114-120): Titoli, partecipazioni, crediti a lungo termine

- **Logica compensazioni**: I crediti possono essere compensati con debiti verso le stesse controparti (Banca o Fornitore), riducendo sia attivo che passivo

### 4.2 Passivo (122 righe x 13 colonne)
- **Scopo**: Dettaglio analitico di OGNI voce del passivo con rettifiche
- **Struttura per voce** (es. Banche c/c passivi, righe 6-17):
  - Colonna A: Nome creditore
  - Colonna B: Saldo contabile (formula `=-SUMIF(Raccordo!G:G,$A6,Raccordo!J:J)`)
  - Colonna C: Incrementi
  - Colonna D: Decrementi (compensazioni da Attivo: `=SUMIF(Attivo!$D$9:$D$17,Passivo!$A7,Attivo!$C$9:$C$17)+...`)
  - Colonna E: Compensato = C + D
  - Colonna F: Fondo rischi
  - Colonna G: Sanzioni e Accessori
  - Colonna H: Interessi
  - Colonna I: Totale rettifiche = E+F+G+H
  - Colonna J: Passivo rettificato = B+I
  - Colonna K: Tipologia creditore (lookup su Passivo_Tipologie)
  - Colonna M: Classe creditore (VLOOKUP su Passivo_Tipologie per Aderente/Non Aderente)

- **Voci trattate**:
  1. **Banche c/c passivi** (r.6-17): Fino a 12 banche, con compensazioni automatiche da Attivo
  2. **Debiti v/Fornitori** (r.18-25): Fino a 7 fornitori, con compensazioni
  3. **Debito IVA** (r.26-30)
  4. **Debiti Previdenziali** (r.31-35): Include rateizzazioni
  5. **Debiti v/Dipendenti** (r.36-40): Stipendi, ratei, TFR
  6. **Debiti Tributari** (r.41-45): Rateizzazioni, IRES/IRAP, Ritenute
  7. **Debiti v/altri Finanziatori** (r.46-50)
  8. **Banche - Finanziamenti** (r.51-55)
  9. **Altri debiti** (r.56-64)
  10. **Ratei e Risconti Passivi** (r.65-70)
  11. **Fondi e Rischi** (r.71-77)
  12. **Fondo TFR** (r.78-80)
  13. **Fondi Ammortamento** (r.81-83): Materiale e Immateriale
  14. **Fondo svalutazione partecipazioni** (r.84-86)
  15. **Patrimonio Netto** (r.87-95): Capitale, Riserve, Risultato esercizio

- **Formula quadratura**: `B99 = Attivo!B122 - Passivo!B96`

### 4.3 Passivo_Tipologie (28 righe x 7 colonne)
- **Scopo**: Classificazione dei creditori per il piano concordatario
- **Due sezioni**:
  - **Non Aderenti** (r.5-14): Fino a 10 tipologie
    - Classe: "Non Aderente Scaduto" o "Non Aderente non Scaduto"
    - Specifica: dettaglio (es. "XXX", "YYY")
    - Codice ordinamento (0_1, 0_2...)
    - Label composta: `=D5&"_"&B5&" _ "&C5`
  - **Aderenti** (r.19-28): Fino a 10 tipologie
    - Classe: "Aderenti"
    - Specifica: es. "Accollato"
- Usato dal foglio Passivo per assegnare ogni creditore a una classe (colonna K -> VLOOKUP)

---

## 5. SCENARI E SIMULAZIONE

### 5.1 Hp Liquidazione Giudiziale (57 righe x 13 colonne)
- **Scopo**: Simulazione dello scenario di Liquidazione Giudiziale come benchmark di confronto
- **Struttura**:
  - **Sezione A - Realizzo Attivo** (r.6-11):
    - Azienda (valore going concern)
    - Cespiti (ripartiti su 3 masse immobiliari + massa mobiliare)
    - Partecipazioni
    - Crediti
    - Disponibilita' liquide (da `Attivo!K8`)
  - **Sezione B - Azioni recuperatorie** (r.13-18):
    - Azioni revocatorie (fino a 4)
    - Azione di responsabilita'
  - **Totale A+B** = Valore di liquidazione
  - **Percentuali per massa**: `H21 = H20/$F$20` (ripartizione % del totale per massa)
  - **Sezione C - Prededuzioni** (r.25-30):
    - Compenso Curatela: `=E25*1.04*1.22` (+ cassa prev. 4% + IVA 22%)
    - Compenso Coadiutori, Imposte, Varie
    - Ripartite proporzionalmente per massa
  - **Residuo attivo** = (A+B) - C
  - **Creditori ipotecari** (r.34-37): Per grado e per massa immobiliare
    - Calcolo cascata: 1o grado soddisfatto per primo, 2o grado su residuo
    - Degradazione a chirografo se massa insufficiente
  - **Creditori privilegiati** (r.44-48): In ordine di legge
    - 001_Dipendenti, 002_Professionisti, 003_Fornitori, 004_Erario, 005_INPS
    - Cascata: `L44=K42+K44`, `L45=L44+K45`...
    - Calcolo % soddisfazione erario: `M47=L46/-K47`
  - **Creditori chirografari** (r.53-57): Residuo dopo privilegiati

### 5.2 Test_Piat (31 righe x 10 colonne)
- **Scopo**: Test pratico per la verifica della ragionevole perseguibilita' del risanamento
- **Sezione A** (r.7-15): Fabbisogno finanziario
  - Debito scaduto + iscrizioni a ruolo
  - Debito riscadenziato e moratorie
  - Linee di credito bancarie in scadenza
  - Rate mutui/finanziamenti nei successivi 2 anni
  - Investimenti per iniziative industriali
  - Meno: risorse da dismissioni (da `'Gestione e Proposta concordatar'!H7`)
  - Meno: nuovi conferimenti
  - Meno: MON negativo primo anno
  - **Totale A**
- **Sezione B** (r.18-21): Capacita' di rimborso
  - MOL prospettico normalizzato a regime (da CE-mese)
  - Meno: investimenti di mantenimento
  - Meno: imposte
  - **Totale B**
- **Rapporto A/B** (r.26): `=IFERROR(F15/F21,"NA")`
- **Interpretazione**:
  - < 2: difficolta' contenuta
  - 2-4: risanamento dipende da iniziative industriali
  - 4-6: MOL positivo insufficiente, necessaria cessione azienda
  - MOL < 0: disequilibrio economico a regime

### 5.3 Piano concordatario (22 righe x 8 colonne)
- Riepilogo per tipologia creditore
- Attivo da liquidare
- Piano: Attivo da liquidazione vs Passivo in ordine
- Proposta: Prelazione vs Gestione

### 5.4 PreDeduzione (33 righe x 131 colonne)
- **Scopo**: Dettaglio costi della procedura su timeline mensile (131 colonne = ~10 anni)
- **Spese di procedura** (r.7-14):
  - Advisor legale, Advisor finanziario, Attestatore, Perizia azienda
  - Formula: `=(Imponibile + Cassa_Prev_4%) * (1 + IVA_22%)`
- **Fondo spese di funzionamento** (r.17-28):
  - Assistenza contabile, Liquidazione societa', IMU, TASI, Assicurazioni, Contingenze, Sindaci, Revisori
  - Importi annuali distribuiti su colonne mensili
- Totale in riga 29

### 5.5 Gestione e Proposta concordataria (60 righe x 130 colonne)
- **Scopo**: Gestione del piano e proposta ai creditori
- Timeline mensile su ~130 colonne
- Contiene:
  - Dismissioni attivo
  - Gestione corrente
  - Proposta di soddisfazione per classe di creditori

---

## 6. PROIEZIONI MENSILI

### 6.1 CE-mese - Conto Economico Mensile (78 righe x 137 colonne)
- **Scopo**: Proiezione mensile del CE su ~11 anni (137 colonne)
- **Struttura**:
  - r.3-4: Anno e mese (da SP-mese)
  - r.5: **Fatturato**
  - r.7: Costi di Acquisto
  - r.8: Variazione Rimanenze
  - r.9: **Costo del Venduto** = Acquisti - Var. Rimanenze
  - r.11: **1o Margine di Contribuzione** = Fatturato - CdV
  - r.12: Margine % = `IFERROR(MC1/Fatturato,"na")`
  - r.14: Costi Variabili
  - r.16: **2o Margine di Contribuzione** = MC1 - Costi Variabili
  - r.18-37: **Costi di Gestione** (fino a 20 voci, linkate al CE aziendale)
  - r.38: Totale Costi Gestione
  - r.41-44: **Ammortamenti** (Materiali da bilancio, Immateriali da bilancio, Nuovi materiali, Nuovi immateriali)
  - r.45: Totale Ammortamenti
  - r.48-49: **Costi del Personale** (dipendenti + accantonamento TFR)
  - r.50: Totale Personale
  - r.52: Accantonamento Rischi Crediti
  - r.54: **Reddito Operativo** = MC2 - Costi Gestione - Ammortamenti - Personale - Acc.Rischi
  - r.55: % Reddito Operativo
  - r.57-58: **Gestione Finanziaria** (OF preammortamento + OF finanziamento)
  - r.62: **Reddito Ante Imposte** = EBIT - Gestione Finanziaria
  - r.65-66: **Imposte** (IRES + IRAP)
  - r.69: **Reddito Netto** = Reddito Ante Imposte - Imposte

### 6.2 SP-mese - Stato Patrimoniale Mensile (89 righe x 123 colonne)
- **Scopo**: Proiezione mensile dello SP su ~10 anni
- **Struttura Attivo**:
  - r.3-4: Anno e mese (da Input!D9, D10; poi formula incrementale `=IF(C4=12,1,C4+1)`)
  - r.5: **Cassa e Banca** (positiva) = `IF('Banca-mese'!C45>0,...)`
  - r.7-12: **Crediti esigibili**: Clienti, Enti Prev., Erario, IVA, Altri
  - r.14-16: **Rimanenze** (da bilancio con flag Continuita' + nuove)
  - r.18-31: **Immobilizzazioni Materiali**: Da bilancio (SUMIF con flag "Continuita'" da Attivo), decrementate degli ammortamenti mensili, + nuove immobilizzazioni, + dettaglio Fabbricati, Impianti con relativi f.di amm.to
  - r.33-43: **Immobilizzazioni Immateriali**: Stessa logica
  - r.45-47: **Immobilizzazioni Finanziarie**: Da bilancio + variazioni da foglio "Imm fin"
  - r.49: **Totale Attivo**
- **Struttura Passivo**:
  - r.51: Cassa e Banca (negativa/scoperto)
  - r.53-65: **Debiti Correnti**: Fornitori (commerciali + immobilizzazioni), Dipendenti, Contributi, IVA, Tributari, Altri
  - r.67-74: **Debiti m/l termine**: Mutui, TFR, Altri Fondi, Altri finanziamenti
  - r.76-83: **Capitale Netto**: Capitale Sociale, Riserva Legale, Altre Riserve, Utile a nuovo, Risultato esercizio (da CE-mese)
  - r.86: **Totale Passivo**
  - r.88-89: **Check** = Totale Attivo - Totale Passivo (deve essere 0)

### 6.3 Cflow-mese - Rendiconto Finanziario Mensile (64 righe x 133 colonne)
- **Scopo**: Cash flow indiretto mensile
- **Struttura** (metodo indiretto OIC 10):
  - **A. Gestione reddituale**:
    - r.5: Utile/perdita (da CE-mese r.69)
    - r.6: Imposte (da CE-mese r.67)
    - r.7: Interessi passivi (da CE-mese r.59)
    - r.9: Reddito Operativo = SUM
    - r.11: Accantonamenti TFR (da CE-mese r.49)
    - r.12: Ammortamenti (da CE-mese r.45)
    - r.13: Flusso prima variazioni CCN
    - r.16-19: **Variazioni CCN**: Delta rimanenze (SP t vs SP t+1), Delta crediti clienti, Delta debiti fornitori, Altre variazioni
    - r.20: Flusso dopo variazioni CCN
    - r.22: Imposte pagate (rettifica per competenza/cassa)
    - r.23: Utilizzo fondi
    - r.26: **FCFO (Flusso gestione reddituale A)**
  - **B. Attivita' di investimento**:
    - r.30-31: Investimenti immobilizzazioni materiali (delta SP al netto ammortamenti)
    - r.33-34: Investimenti immobilizzazioni immateriali
    - r.36-37: Investimenti immobilizzazioni finanziarie
    - r.40: **Flusso investimenti B**
  - **C. Attivita' di finanziamento**:
    - r.44-50: Mezzi di terzi: Accensione/rimborso finanziamenti, Fornitori cespiti, Oneri finanziari
    - r.52-54: Mezzi propri: Aumento capitale, Dividendi
    - r.56: **Flusso finanziamento C**
  - r.58: **Variazione liquidita'** = A + B + C
  - r.60-61: Disponibilita' liquide inizio/fine periodo
  - r.64: **Check** = Liquidita' fine periodo - Saldo Banca (deve essere 0)

### 6.4 Banca-mese - Flussi di Cassa Diretti (64 righe x 133 colonne)
- **Scopo**: Simulazione del conto corrente bancario mese per mese
- **Entrate** (r.6-12):
  - Incasso clienti
  - Capitale sociale
  - Finanziamento soci
  - Finanziamento banca
  - Altri incassi
- **Uscite** (r.17-38):
  - Costi variabili, Acquisti, Fornitori immobilizzazioni
  - Dipendenti, Contributi, Utilizzo TFR, Utilizzo altri fondi
  - Costi gestione, Altre uscite
  - Liquidazione IVA, Canone leasing
  - Rimborso finanziamenti bancari e soci
  - Oneri finanziari (preammortamento + finanziamento)
  - Pagamento IRES, IRAP
  - Debiti tributari, previdenziali, IVA
  - Immobilizzazioni finanziarie, Distribuzione utile
- r.42: **Flusso finanziario** = Entrate - Uscite
- r.44: **Saldo iniziale** (= saldo finale mese precedente)
- r.45: **Saldo finale** = Saldo iniziale + Flusso
  - Valore iniziale: `='SP-mese'!C5` (cassa da bilancio)
- r.48: **Check** vs Cflow-mese (deve essere 0)

### 6.5 Imm fin - Immobilizzazioni Finanziarie (25 righe x 125 colonne)
- Dettaglio fino a 20 immobilizzazioni finanziarie
- Variazioni mensili (acquisti/vendite) su timeline
- Totale per colonna alimenta SP-mese r.47

### 6.6 C_Azienda - Cessione Azienda (37 righe x 125 colonne)
- **Scopo**: Simulazione cessione/vendita azienda o ramo d'azienda
- Importo lordo, accolli (TFR, Fornitori, etc.)
- Importo netto = Lordo - Accolli
- Parametri: Mese e Anno vendita
- Formula distribuzione: `=IF(mese=MeseVendita AND anno=AnnoVendita, ImportoNetto, 0)`

### 6.7 Affitto - Affitto d'Azienda (10 righe x 125 colonne)
- Canone mensile + IVA
- Gestione dilazione incasso (0/30/60/90 gg)
- Formula incasso con shift temporale

### 6.8 L_Iva - Liquidazione IVA (35 righe x 126 colonne)
- **Scopo**: Calcolo mensile della liquidazione IVA
- IVA a debito (da vendite/affitto)
- IVA a credito (da acquisti + credito iniziale da Attivo)
- Saldo mensile, riporto credito, liquidazione
- Pagamento con ritardo di un mese
- Impatto su SP (variazione credito/debito IVA)

### 6.9 I_Ult CE - Ultimo CE (63 righe x 5 colonne)
- Template per importare l'ultimo conto economico
- Struttura identica a CE-mese ma per singolo periodo
- Link ai nomi conti di CE-mese

---

## 7. OUTPUT E REPORTING

### 7.1 CRUSCOTTO - Dashboard (37 righe x 12 colonne)
- **Scopo**: Vista sintetica su 10 periodi
- **Sezione CE** (r.3-8): Fatturato, MC1, MC2, Reddito Operativo, Reddito Netto (da CE-mese)
- **Sezione Flussi** (r.10-15): Totale Entrate, Totale Uscite, Flusso Finanziario, Saldo iniziale/finale (da Banca-mese)
- **Sezione DSCR** (r.18-21): Debt Service Coverage Ratio
  - FCFO / Flusso Servizio Debito
  - Formula: `=IFERROR(FCFO/FlussoServizioDebito, "na")`
- **Sezione SP** (r.24-36): Attivo (Cassa, Crediti, Rimanenze, Imm.Mat, Imm.Immat, Imm.Fin) e Passivo (Debiti correnti, Debiti m/l, Fondi, PN)
  - Totale Attivo = SUM, Totale Passivo = SUM

### 7.2 Relazione_AI (186 righe x 18 colonne)
- **Scopo**: Preparazione dati strutturati per generazione relazione tramite AI
- **Tabella 1 - Attivo** (r.2-27): Tutte le voci dell'attivo rettificato con colonne Contabile, Rettifiche (Cessioni, Compensazioni, Rettifiche economiche, Patrimoniali, F.do Svalutazione), Totale rettifiche, Attivo rettificato - tutto linkato al foglio Attivo
- **Tabella 2 - Passivo** (r.29-48): Tutte le voci del passivo rettificato con colonne Contabile, Incrementi, Decrementi, Compensato, Fondo rischi, Sanzioni, Interessi, Totale rettifiche, Passivo rettificato - tutto linkato al foglio Passivo
- **Tabella 3 - Tipologie Passivo Non Aderenti** (r.52-65): Da Passivo_Tipologie
- **Tabella 4 - Tipologie Passivo Aderenti** (r.68-81): Da Passivo_Tipologie
- **Sezione Affitto d'Azienda** (r.84-91): Canoni, IVA, incassi mensili
- **Sezione PreDeduzione** (r.93-116): Spese di procedura e funzionamento
- **Sezione Cessione Azienda** (r.118-131): Dettaglio importi e accolli
- **Sezione Gestione Piano** (r.135+): Dati dal piano concordatario

---

## 8. FLUSSO DATI COMPLESSIVO

```
IMPORT                     RACCORDO                    ANALISI
+-----------+             +----------+              +----------+
| SW_SP_BIL |--bilancio-->| Raccordo |--saldi------>| Attivo   |
| SW_CE_BIL |             | (SUMIF + |              | (rettif.)|
+-----------+             | VLOOKUP) |              +----+-----+
                          +----+-----+                   |
+-----------+                  |                         v
| SW_SP_CONTI|--PdC--> Riclassificato        +----------+----------+
| SW_CE_CONTI|         con Piano crisi       | Passivo              |
+-----------+         (mapping A/P)          | (rettif.+compensaz.) |
                                             +----------+----------+
                                                        |
PARAMETRI                SCENARI                        v
+-----------+          +----------+            +--------+--------+
| Input     |--data--->| Hp LG    |            | Piano concordat.|
| BCTool    |          | Test_Piat|            | Passivo_Tipol.  |
+-----------+          +----------+            +---------+-------+
                                                        |
PROIEZIONI MENSILI                                      v
+--------+    +--------+    +---------+        +--------+--------+
| CE-mese|<-->| SP-mese|<-->|Cflow-mes|<------>| Banca-mese     |
+---+----+    +---+----+    +---------+        +--------+-------+
    |             |                                      |
    |    +--------+--------+                             |
    |    | Imm fin         |                             |
    |    | C_Azienda       |                             |
    |    | Affitto         |                             |
    |    | L_Iva           |                             |
    |    | PreDeduzione    |                             |
    |    +-----------------+                             |
    |                                                    |
    v                                                    v
+---+--------------------------------------------+------+--+
| CRUSCOTTO (Dashboard sintetica)                           |
+---+-------------------------------------------------------+
    |
    v
+---+-------------------------------------------------------+
| Relazione_AI (Tabelle strutturate per generazione AI)     |
+-----------------------------------------------------------+
```

---

## 9. FORMULE CHIAVE E PATTERN

### 9.1 Aggregazione da bilancio a voci di crisi
```
Attivo!B8 = SUMIF(Raccordo!F:F, $A8, Raccordo!J:J)
Passivo!B6 = -SUMIF(Raccordo!G:G, $A6, Raccordo!J:J)
```
Il segno negativo nel Passivo converte la convenzione contabile (passivo negativo) in valori positivi.

### 9.2 Rettifica attivo con % svalutazione
```
Attivo!I9 = -B9 * 15%              -- Svalutazione crediti 15%
Attivo!K93 = (B93+J93) * (1+Q93)   -- Rettifica rimanenze con % in colonna Q
```

### 9.3 Compensazioni attivo-passivo
```
Passivo!D7 = SUMIF(Attivo!$D$9:$D$17, Passivo!$A7, Attivo!$C$9:$C$17)
           + SUMIF(Attivo!$D$19:$D$27, Passivo!$A7, Attivo!$C$19:$C$27)
           + SUMIF(Attivo!$F$115:$F$120, Passivo!$A7, Attivo!$F$115:$F$120)
```
Cerca il nome della banca/fornitore nell'attivo e porta la compensazione al passivo.

### 9.4 Classificazione creditori
```
Passivo!M7 = IFERROR(VLOOKUP(K7, Passivo_Tipologie!$E$5:$G$28, 3, FALSE), "")
```

### 9.5 Liquidazione giudiziale - cascata
```
Hp LG!F32 = F20 + F30                    -- Residuo = Realizzo - Prededuzioni
Hp LG!H35 = -(H32+H34)                  -- 2o grado = -(Residuo + 1o grado)
Hp LG!L44 = K42 + K44                   -- Residuo dopo privilegiati
Hp LG!M47 = L46 / -K47                  -- % soddisfazione erario
```

### 9.6 Timeline mensile
```
SP-mese!C3 = Input!D9                    -- Anno iniziale
SP-mese!D3 = IF(D4=1, C3+1, C3)         -- Incremento anno al cambio gen
SP-mese!C4 = Input!D10                   -- Mese iniziale
SP-mese!D4 = IF(C4=12, 1, C4+1)         -- Incremento mese ciclico
```

### 9.7 DSCR
```
CRUSCOTTO!C21 = IFERROR(C19/C20, "na")  -- FCFO / Servizio debito
```

### 9.8 Ammortamento immobilizzazioni nel piano
```
SP-mese!D18 = C18 - 'CE-mese'!C41       -- Imm.Mat t+1 = Imm.Mat t - Amm.Mat
```

### 9.9 Cassa banca con split +/-
```
SP-mese!D5 = IF('Banca-mese'!C45 > 0, 'Banca-mese'!C45, 0)   -- Attivo
SP-mese!D51 = IF('Banca-mese'!C45 < 0, -'Banca-mese'!C45, 0)  -- Passivo
```

---

## 10. REQUISITI PER IL SISTEMA WEB

### 10.1 Moduli da implementare

| # | Modulo | Fogli Excel | Priorita' |
|---|--------|-------------|-----------|
| 1 | **Piano dei Conti** | SW_SP_CONTI, SW_CE_CONTI | Alta |
| 2 | **Import Bilancio** | SW_SP_BIL, SW_CE_BIL, SW_SP_REP, SW_CE_REP | Alta |
| 3 | **Raccordo/Riclassifica** | Raccordo, Riclassificato con Piano crisi | Alta |
| 4 | **Analisi Attivo** | Attivo | Alta |
| 5 | **Analisi Passivo** | Passivo, Passivo_Tipologie | Alta |
| 6 | **Hp Liquidazione Giudiziale** | Hp Liquidazione Giudiziale | Alta |
| 7 | **Test Perseguibilita'** | Test_Piat | Media |
| 8 | **Piano Concordatario** | Piano concordatario, Gestione e Proposta | Alta |
| 9 | **PreDeduzione** | PreDeduzione | Media |
| 10 | **Cessione Azienda** | C_Azienda | Media |
| 11 | **Affitto d'Azienda** | Affitto | Media |
| 12 | **CE Mensile** | CE-mese, I_Ult CE | Alta |
| 13 | **SP Mensile** | SP-mese | Alta |
| 14 | **Cash Flow Mensile** | Cflow-mese | Alta |
| 15 | **Banca Mensile** | Banca-mese | Alta |
| 16 | **Liquidazione IVA** | L_Iva | Media |
| 17 | **Immobilizzazioni Finanziarie** | Imm fin | Bassa |
| 18 | **Dashboard/Cruscotto** | CRUSCOTTO | Alta |
| 19 | **Relazione AI** | Relazione_AI | Alta |
| 20 | **Configurazione** | Input, MENU, BCTool | Media |

### 10.2 Input utente richiesti
1. Upload bilancio contabile (CSV/XLSX con PdC aziendale)
2. Upload XBRL (bilanci depositati)
3. Mappatura PdC aziendale -> voci di crisi (Riclassificato con Piano crisi)
4. Dettaglio per singolo creditore/debitore con rettifiche (fogli Attivo e Passivo)
5. Ipotesi di realizzo per LG (percentuali, tempi, costi procedurali)
6. Classificazione creditori (Aderenti/Non Aderenti, tipologie)
7. Parametri piano: canone affitto, prezzo cessione, accolli
8. Proiezioni CE mensili: fatturato, costi, personale, ammortamenti
9. Proiezioni finanziarie: entrate/uscite, finanziamenti, rate

### 10.3 Calcoli da replicare lato server
1. **SUMIF/VLOOKUP** per raccordo bilancio -> voci di crisi
2. **Rettifiche attivo**: cessioni, compensazioni, svalutazioni con % variabile
3. **Rettifiche passivo**: incrementi, decrementi, compensazioni incrociate con attivo
4. **Cascata LG**: realizzo -> prededuzioni -> ipotecari per massa -> privilegiati -> chirografari
5. **Test perseguibilita'**: rapporto fabbisogno/capacita' rimborso
6. **Proiezioni mensili**: CE completo con margini e subtotali
7. **SP mensile**: con ammortamento progressivo, variazioni CCN
8. **Cash flow indiretto**: riconciliazione con metodo OIC 10
9. **Banca diretta**: entrate/uscite con saldo progressivo
10. **Liquidazione IVA**: debito/credito mensile con riporto
11. **DSCR**: Debt Service Coverage Ratio per periodo
12. **Quadratura**: Attivo = Passivo, Cflow = Banca

### 10.4 Differenze rispetto all'implementazione attuale nel backend
Il backend attuale gestisce solo:
- Import TB e XBRL
- Riclassifica SP con longest-prefix match (semplificata)
- KPI base (tutti a 0)
- Aggregazione mensile base

**Mancano completamente**:
- Analisi Attivo con rettifiche per singolo creditore
- Analisi Passivo con compensazioni incrociate e classificazione creditori
- Scenario Liquidazione Giudiziale con cascata
- Test perseguibilita' risanamento
- Piano concordatario con tipologie creditori
- PreDeduzione e costi procedurali
- Proiezioni CE/SP/CFlow/Banca complete
- Cessione azienda e affitto d'azienda
- Liquidazione IVA
- Dashboard con DSCR
- Preparazione dati per Relazione AI
