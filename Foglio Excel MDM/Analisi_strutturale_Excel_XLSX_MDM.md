# Analisi strutturale del file Excel

**File:** MDM - Accordi di ristrutturazione debiti cont_indiretta.xlsx  
**Generato:** 2025-09-23 12:33

---

## Sintesi esecutiva

- **Numero fogli:** 37
- **Intervalli denominati:** 11 (alcuni duplicati)
- Il workbook funge da **staging + riclassifica** per dati **XBRL** e **contabili** verso uno schema di **Piano Crisi**; presenza di moduli per **budget/forecast**, **mensilità/dilazioni**, **IVA**, **prededuzioni**.
- La **mappatura** tra *conto importato* e *conto riclassificato/categoria* è esplicita (fogli **Raccordo** e **Riclassificato con Piano crisi**).
- Sono impiegate **validazioni** (liste) e **formule** diffuse; non risultano **Excel Tables** (ListObjects).

## Architettura logica e flusso

1. **Staging**: import di conti e bilancio (fogli `SW_*_CONTI`, `SW_*_BIL-01`, `SW_*_REP-01`).
2. **Mappatura**: ponte tra contabilità/XBRL e schema target (`Raccordo`).
3. **Riclassifica**: vista finale coerente con **Piano crisi** (`Riclassificato con Piano crisi`).
4. **Serie temporali / Scenari**: budget/forecast e mensilità/dilazioni (`SW_BUDGET-01`, `SW_FORECAST-01`, `SW_FOR_*`, `Banca-mese`, `SP-mese`).
5. **Moduli specialistici**: IVA (`L_Iva`), tipologie passivo/attivo (`Passivo_Tipologie`, `Attivo_Tipologie`), prededuzioni (`PreDeduzione`).

## Intervalli denominati (Named Ranges)

| Nome | Riferimento |
|---|---|
| elenco_gg_dilazione | #REF! |
| elenco_mensilita_anni_A_m | #REF! |
| elenco_mensilita_m | #REF! |
| tipologia_mensilita | #REF! |
| elenco_gg_dilazione | 'Riclassificato con Piano crisi'!#REF! |
| elenco_mensilita_anni_A_m | 'Riclassificato con Piano crisi'!#REF! |
| elenco_mensilita_m | 'Riclassificato con Piano crisi'!#REF! |
| elenco_gg_dilazione | #REF! |
| elenco_mensilita_anni_A_m | #REF! |
| elenco_mensilita_m | #REF! |
| tipologia_mensilita | #REF! |

> Noti duplicati di: `elenco_gg_dilazione`, `elenco_mensilita_anni_A_m`, `elenco_mensilita_m`, `tipologia_mensilita`.

## Fogli di mappatura (euristica)

**Riclassificato con Piano crisi** — colonne esemplificative:

- Conto
- Descrizione
- CATEGORIA
- Attivo
- Passivo

**Raccordo** — colonne esemplificative:

- Input
- CONTO RICLASSIFICATO
- CONTO IMPORTATO
- DESCRIZIONE
- Riclassifica PdC
- Attivo
- Passivo
- Importo
- Rettifiche
- Valore netto

## Fogli con struttura XBRL / concetti correlati (euristica)

**Programma** — colonne esemplificative:

- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4

**MENU** — colonne esemplificative:

- Unnamed: 0
- 2025-09-17 00:00:00

**BCTool** — colonne esemplificative:

- Unnamed: 0
- DEVAJH1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11

**SW_SP_CONTI** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3

**SW_CE_CONTI** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3

**SW_FOR_TRI_OF-01** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**SW_FOR_TRI_QC-01** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**SW_FOR_FIN_OF-01** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**SW_FOR_FIN_QC-01** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**SW_FORECAST-01** — colonne esemplificative:

- Descrizione
- Categoria
- 2025-10-31 00:00:00
- 2025-11-30 00:00:00
- 2025-12-31 00:00:00
- 2026-01-31 00:00:00
- 2026-02-28 00:00:00
- 2026-03-31 00:00:00
- 2026-04-30 00:00:00
- 2026-05-31 00:00:00
- 2026-06-30 00:00:00
- 2026-07-31 00:00:00
- 2026-08-31 00:00:00
- 2026-09-30 00:00:00
- 2026-10-31 00:00:00
- 2026-11-30 00:00:00
- 2026-12-31 00:00:00
- 2027-01-31 00:00:00
- 2027-02-28 00:00:00
- 2027-03-31 00:00:00

**SW_BUDGET-01** — colonne esemplificative:

- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13

**SW_SP_BIL-01** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**SW_CE_BIL-01** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**SW_SP_REP-01** — colonne esemplificative:

- MENU
- 0
- 0.1
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**SW_CE_REP-01** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**Input** — colonne esemplificative:

- 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7

**Hp Liquidazione Giudiziale** — colonne esemplificative:

- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12

**Relazione_AI** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15

**Test_Piat** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8

**Passivo_Tipologie** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6

**Piano concordatario** — colonne esemplificative:

- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7

**PreDeduzione** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**CRUSCOTTO** — colonne esemplificative:

- Unnamed: 0
- MENU
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11

**Imm fin** — colonne esemplificative:

- Equity 
- Unnamed: 1
- MENU
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**Attivo** — colonne esemplificative:

- MENU
- Dettaglio SP Attivo
- Formule
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**Passivo** — colonne esemplificative:

- MENU
- Dettaglio Passivo
- Formule
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10

**Gestione e Proposta concordatar** — colonne esemplificative:

- MENU
- input
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- ANNO DI PIANO
- 1
- 1.1
- 1.2
- 1.3
- 1.4
- 1.5
- 1.6
- 1.7
- 1.8
- 1.9
- 1.10

**C_Azienda** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- anno
- 2025
- 2025.1
- 2025.2
- 2026
- 2026.1
- 2026.2
- 2026.3
- 2026.4
- 2026.5
- 2026.6
- 2026.7
- 2026.8
- 2026.9
- 2026.10
- 2026.11

**Affitto** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- anno
- 2025
- 2025.1
- 2025.2
- 2026
- 2026.1
- 2026.2
- 2026.3
- 2026.4
- 2026.5
- 2026.6
- 2026.7
- 2026.8
- 2026.9
- 2026.10
- 2026.11

**CE-mese** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**Cflow-mese** — colonne esemplificative:

- MENU
- anno
- 2025
- 2025.1
- 2025.2
- 2026
- 2026.1
- 2026.2
- 2026.3
- 2026.4
- 2026.5
- 2026.6
- 2026.7
- 2026.8
- 2026.9
- 2026.10
- 2026.11
- 2027
- 2027.1
- 2027.2

**Banca-mese** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**SP-mese** — colonne esemplificative:

- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**L_Iva** — colonne esemplificative:

- Unnamed: 0
- MENU
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19

**I_Ult CE** — colonne esemplificative:

- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4

## Fogli con formule – esempi

- **SW_FOR_TRI_OF-01**: `=+EOMONTH(MENU!B1,1)`; `=+EOMONTH(C2,1)`; `=+EOMONTH(D2,1)`; `=+EOMONTH(E2,1)`; `=+EOMONTH(F2,1)`
- **SW_FOR_TRI_QC-01**: `=+EOMONTH(MENU!B1,1)`; `=+EOMONTH(C2,1)`; `=+EOMONTH(D2,1)`; `=+EOMONTH(E2,1)`; `=+EOMONTH(F2,1)`
- **SW_FOR_FIN_OF-01**: `=+EOMONTH(MENU!B1,1)`; `=+EOMONTH(C2,1)`; `=+EOMONTH(D2,1)`; `=+EOMONTH(E2,1)`; `=+EOMONTH(F2,1)`
- **SW_FOR_FIN_QC-01**: `=+EOMONTH(MENU!B1,1)`; `=+EOMONTH(C2,1)`; `=+EOMONTH(D2,1)`; `=+EOMONTH(E2,1)`; `=+EOMONTH(F2,1)`
- **SW_FORECAST-01**: `=+EOMONTH(MENU!B1,1)`; `=+EOMONTH(C1,1)`; `=+EOMONTH(D1,1)`; `=+EOMONTH(E1,1)`; `=+EOMONTH(F1,1)`
- **SW_SP_BIL-01**: `=+F3-1`; `=+G3-1`; `=+H3-1`; `=+YEAR(MENU!B1)-1`; `=+MENU!B1`
- **SW_CE_BIL-01**: `=+F3-1`; `=+G3-1`; `=+H3-1`; `=+YEAR(MENU!B1)-1`; `=+MENU!B1`
- **Riclassificato con Piano crisi**: `=SW_SP_CONTI!B2`; `=SW_SP_CONTI!C2`; `=SW_SP_CONTI!D2`; `=SW_SP_CONTI!B3`; `=SW_SP_CONTI!C3`
- **Raccordo**: `='SW_SP_REP-01'!B4`; `='SW_SP_REP-01'!C4`; `='SW_SP_REP-01'!D4`; `=_xlfn.XLOOKUP(B2,'SW_SP_BIL-01'!B:B,'SW_SP_BIL-01'!D:D)`; `=+IFERROR(VLOOKUP($B2,'Riclassificato con Piano crisi'!$A:$E,4,FALSE),"")`
- **Input**: `=+Passivo!B99`; `=YEAR(MENU!B1)`; `=MONTH(MENU!B1)`; `=+B114+1`; `=+B115+1`
- **Hp Liquidazione Giudiziale**: `=+F6`; `=+F8`; `=+F9`; `=+Attivo!K8`; `=+F10`
- **Relazione_AI**: `=+Attivo!B3`; `=+Attivo!C4`; `=+Attivo!E4`; `=+Attivo!G4`; `=+Attivo!H4`
- **Test_Piat**: `=-'Gestione e Proposta concordatar'!H7`; `=SUM(F7:F14)`; `=+'CE-mese'!DU54-'CE-mese'!DU52-'CE-mese'!DU45`; `=+SUMIF(#REF!,'CE-mese'!DU3,#REF!)`; `=+'CE-mese'!DU67`
- **Passivo_Tipologie**: `=D5& "_" & B5 & " _ " & C5`; `=+B5`; `=+A5+1`; `=D6& "_" & B6 & " _ " & C6`; `=+B6`
- **PreDeduzione**: `=MIN(L2:EA2)`; `='Gestione e Proposta concordatar'!J20`; `='Gestione e Proposta concordatar'!K20`; `='Gestione e Proposta concordatar'!L20`; `='Gestione e Proposta concordatar'!M20`
- **CRUSCOTTO**: `=C3-1`; `=+#REF!`; `=+#REF!`; `=+#REF!`; `=+#REF!`
- **Imm fin**: `=+#REF!`; `=+#REF!`; `=+#REF!`; `=+#REF!`; `=+#REF!`
- **Attivo**: `=+'Gestione e Proposta concordatar'!J3`; `=+'Gestione e Proposta concordatar'!K3`; `=+'Gestione e Proposta concordatar'!L3`; `=+'Gestione e Proposta concordatar'!M3`; `=+'Gestione e Proposta concordatar'!N3`
- **Passivo**: `=+Attivo!B3`; `=-SUMIF(Raccordo!G:G,$A6,Raccordo!J:J)`; `=+SUM(C7:C17)`; `=+SUM(D7:D17)`; `=+SUM(E7:E17)`
- **Gestione e Proposta concordatar**: `=+J1+1`; `=+K1+1`; `=+L1+1`; `=+M1+1`; `=+N1+1`
- **C_Azienda**: `=+'CE-mese'!B3`; `=+'CE-mese'!C3`; `=+'CE-mese'!D3`; `=+'CE-mese'!E3`; `=+'CE-mese'!F3`
- **Affitto**: `=+'CE-mese'!B3`; `=+'CE-mese'!C3`; `=+'CE-mese'!D3`; `=+'CE-mese'!E3`; `=+'CE-mese'!F3`
- **CE-mese**: `=+'SP-mese'!D3`; `=+'SP-mese'!E3`; `=+'SP-mese'!F3`; `=+'SP-mese'!G3`; `=+'SP-mese'!H3`
- **Cflow-mese**: `=+'SP-mese'!D3`; `=+'SP-mese'!E3`; `=+'SP-mese'!F3`; `=+'SP-mese'!G3`; `=+'SP-mese'!H3`
- **Banca-mese**: `=+'CE-mese'!B3`; `=+'CE-mese'!C3`; `=+'CE-mese'!D3`; `=+'CE-mese'!E3`; `=+'CE-mese'!F3`
- **SP-mese**: `=+Input!D9`; `=+IF(D4=1,C3+1,C3)`; `=+IF(E4=1,D3+1,D3)`; `=+IF(F4=1,E3+1,E3)`; `=+IF(G4=1,F3+1,F3)`
- **L_Iva**: `=+'Banca-mese'!B2`; `=+'Banca-mese'!C2`; `=+'Banca-mese'!D2`; `=+'Banca-mese'!E2`; `=+'Banca-mese'!F2`
- **I_Ult CE**: `=+E4-E5`; `=+E2-E6`; `=+'CE-mese'!A19`; `=+'CE-mese'!A20`; `=+'CE-mese'!A21`

## Raccomandazioni operative

- Definire **Excel Tables** per i blocchi chiave (Raccordo, Riclassificato, Banca-mese, SP-mese) per stabilizzare nomi colonne in ETL.
- **Centralizzare** le liste/driver (mensilità, dilazioni, tipologie) in un foglio **Parametri** e **deduplicare** i named ranges.
- Aggiungere **ID surrogate** per `conto_riclassificato` e `categoria` e documentare il **data lineage** tra fogli (es. `PreDeduzione → Gestione e Proposta...`).
- Normalizzare il **periodo** (es. `YYYY-MM`) nelle tabelle mensilizzate e predisporre **export CSV** per data lake/BI.

## Modello dati proposto per l’analisi (estrazione)

1. **dim_account**: account_originale, descrizione, conto_riclassificato, categoria_piano_crisi, natura (A/P).
2. **fact_balances**: periodo, account, importo, rettifiche, valore_netto.
3. **dim_time**: anno, mese, tipologia_mensilita.
4. **fact_liquidity_schedule**: periodo, voce, importo, dilazione_giorni.
5. **fact_tax_iva**: periodo, imponibile, iva, aliquota, posizione.
6. **fact_xbrl_concepts**: concept, unit, context/periodo, valore.

## Panoramica per foglio (metriche principali)

| sheet_name | n_rows | n_cols | data_validations | formula_cells_detected_(<=2000_rows) | suspected_xbrl_headers | suspected_xbrl_cells_sample | acct_keywords_in_headers | likely_mapping_sheet |
|---|---|---|---|---|---|---|---|---|
| Affitto | 10 | 125 | 1 | 482 | 0 | 0 | 0 | False |
| Attivo | 319 | 77 | 1 | 2025 | 0 | 0 | 0 | False |
| BCTool | 29 | 12 | 0 | 0 | 0 | 0 | 0 | False |
| Banca-mese | 64 | 133 | 0 | 1283 | 0 | 0 | 0 | False |
| CE-mese | 78 | 137 | 0 | 2309 | 0 | 0 | 0 | False |
| CRUSCOTTO | 37 | 12 | 0 | 310 | 0 | 0 | 0 | False |
| C_Azienda | 37 | 125 | 2 | 374 | 0 | 0 | 0 | False |
| Cflow-mese | 64 | 133 | 0 | 5449 | 0 | 0 | 0 | False |
| Gestione e Proposta concordatar | 60 | 130 | 1 | 2889 | 0 | 0 | 0 | False |
| Hp Liquidazione Giudiziale | 57 | 13 | 0 | 66 | 0 | 0 | 0 | False |
| I_Ult CE | 63 | 5 | 0 | 21 | 0 | 0 | 0 | False |
| Imm fin | 25 | 125 | 0 | 380 | 0 | 0 | 0 | False |
| Input | 126 | 8 | 0 | 14 | 0 | 0 | 0 | False |
| L_Iva | 35 | 126 | 0 | 1684 | 0 | 0 | 0 | False |
| MENU | 15 | 2 | 0 | 0 | 0 | 0 | 0 | False |
| Passivo | 122 | 13 | 1 | 479 | 0 | 0 | 0 | False |
| Passivo_Tipologie | 28 | 7 | 2 | 49 | 0 | 0 | 0 | False |
| Piano concordatario | 22 | 8 | 0 | 0 | 0 | 0 | 0 | False |
| PreDeduzione | 33 | 131 | 0 | 884 | 0 | 0 | 0 | False |
| Programma | 17 | 5 | 0 | 0 | 0 | 0 | 0 | False |
| Raccordo | 126 | 10 | 0 | 1000 | 0 | 0 | 3 | False |
| Relazione_AI | 186 | 18 | 0 | 705 | 0 | 1 | 0 | False |
| Riclassificato con Piano crisi | 117 | 5 | 0 | 351 | 0 | 0 | 2 | False |
| SP-mese | 89 | 123 | 0 | 4708 | 0 | 0 | 0 | False |
| SW_BUDGET-01 | 3 | 14 | 0 | 0 | 0 | 0 | 0 | False |
| SW_CE_BIL-01 | 657 | 20 | 0 | 1967 | 0 | 0 | 0 | False |
| SW_CE_CONTI | 163 | 4 | 0 | 0 | 0 | 0 | 0 | False |
| SW_CE_REP-01 | 3 | 21 | 0 | 0 | 0 | 0 | 0 | False |
| SW_FORECAST-01 | 128 | 62 | 0 | 60 | 0 | 0 | 1 | False |
| SW_FOR_FIN_OF-01 | 555 | 62 | 0 | 60 | 0 | 0 | 0 | False |
| SW_FOR_FIN_QC-01 | 649 | 62 | 0 | 60 | 0 | 0 | 0 | False |
| SW_FOR_TRI_OF-01 | 588 | 62 | 0 | 60 | 0 | 0 | 0 | False |
| SW_FOR_TRI_QC-01 | 689 | 62 | 0 | 60 | 0 | 0 | 0 | False |
| SW_SP_BIL-01 | 618 | 20 | 0 | 1850 | 0 | 0 | 0 | False |
| SW_SP_CONTI | 118 | 4 | 0 | 0 | 0 | 0 | 0 | False |
| SW_SP_REP-01 | 3 | 21 | 0 | 0 | 0 | 0 | 0 | False |
| Test_Piat | 31 | 10 | 0 | 7 | 0 | 0 | 0 | False |

## Appendice A – Dettaglio per foglio

### Programma
**Colonne (prime 30):**
- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
**Tipi rilevati (sample):**
- Unnamed: 0: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
**Valori nulli (sample):**
- Unnamed: 0: 16
- Unnamed: 1: 10
- Unnamed: 2: 9
- Unnamed: 3: 11
- Unnamed: 4: 14
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### MENU
**Colonne (prime 30):**
- Unnamed: 0
- 2025-09-17 00:00:00
**Tipi rilevati (sample):**
- Unnamed: 0: object
- 2025-09-17 00:00:00: object
**Valori nulli (sample):**
- Unnamed: 0: 14
- 2025-09-17 00:00:00: 1
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### BCTool
**Colonne (prime 30):**
- Unnamed: 0
- DEVAJH1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
**Tipi rilevati (sample):**
- Unnamed: 0: object
- DEVAJH1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
**Valori nulli (sample):**
- Unnamed: 0: 11
- DEVAJH1: 6
- Unnamed: 2: 15
- Unnamed: 3: 15
- Unnamed: 4: 7
- Unnamed: 5: 6
- Unnamed: 6: 6
- Unnamed: 7: 6
- Unnamed: 8: 28
- Unnamed: 9: 19
- Unnamed: 10: 19
- Unnamed: 11: 19
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### SW_SP_CONTI
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
**Valori nulli (sample):**
- MENU: 117
- Unnamed: 1: 0
- Unnamed: 2: 0
- Unnamed: 3: 0
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### SW_CE_CONTI
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
**Valori nulli (sample):**
- MENU: 162
- Unnamed: 1: 0
- Unnamed: 2: 0
- Unnamed: 3: 0
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### SW_FOR_TRI_OF-01
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: datetime64[ns]
- Unnamed: 3: datetime64[ns]
- Unnamed: 4: datetime64[ns]
- Unnamed: 5: datetime64[ns]
- Unnamed: 6: datetime64[ns]
- Unnamed: 7: datetime64[ns]
- Unnamed: 8: datetime64[ns]
- Unnamed: 9: datetime64[ns]
- Unnamed: 10: datetime64[ns]
- Unnamed: 11: datetime64[ns]
- Unnamed: 12: datetime64[ns]
- Unnamed: 13: datetime64[ns]
- Unnamed: 14: datetime64[ns]
- Unnamed: 15: datetime64[ns]
- Unnamed: 16: datetime64[ns]
- Unnamed: 17: datetime64[ns]
- Unnamed: 18: datetime64[ns]
- Unnamed: 19: datetime64[ns]
**Valori nulli (sample):**
- MENU: 587
- Unnamed: 1: 0
- Unnamed: 2: 586
- Unnamed: 3: 586
- Unnamed: 4: 586
- Unnamed: 5: 586
- Unnamed: 6: 586
- Unnamed: 7: 586
- Unnamed: 8: 586
- Unnamed: 9: 586
- Unnamed: 10: 586
- Unnamed: 11: 586
- Unnamed: 12: 586
- Unnamed: 13: 586
- Unnamed: 14: 586
- Unnamed: 15: 586
- Unnamed: 16: 586
- Unnamed: 17: 586
- Unnamed: 18: 586
- Unnamed: 19: 586
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+EOMONTH(MENU!B1,1)`
- `=+EOMONTH(C2,1)`
- `=+EOMONTH(D2,1)`
- `=+EOMONTH(E2,1)`
- `=+EOMONTH(F2,1)`
- `=+EOMONTH(G2,1)`
- `=+EOMONTH(H2,1)`
- `=+EOMONTH(I2,1)`
- `=+EOMONTH(J2,1)`
- `=+EOMONTH(K2,1)`

### SW_FOR_TRI_QC-01
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: datetime64[ns]
- Unnamed: 3: datetime64[ns]
- Unnamed: 4: datetime64[ns]
- Unnamed: 5: datetime64[ns]
- Unnamed: 6: datetime64[ns]
- Unnamed: 7: datetime64[ns]
- Unnamed: 8: datetime64[ns]
- Unnamed: 9: datetime64[ns]
- Unnamed: 10: datetime64[ns]
- Unnamed: 11: datetime64[ns]
- Unnamed: 12: datetime64[ns]
- Unnamed: 13: datetime64[ns]
- Unnamed: 14: datetime64[ns]
- Unnamed: 15: datetime64[ns]
- Unnamed: 16: datetime64[ns]
- Unnamed: 17: datetime64[ns]
- Unnamed: 18: datetime64[ns]
- Unnamed: 19: datetime64[ns]
**Valori nulli (sample):**
- MENU: 688
- Unnamed: 1: 0
- Unnamed: 2: 687
- Unnamed: 3: 687
- Unnamed: 4: 687
- Unnamed: 5: 687
- Unnamed: 6: 687
- Unnamed: 7: 687
- Unnamed: 8: 687
- Unnamed: 9: 687
- Unnamed: 10: 687
- Unnamed: 11: 687
- Unnamed: 12: 687
- Unnamed: 13: 687
- Unnamed: 14: 687
- Unnamed: 15: 687
- Unnamed: 16: 687
- Unnamed: 17: 687
- Unnamed: 18: 687
- Unnamed: 19: 687
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+EOMONTH(MENU!B1,1)`
- `=+EOMONTH(C2,1)`
- `=+EOMONTH(D2,1)`
- `=+EOMONTH(E2,1)`
- `=+EOMONTH(F2,1)`
- `=+EOMONTH(G2,1)`
- `=+EOMONTH(H2,1)`
- `=+EOMONTH(I2,1)`
- `=+EOMONTH(J2,1)`
- `=+EOMONTH(K2,1)`

### SW_FOR_FIN_OF-01
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: datetime64[ns]
- Unnamed: 3: datetime64[ns]
- Unnamed: 4: datetime64[ns]
- Unnamed: 5: datetime64[ns]
- Unnamed: 6: datetime64[ns]
- Unnamed: 7: datetime64[ns]
- Unnamed: 8: datetime64[ns]
- Unnamed: 9: datetime64[ns]
- Unnamed: 10: datetime64[ns]
- Unnamed: 11: datetime64[ns]
- Unnamed: 12: datetime64[ns]
- Unnamed: 13: datetime64[ns]
- Unnamed: 14: datetime64[ns]
- Unnamed: 15: datetime64[ns]
- Unnamed: 16: datetime64[ns]
- Unnamed: 17: datetime64[ns]
- Unnamed: 18: datetime64[ns]
- Unnamed: 19: datetime64[ns]
**Valori nulli (sample):**
- MENU: 554
- Unnamed: 1: 0
- Unnamed: 2: 553
- Unnamed: 3: 553
- Unnamed: 4: 553
- Unnamed: 5: 553
- Unnamed: 6: 553
- Unnamed: 7: 553
- Unnamed: 8: 553
- Unnamed: 9: 553
- Unnamed: 10: 553
- Unnamed: 11: 553
- Unnamed: 12: 553
- Unnamed: 13: 553
- Unnamed: 14: 553
- Unnamed: 15: 553
- Unnamed: 16: 553
- Unnamed: 17: 553
- Unnamed: 18: 553
- Unnamed: 19: 553
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+EOMONTH(MENU!B1,1)`
- `=+EOMONTH(C2,1)`
- `=+EOMONTH(D2,1)`
- `=+EOMONTH(E2,1)`
- `=+EOMONTH(F2,1)`
- `=+EOMONTH(G2,1)`
- `=+EOMONTH(H2,1)`
- `=+EOMONTH(I2,1)`
- `=+EOMONTH(J2,1)`
- `=+EOMONTH(K2,1)`

### SW_FOR_FIN_QC-01
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: datetime64[ns]
- Unnamed: 3: datetime64[ns]
- Unnamed: 4: datetime64[ns]
- Unnamed: 5: datetime64[ns]
- Unnamed: 6: datetime64[ns]
- Unnamed: 7: datetime64[ns]
- Unnamed: 8: datetime64[ns]
- Unnamed: 9: datetime64[ns]
- Unnamed: 10: datetime64[ns]
- Unnamed: 11: datetime64[ns]
- Unnamed: 12: datetime64[ns]
- Unnamed: 13: datetime64[ns]
- Unnamed: 14: datetime64[ns]
- Unnamed: 15: datetime64[ns]
- Unnamed: 16: datetime64[ns]
- Unnamed: 17: datetime64[ns]
- Unnamed: 18: datetime64[ns]
- Unnamed: 19: datetime64[ns]
**Valori nulli (sample):**
- MENU: 648
- Unnamed: 1: 0
- Unnamed: 2: 647
- Unnamed: 3: 647
- Unnamed: 4: 647
- Unnamed: 5: 647
- Unnamed: 6: 647
- Unnamed: 7: 647
- Unnamed: 8: 647
- Unnamed: 9: 647
- Unnamed: 10: 647
- Unnamed: 11: 647
- Unnamed: 12: 647
- Unnamed: 13: 647
- Unnamed: 14: 647
- Unnamed: 15: 647
- Unnamed: 16: 647
- Unnamed: 17: 647
- Unnamed: 18: 647
- Unnamed: 19: 647
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+EOMONTH(MENU!B1,1)`
- `=+EOMONTH(C2,1)`
- `=+EOMONTH(D2,1)`
- `=+EOMONTH(E2,1)`
- `=+EOMONTH(F2,1)`
- `=+EOMONTH(G2,1)`
- `=+EOMONTH(H2,1)`
- `=+EOMONTH(I2,1)`
- `=+EOMONTH(J2,1)`
- `=+EOMONTH(K2,1)`

### SW_FORECAST-01
**Colonne (prime 30):**
- Descrizione
- Categoria
- 2025-10-31 00:00:00
- 2025-11-30 00:00:00
- 2025-12-31 00:00:00
- 2026-01-31 00:00:00
- 2026-02-28 00:00:00
- 2026-03-31 00:00:00
- 2026-04-30 00:00:00
- 2026-05-31 00:00:00
- 2026-06-30 00:00:00
- 2026-07-31 00:00:00
- 2026-08-31 00:00:00
- 2026-09-30 00:00:00
- 2026-10-31 00:00:00
- 2026-11-30 00:00:00
- 2026-12-31 00:00:00
- 2027-01-31 00:00:00
- 2027-02-28 00:00:00
- 2027-03-31 00:00:00
- 2027-04-30 00:00:00
- 2027-05-31 00:00:00
- 2027-06-30 00:00:00
- 2027-07-31 00:00:00
- 2027-08-31 00:00:00
- 2027-09-30 00:00:00
- 2027-10-31 00:00:00
- 2027-11-30 00:00:00
- 2027-12-31 00:00:00
- 2028-01-31 00:00:00
**Tipi rilevati (sample):**
- Descrizione: object
- Categoria: object
- 2025-10-31 00:00:00: object
- 2025-11-30 00:00:00: object
- 2025-12-31 00:00:00: object
- 2026-01-31 00:00:00: object
- 2026-02-28 00:00:00: object
- 2026-03-31 00:00:00: object
- 2026-04-30 00:00:00: object
- 2026-05-31 00:00:00: object
- 2026-06-30 00:00:00: object
- 2026-07-31 00:00:00: object
- 2026-08-31 00:00:00: object
- 2026-09-30 00:00:00: object
- 2026-10-31 00:00:00: object
- 2026-11-30 00:00:00: object
- 2026-12-31 00:00:00: object
- 2027-01-31 00:00:00: object
- 2027-02-28 00:00:00: object
- 2027-03-31 00:00:00: object
**Valori nulli (sample):**
- Descrizione: 0
- Categoria: 0
- 2025-10-31 00:00:00: 96
- 2025-11-30 00:00:00: 89
- 2025-12-31 00:00:00: 96
- 2026-01-31 00:00:00: 95
- 2026-02-28 00:00:00: 93
- 2026-03-31 00:00:00: 96
- 2026-04-30 00:00:00: 96
- 2026-05-31 00:00:00: 91
- 2026-06-30 00:00:00: 96
- 2026-07-31 00:00:00: 96
- 2026-08-31 00:00:00: 93
- 2026-09-30 00:00:00: 96
- 2026-10-31 00:00:00: 96
- 2026-11-30 00:00:00: 89
- 2026-12-31 00:00:00: 96
- 2027-01-31 00:00:00: 95
- 2027-02-28 00:00:00: 93
- 2027-03-31 00:00:00: 96
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+EOMONTH(MENU!B1,1)`
- `=+EOMONTH(C1,1)`
- `=+EOMONTH(D1,1)`
- `=+EOMONTH(E1,1)`
- `=+EOMONTH(F1,1)`
- `=+EOMONTH(G1,1)`
- `=+EOMONTH(H1,1)`
- `=+EOMONTH(I1,1)`
- `=+EOMONTH(J1,1)`
- `=+EOMONTH(K1,1)`

### SW_BUDGET-01
**Colonne (prime 30):**
- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
**Tipi rilevati (sample):**
- Unnamed: 0: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
**Valori nulli (sample):**
- Unnamed: 0: 1
- Unnamed: 1: 1
- Unnamed: 2: 0
- Unnamed: 3: 0
- Unnamed: 4: 0
- Unnamed: 5: 0
- Unnamed: 6: 0
- Unnamed: 7: 0
- Unnamed: 8: 0
- Unnamed: 9: 0
- Unnamed: 10: 0
- Unnamed: 11: 0
- Unnamed: 12: 0
- Unnamed: 13: 0
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### SW_SP_BIL-01
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 617
- Unnamed: 1: 1
- Unnamed: 2: 1
- Unnamed: 3: 1
- Unnamed: 4: 616
- Unnamed: 5: 616
- Unnamed: 6: 616
- Unnamed: 7: 616
- Unnamed: 8: 616
- Unnamed: 9: 616
- Unnamed: 10: 616
- Unnamed: 11: 616
- Unnamed: 12: 616
- Unnamed: 13: 616
- Unnamed: 14: 616
- Unnamed: 15: 616
- Unnamed: 16: 616
- Unnamed: 17: 616
- Unnamed: 18: 616
- Unnamed: 19: 499
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+F3-1`
- `=+G3-1`
- `=+H3-1`
- `=+YEAR(MENU!B1)-1`
- `=+MENU!B1`
- `=+SW_SP_CONTI!B3`
- `=+SW_SP_CONTI!C3`
- `=+SW_SP_CONTI!D3`
- `=+SW_SP_CONTI!B4`
- `=+SW_SP_CONTI!C4`

### SW_CE_BIL-01
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 656
- Unnamed: 1: 1
- Unnamed: 2: 1
- Unnamed: 3: 1
- Unnamed: 4: 655
- Unnamed: 5: 655
- Unnamed: 6: 655
- Unnamed: 7: 655
- Unnamed: 8: 655
- Unnamed: 9: 655
- Unnamed: 10: 655
- Unnamed: 11: 655
- Unnamed: 12: 655
- Unnamed: 13: 655
- Unnamed: 14: 655
- Unnamed: 15: 655
- Unnamed: 16: 655
- Unnamed: 17: 655
- Unnamed: 18: 655
- Unnamed: 19: 493
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+F3-1`
- `=+G3-1`
- `=+H3-1`
- `=+YEAR(MENU!B1)-1`
- `=+MENU!B1`
- `=+SW_CE_CONTI!B3`
- `=+SW_CE_CONTI!C3`
- `=+SW_CE_CONTI!D3`
- `=+SW_CE_CONTI!B4`
- `=+SW_CE_CONTI!C4`

### SW_SP_REP-01
**Colonne (prime 30):**
- MENU
- 0
- 0.1
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
**Tipi rilevati (sample):**
- MENU: object
- 0: object
- 0.1: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 2
- 0: 1
- 0.1: 1
- Unnamed: 3: 1
- Unnamed: 4: 1
- Unnamed: 5: 1
- Unnamed: 6: 1
- Unnamed: 7: 1
- Unnamed: 8: 1
- Unnamed: 9: 1
- Unnamed: 10: 1
- Unnamed: 11: 1
- Unnamed: 12: 1
- Unnamed: 13: 1
- Unnamed: 14: 1
- Unnamed: 15: 1
- Unnamed: 16: 1
- Unnamed: 17: 1
- Unnamed: 18: 1
- Unnamed: 19: 1
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### SW_CE_REP-01
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 2
- Unnamed: 1: 1
- Unnamed: 2: 1
- Unnamed: 3: 1
- Unnamed: 4: 1
- Unnamed: 5: 1
- Unnamed: 6: 1
- Unnamed: 7: 1
- Unnamed: 8: 1
- Unnamed: 9: 1
- Unnamed: 10: 1
- Unnamed: 11: 1
- Unnamed: 12: 1
- Unnamed: 13: 1
- Unnamed: 14: 1
- Unnamed: 15: 1
- Unnamed: 16: 1
- Unnamed: 17: 1
- Unnamed: 18: 1
- Unnamed: 19: 1
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### Riclassificato con Piano crisi
**Colonne (prime 30):**
- Conto
- Descrizione
- CATEGORIA
- Attivo
- Passivo
**Tipi rilevati (sample):**
- Conto: object
- Descrizione: object
- CATEGORIA: object
- Attivo: object
- Passivo: object
**Valori nulli (sample):**
- Conto: 0
- Descrizione: 0
- CATEGORIA: 0
- Attivo: 57
- Passivo: 59
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=SW_SP_CONTI!B2`
- `=SW_SP_CONTI!C2`
- `=SW_SP_CONTI!D2`
- `=SW_SP_CONTI!B3`
- `=SW_SP_CONTI!C3`
- `=SW_SP_CONTI!D3`
- `=SW_SP_CONTI!B4`
- `=SW_SP_CONTI!C4`
- `=SW_SP_CONTI!D4`
- `=SW_SP_CONTI!B5`

### Raccordo
**Colonne (prime 30):**
- Input
- CONTO RICLASSIFICATO
- CONTO IMPORTATO
- DESCRIZIONE
- Riclassifica PdC
- Attivo
- Passivo
- Importo
- Rettifiche
- Valore netto
**Tipi rilevati (sample):**
- Input: object
- CONTO RICLASSIFICATO: object
- CONTO IMPORTATO: object
- DESCRIZIONE: object
- Riclassifica PdC: object
- Attivo: object
- Passivo: object
- Importo: object
- Rettifiche: object
- Valore netto: object
**Valori nulli (sample):**
- Input: 123
- CONTO RICLASSIFICATO: 0
- CONTO IMPORTATO: 0
- DESCRIZIONE: 0
- Riclassifica PdC: 125
- Attivo: 125
- Passivo: 125
- Importo: 0
- Rettifiche: 125
- Valore netto: 0
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `='SW_SP_REP-01'!B4`
- `='SW_SP_REP-01'!C4`
- `='SW_SP_REP-01'!D4`
- `=_xlfn.XLOOKUP(B2,'SW_SP_BIL-01'!B:B,'SW_SP_BIL-01'!D:D)`
- `=+IFERROR(VLOOKUP($B2,'Riclassificato con Piano crisi'!$A:$E,4,FALSE),"")`
- `=+IFERROR(VLOOKUP($B2,'Riclassificato con Piano crisi'!$A:$E,5,FALSE),"")`
- `=SUMIF('SW_SP_REP-01'!C:C,$C2,'SW_SP_REP-01'!T:T)`
- `=H2+I2`
- `='SW_SP_REP-01'!B5`
- `='SW_SP_REP-01'!C5`

### Input
**Colonne (prime 30):**
- 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
**Tipi rilevati (sample):**
- 0: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
**Valori nulli (sample):**
- 0: 112
- Unnamed: 1: 110
- Unnamed: 2: 118
- Unnamed: 3: 117
- Unnamed: 4: 122
- Unnamed: 5: 124
- Unnamed: 6: 124
- Unnamed: 7: 123
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+Passivo!B99`
- `=YEAR(MENU!B1)`
- `=MONTH(MENU!B1)`
- `=+B114+1`
- `=+B115+1`
- `=+B116+1`
- `=+B117+1`
- `=+B118+1`
- `=+B119+1`
- `=+B120+1`

### Hp Liquidazione Giudiziale
**Colonne (prime 30):**
- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
**Tipi rilevati (sample):**
- Unnamed: 0: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
**Valori nulli (sample):**
- Unnamed: 0: 56
- Unnamed: 1: 56
- Unnamed: 2: 51
- Unnamed: 3: 18
- Unnamed: 4: 51
- Unnamed: 5: 28
- Unnamed: 6: 56
- Unnamed: 7: 45
- Unnamed: 8: 46
- Unnamed: 9: 48
- Unnamed: 10: 31
- Unnamed: 11: 46
- Unnamed: 12: 55
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+F6`
- `=+F8`
- `=+F9`
- `=+Attivo!K8`
- `=+F10`
- `=SUM(F6:F10)`
- `=+F13`
- `=+F14`
- `=+F15`
- `=+F16`

### Relazione_AI
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
**Valori nulli (sample):**
- MENU: 134
- Unnamed: 1: 134
- Unnamed: 2: 134
- Unnamed: 3: 22
- Unnamed: 4: 35
- Unnamed: 5: 63
- Unnamed: 6: 42
- Unnamed: 7: 65
- Unnamed: 8: 65
- Unnamed: 9: 64
- Unnamed: 10: 86
- Unnamed: 11: 86
- Unnamed: 12: 109
- Unnamed: 13: 126
- Unnamed: 14: 126
- Unnamed: 15: 126
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+Attivo!B3`
- `=+Attivo!C4`
- `=+Attivo!E4`
- `=+Attivo!G4`
- `=+Attivo!H4`
- `=+Attivo!I4`
- `=+Attivo!A5`
- `=+Attivo!B5`
- `=+Attivo!C5`
- `=+Attivo!E5`

### Test_Piat
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
**Valori nulli (sample):**
- MENU: 30
- Unnamed: 1: 30
- Unnamed: 2: 30
- Unnamed: 3: 18
- Unnamed: 4: 12
- Unnamed: 5: 22
- Unnamed: 6: 30
- Unnamed: 7: 30
- Unnamed: 8: 29
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=-'Gestione e Proposta concordatar'!H7`
- `=SUM(F7:F14)`
- `=+'CE-mese'!DU54-'CE-mese'!DU52-'CE-mese'!DU45`
- `=+SUMIF(#REF!,'CE-mese'!DU3,#REF!)`
- `=+'CE-mese'!DU67`
- `=SUM(F18:F20)`
- `=+IFERROR(F15/F21,"NA")`

### Passivo_Tipologie
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
**Valori nulli (sample):**
- MENU: 17
- Unnamed: 1: 3
- Unnamed: 2: 14
- Unnamed: 3: 5
- Unnamed: 4: 5
- Unnamed: 5: 27
- Unnamed: 6: 7
**Data validations:** 2
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=D5& "_" & B5 & " _ " & C5`
- `=+B5`
- `=+A5+1`
- `=D6& "_" & B6 & " _ " & C6`
- `=+B6`
- `=+A6+1`
- `=D7& "_" & B7 & " _ " & C7`
- `=+B7`
- `=+A7+1`
- `=D8& "_" & B8 & " _ " & C8`

### Piano concordatario
**Colonne (prime 30):**
- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
**Tipi rilevati (sample):**
- Unnamed: 0: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
**Valori nulli (sample):**
- Unnamed: 0: 20
- Unnamed: 1: 20
- Unnamed: 2: 16
- Unnamed: 3: 15
- Unnamed: 4: 20
- Unnamed: 5: 20
- Unnamed: 6: 20
- Unnamed: 7: 19
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_

### PreDeduzione
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 30
- Unnamed: 1: 30
- Unnamed: 2: 17
- Unnamed: 3: 17
- Unnamed: 4: 24
- Unnamed: 5: 28
- Unnamed: 6: 20
- Unnamed: 7: 22
- Unnamed: 8: 11
- Unnamed: 9: 30
- Unnamed: 10: 6
- Unnamed: 11: 23
- Unnamed: 12: 23
- Unnamed: 13: 23
- Unnamed: 14: 23
- Unnamed: 15: 23
- Unnamed: 16: 23
- Unnamed: 17: 23
- Unnamed: 18: 21
- Unnamed: 19: 22
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=MIN(L2:EA2)`
- `='Gestione e Proposta concordatar'!J20`
- `='Gestione e Proposta concordatar'!K20`
- `='Gestione e Proposta concordatar'!L20`
- `='Gestione e Proposta concordatar'!M20`
- `='Gestione e Proposta concordatar'!N20`
- `='Gestione e Proposta concordatar'!O20`
- `='Gestione e Proposta concordatar'!P20`
- `='Gestione e Proposta concordatar'!Q20`
- `='Gestione e Proposta concordatar'!R20`

### CRUSCOTTO
**Colonne (prime 30):**
- Unnamed: 0
- MENU
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
**Tipi rilevati (sample):**
- Unnamed: 0: object
- MENU: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
**Valori nulli (sample):**
- Unnamed: 0: 35
- MENU: 7
- Unnamed: 2: 34
- Unnamed: 3: 34
- Unnamed: 4: 34
- Unnamed: 5: 34
- Unnamed: 6: 34
- Unnamed: 7: 34
- Unnamed: 8: 34
- Unnamed: 9: 34
- Unnamed: 10: 34
- Unnamed: 11: 34
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=C3-1`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`

### Imm fin
**Colonne (prime 30):**
- Equity 
- Unnamed: 1
- MENU
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- Equity : object
- Unnamed: 1: object
- MENU: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- Equity : 24
- Unnamed: 1: 24
- MENU: 3
- Unnamed: 3: 4
- Unnamed: 4: 24
- Unnamed: 5: 23
- Unnamed: 6: 23
- Unnamed: 7: 23
- Unnamed: 8: 23
- Unnamed: 9: 23
- Unnamed: 10: 23
- Unnamed: 11: 23
- Unnamed: 12: 23
- Unnamed: 13: 23
- Unnamed: 14: 23
- Unnamed: 15: 23
- Unnamed: 16: 23
- Unnamed: 17: 23
- Unnamed: 18: 23
- Unnamed: 19: 23
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`
- `=+#REF!`

### Attivo
**Colonne (prime 30):**
- MENU
- Dettaglio SP Attivo
- Formule
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Dettaglio SP Attivo: object
- Formule: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 203
- Dettaglio SP Attivo: 292
- Formule: 313
- Unnamed: 3: 315
- Unnamed: 4: 299
- Unnamed: 5: 303
- Unnamed: 6: 295
- Unnamed: 7: 293
- Unnamed: 8: 284
- Unnamed: 9: 206
- Unnamed: 10: 202
- Unnamed: 11: 314
- Unnamed: 12: 313
- Unnamed: 13: 300
- Unnamed: 14: 318
- Unnamed: 15: 228
- Unnamed: 16: 315
- Unnamed: 17: 292
- Unnamed: 18: 292
- Unnamed: 19: 292
**Data validations:** 1
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+'Gestione e Proposta concordatar'!J3`
- `=+'Gestione e Proposta concordatar'!K3`
- `=+'Gestione e Proposta concordatar'!L3`
- `=+'Gestione e Proposta concordatar'!M3`
- `=+'Gestione e Proposta concordatar'!N3`
- `=+'Gestione e Proposta concordatar'!O3`
- `=+'Gestione e Proposta concordatar'!P3`
- `=+'Gestione e Proposta concordatar'!Q3`
- `=+'Gestione e Proposta concordatar'!R3`
- `=+'Gestione e Proposta concordatar'!S3`

### Passivo
**Colonne (prime 30):**
- MENU
- Dettaglio Passivo
- Formule
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
**Tipi rilevati (sample):**
- MENU: object
- Dettaglio Passivo: object
- Formule: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
**Valori nulli (sample):**
- MENU: 35
- Dettaglio Passivo: 91
- Formule: 104
- Unnamed: 3: 86
- Unnamed: 4: 38
- Unnamed: 5: 105
- Unnamed: 6: 105
- Unnamed: 7: 105
- Unnamed: 8: 38
- Unnamed: 9: 29
- Unnamed: 10: 87
**Data validations:** 1
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+Attivo!B3`
- `=-SUMIF(Raccordo!G:G,$A6,Raccordo!J:J)`
- `=+SUM(C7:C17)`
- `=+SUM(D7:D17)`
- `=+SUM(E7:E17)`
- `=+SUM(F7:F17)`
- `=+SUM(G7:G17)`
- `=+SUM(H7:H17)`
- `=+SUM(I7:I17)`
- `=+SUM(J7:J17)`

### Gestione e Proposta concordatar
**Colonne (prime 30):**
- MENU
- input
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- ANNO DI PIANO
- 1
- 1.1
- 1.2
- 1.3
- 1.4
- 1.5
- 1.6
- 1.7
- 1.8
- 1.9
- 1.10
- 1.11
- 2
- 2.1
- 2.2
- 2.3
- 2.4
- 2.5
- 2.6
- 2.7
- 2.8
**Tipi rilevati (sample):**
- MENU: object
- input: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- ANNO DI PIANO: object
- 1: object
- 1.1: object
- 1.2: object
- 1.3: object
- 1.4: object
- 1.5: object
- 1.6: object
- 1.7: object
- 1.8: object
- 1.9: object
- 1.10: object
**Valori nulli (sample):**
- MENU: 59
- input: 33
- Unnamed: 2: 35
- Unnamed: 3: 56
- Unnamed: 4: 35
- Unnamed: 5: 36
- Unnamed: 6: 31
- Unnamed: 7: 20
- ANNO DI PIANO: 18
- 1: 36
- 1.1: 36
- 1.2: 36
- 1.3: 36
- 1.4: 36
- 1.5: 35
- 1.6: 36
- 1.7: 36
- 1.8: 36
- 1.9: 33
- 1.10: 36
**Data validations:** 1
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+J1+1`
- `=+K1+1`
- `=+L1+1`
- `=+M1+1`
- `=+N1+1`
- `=+O1+1`
- `=+P1+1`
- `=+Q1+1`
- `=+R1+1`
- `=+S1+1`

### C_Azienda
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- anno
- 2025
- 2025.1
- 2025.2
- 2026
- 2026.1
- 2026.2
- 2026.3
- 2026.4
- 2026.5
- 2026.6
- 2026.7
- 2026.8
- 2026.9
- 2026.10
- 2026.11
- 2027
- 2027.1
- 2027.2
- 2027.3
- 2027.4
- 2027.5
- 2027.6
- 2027.7
- 2027.8
- 2027.9
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- anno: object
- 2025: object
- 2025.1: object
- 2025.2: object
- 2026: object
- 2026.1: object
- 2026.2: object
- 2026.3: object
- 2026.4: object
- 2026.5: object
- 2026.6: object
- 2026.7: object
- 2026.8: object
- 2026.9: object
- 2026.10: object
- 2026.11: object
**Valori nulli (sample):**
- MENU: 36
- Unnamed: 1: 33
- Unnamed: 2: 13
- Unnamed: 3: 35
- anno: 34
- 2025: 34
- 2025.1: 34
- 2025.2: 34
- 2026: 34
- 2026.1: 34
- 2026.2: 34
- 2026.3: 34
- 2026.4: 34
- 2026.5: 34
- 2026.6: 34
- 2026.7: 34
- 2026.8: 34
- 2026.9: 34
- 2026.10: 34
- 2026.11: 34
**Data validations:** 2
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+'CE-mese'!B3`
- `=+'CE-mese'!C3`
- `=+'CE-mese'!D3`
- `=+'CE-mese'!E3`
- `=+'CE-mese'!F3`
- `=+'CE-mese'!G3`
- `=+'CE-mese'!H3`
- `=+'CE-mese'!I3`
- `=+'CE-mese'!J3`
- `=+'CE-mese'!K3`

### Affitto
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- anno
- 2025
- 2025.1
- 2025.2
- 2026
- 2026.1
- 2026.2
- 2026.3
- 2026.4
- 2026.5
- 2026.6
- 2026.7
- 2026.8
- 2026.9
- 2026.10
- 2026.11
- 2027
- 2027.1
- 2027.2
- 2027.3
- 2027.4
- 2027.5
- 2027.6
- 2027.7
- 2027.8
- 2027.9
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- anno: object
- 2025: object
- 2025.1: object
- 2025.2: object
- 2026: object
- 2026.1: object
- 2026.2: object
- 2026.3: object
- 2026.4: object
- 2026.5: object
- 2026.6: object
- 2026.7: object
- 2026.8: object
- 2026.9: object
- 2026.10: object
- 2026.11: object
**Valori nulli (sample):**
- MENU: 9
- Unnamed: 1: 6
- Unnamed: 2: 6
- Unnamed: 3: 8
- anno: 8
- 2025: 6
- 2025.1: 6
- 2025.2: 6
- 2026: 6
- 2026.1: 6
- 2026.2: 6
- 2026.3: 6
- 2026.4: 6
- 2026.5: 6
- 2026.6: 6
- 2026.7: 6
- 2026.8: 6
- 2026.9: 6
- 2026.10: 6
- 2026.11: 6
**Data validations:** 1
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+'CE-mese'!B3`
- `=+'CE-mese'!C3`
- `=+'CE-mese'!D3`
- `=+'CE-mese'!E3`
- `=+'CE-mese'!F3`
- `=+'CE-mese'!G3`
- `=+'CE-mese'!H3`
- `=+'CE-mese'!I3`
- `=+'CE-mese'!J3`
- `=+'CE-mese'!K3`

### CE-mese
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 34
- Unnamed: 1: 66
- Unnamed: 2: 53
- Unnamed: 3: 53
- Unnamed: 4: 53
- Unnamed: 5: 53
- Unnamed: 6: 53
- Unnamed: 7: 53
- Unnamed: 8: 53
- Unnamed: 9: 53
- Unnamed: 10: 53
- Unnamed: 11: 53
- Unnamed: 12: 53
- Unnamed: 13: 53
- Unnamed: 14: 53
- Unnamed: 15: 53
- Unnamed: 16: 53
- Unnamed: 17: 53
- Unnamed: 18: 53
- Unnamed: 19: 53
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+'SP-mese'!D3`
- `=+'SP-mese'!E3`
- `=+'SP-mese'!F3`
- `=+'SP-mese'!G3`
- `=+'SP-mese'!H3`
- `=+'SP-mese'!I3`
- `=+'SP-mese'!J3`
- `=+'SP-mese'!K3`
- `=+'SP-mese'!L3`
- `=+'SP-mese'!M3`

### Cflow-mese
**Colonne (prime 30):**
- MENU
- anno
- 2025
- 2025.1
- 2025.2
- 2026
- 2026.1
- 2026.2
- 2026.3
- 2026.4
- 2026.5
- 2026.6
- 2026.7
- 2026.8
- 2026.9
- 2026.10
- 2026.11
- 2027
- 2027.1
- 2027.2
- 2027.3
- 2027.4
- 2027.5
- 2027.6
- 2027.7
- 2027.8
- 2027.9
- 2027.10
- 2027.11
- 2028
**Tipi rilevati (sample):**
- MENU: object
- anno: object
- 2025: object
- 2025.1: object
- 2025.2: object
- 2026: object
- 2026.1: object
- 2026.2: object
- 2026.3: object
- 2026.4: object
- 2026.5: object
- 2026.6: object
- 2026.7: object
- 2026.8: object
- 2026.9: object
- 2026.10: object
- 2026.11: object
- 2027: object
- 2027.1: object
- 2027.2: object
**Valori nulli (sample):**
- MENU: 19
- anno: 62
- 2025: 33
- 2025.1: 34
- 2025.2: 34
- 2026: 34
- 2026.1: 34
- 2026.2: 34
- 2026.3: 34
- 2026.4: 34
- 2026.5: 34
- 2026.6: 34
- 2026.7: 34
- 2026.8: 34
- 2026.9: 34
- 2026.10: 34
- 2026.11: 34
- 2027: 34
- 2027.1: 34
- 2027.2: 34
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+'SP-mese'!D3`
- `=+'SP-mese'!E3`
- `=+'SP-mese'!F3`
- `=+'SP-mese'!G3`
- `=+'SP-mese'!H3`
- `=+'SP-mese'!I3`
- `=+'SP-mese'!J3`
- `=+'SP-mese'!K3`
- `=+'SP-mese'!L3`
- `=+'SP-mese'!M3`

### Banca-mese
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 11
- Unnamed: 1: 44
- Unnamed: 2: 40
- Unnamed: 3: 40
- Unnamed: 4: 40
- Unnamed: 5: 40
- Unnamed: 6: 40
- Unnamed: 7: 40
- Unnamed: 8: 40
- Unnamed: 9: 40
- Unnamed: 10: 40
- Unnamed: 11: 40
- Unnamed: 12: 40
- Unnamed: 13: 40
- Unnamed: 14: 40
- Unnamed: 15: 40
- Unnamed: 16: 40
- Unnamed: 17: 40
- Unnamed: 18: 40
- Unnamed: 19: 40
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+'CE-mese'!B3`
- `=+'CE-mese'!C3`
- `=+'CE-mese'!D3`
- `=+'CE-mese'!E3`
- `=+'CE-mese'!F3`
- `=+'CE-mese'!G3`
- `=+'CE-mese'!H3`
- `=+'CE-mese'!I3`
- `=+'CE-mese'!J3`
- `=+'CE-mese'!K3`

### SP-mese
**Colonne (prime 30):**
- MENU
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- MENU: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- MENU: 20
- Unnamed: 1: 84
- Unnamed: 2: 60
- Unnamed: 3: 49
- Unnamed: 4: 49
- Unnamed: 5: 49
- Unnamed: 6: 49
- Unnamed: 7: 49
- Unnamed: 8: 49
- Unnamed: 9: 49
- Unnamed: 10: 49
- Unnamed: 11: 49
- Unnamed: 12: 49
- Unnamed: 13: 49
- Unnamed: 14: 49
- Unnamed: 15: 49
- Unnamed: 16: 49
- Unnamed: 17: 49
- Unnamed: 18: 49
- Unnamed: 19: 49
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+Input!D9`
- `=+IF(D4=1,C3+1,C3)`
- `=+IF(E4=1,D3+1,D3)`
- `=+IF(F4=1,E3+1,E3)`
- `=+IF(G4=1,F3+1,F3)`
- `=+IF(H4=1,G3+1,G3)`
- `=+IF(I4=1,H3+1,H3)`
- `=+IF(J4=1,I3+1,I3)`
- `=+IF(K4=1,J3+1,J3)`
- `=+IF(L4=1,K3+1,K3)`

### L_Iva
**Colonne (prime 30):**
- Unnamed: 0
- MENU
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
- Unnamed: 5
- Unnamed: 6
- Unnamed: 7
- Unnamed: 8
- Unnamed: 9
- Unnamed: 10
- Unnamed: 11
- Unnamed: 12
- Unnamed: 13
- Unnamed: 14
- Unnamed: 15
- Unnamed: 16
- Unnamed: 17
- Unnamed: 18
- Unnamed: 19
- Unnamed: 20
- Unnamed: 21
- Unnamed: 22
- Unnamed: 23
- Unnamed: 24
- Unnamed: 25
- Unnamed: 26
- Unnamed: 27
- Unnamed: 28
- Unnamed: 29
**Tipi rilevati (sample):**
- Unnamed: 0: object
- MENU: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
- Unnamed: 5: object
- Unnamed: 6: object
- Unnamed: 7: object
- Unnamed: 8: object
- Unnamed: 9: object
- Unnamed: 10: object
- Unnamed: 11: object
- Unnamed: 12: object
- Unnamed: 13: object
- Unnamed: 14: object
- Unnamed: 15: object
- Unnamed: 16: object
- Unnamed: 17: object
- Unnamed: 18: object
- Unnamed: 19: object
**Valori nulli (sample):**
- Unnamed: 0: 33
- MENU: 32
- Unnamed: 2: 31
- Unnamed: 3: 22
- Unnamed: 4: 32
- Unnamed: 5: 28
- Unnamed: 6: 20
- Unnamed: 7: 19
- Unnamed: 8: 19
- Unnamed: 9: 19
- Unnamed: 10: 19
- Unnamed: 11: 19
- Unnamed: 12: 19
- Unnamed: 13: 19
- Unnamed: 14: 19
- Unnamed: 15: 19
- Unnamed: 16: 19
- Unnamed: 17: 19
- Unnamed: 18: 19
- Unnamed: 19: 19
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+'Banca-mese'!B2`
- `=+'Banca-mese'!C2`
- `=+'Banca-mese'!D2`
- `=+'Banca-mese'!E2`
- `=+'Banca-mese'!F2`
- `=+'Banca-mese'!G2`
- `=+'Banca-mese'!H2`
- `=+'Banca-mese'!I2`
- `=+'Banca-mese'!J2`
- `=+'Banca-mese'!K2`

### I_Ult CE
**Colonne (prime 30):**
- Unnamed: 0
- Unnamed: 1
- Unnamed: 2
- Unnamed: 3
- Unnamed: 4
**Tipi rilevati (sample):**
- Unnamed: 0: object
- Unnamed: 1: object
- Unnamed: 2: object
- Unnamed: 3: object
- Unnamed: 4: object
**Valori nulli (sample):**
- Unnamed: 0: 62
- Unnamed: 1: 46
- Unnamed: 2: 49
- Unnamed: 3: 62
- Unnamed: 4: 60
**Data validations:** 0
**Tabelle Excel:** _(nessuna)_
**Esempi formule:**
- `=+E4-E5`
- `=+E2-E6`
- `=+'CE-mese'!A19`
- `=+'CE-mese'!A20`
- `=+'CE-mese'!A21`
- `=+'CE-mese'!A22`
- `=+'CE-mese'!A23`
- `=+'CE-mese'!A24`
- `=+'CE-mese'!A25`
- `=+'CE-mese'!A26`
