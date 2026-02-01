# app/services/xbrl_mapping.py
"""Mapping statico IFRS + IT-GAAP (OIC) concept -> riclass code per SP e CE."""

import re
from typing import Optional, Tuple

# ─── SP (Stato Patrimoniale) — IFRS ─────────────────────────────
IFRS_TO_SP_RICLASS: dict[str, tuple[str, str]] = {
    # Attivo corrente
    "ifrs-full:CashAndCashEquivalents": ("LIQUIDITA_E_ESIGIBILITA_IMMEDIATE", "Disponibilita' liquide"),
    "ifrs-full:Cash": ("LIQUIDITA_E_ESIGIBILITA_IMMEDIATE", "Cassa"),
    "ifrs-full:TradeAndOtherCurrentReceivables": ("CREDITI", "Crediti commerciali"),
    "ifrs-full:TradeReceivables": ("CREDITI", "Crediti vs clienti"),
    "ifrs-full:CurrentTradeReceivables": ("CREDITI", "Crediti commerciali correnti"),
    "ifrs-full:OtherCurrentReceivables": ("CREDITI", "Altri crediti correnti"),
    "ifrs-full:CurrentTaxAssets": ("CREDITI", "Crediti tributari correnti"),
    "ifrs-full:Inventories": ("RIMANENZE", "Rimanenze"),
    "ifrs-full:RawMaterials": ("RIMANENZE", "Materie prime"),
    "ifrs-full:FinishedGoods": ("RIMANENZE", "Prodotti finiti"),
    "ifrs-full:OtherCurrentFinancialAssets": ("CREDITI", "Altre attivita' finanziarie correnti"),
    "ifrs-full:PrepaidExpenses": ("CREDITI", "Risconti attivi"),
    "ifrs-full:CurrentAssets": ("CREDITI", "Totale attivo corrente"),
    # Attivo non corrente
    "ifrs-full:IntangibleAssetsOtherThanGoodwill": ("IMMOBILIZZAZIONI_IMMATERIALI", "Immob. immateriali"),
    "ifrs-full:IntangibleAssets": ("IMMOBILIZZAZIONI_IMMATERIALI", "Immob. immateriali totali"),
    "ifrs-full:Goodwill": ("IMMOBILIZZAZIONI_IMMATERIALI", "Avviamento"),
    "ifrs-full:PropertyPlantAndEquipment": ("IMMOBILIZZAZIONI_MATERIALI", "Immob. materiali"),
    "ifrs-full:Land": ("IMMOBILIZZAZIONI_MATERIALI", "Terreni"),
    "ifrs-full:Buildings": ("IMMOBILIZZAZIONI_MATERIALI", "Fabbricati"),
    "ifrs-full:Machinery": ("IMMOBILIZZAZIONI_MATERIALI", "Macchinari"),
    "ifrs-full:RightofuseAssets": ("IMMOBILIZZAZIONI_MATERIALI", "Diritti d'uso (IFRS 16)"),
    "ifrs-full:InvestmentProperty": ("IMMOBILIZZAZIONI_MATERIALI", "Investimenti immobiliari"),
    "ifrs-full:OtherNoncurrentFinancialAssets": ("IMMOBILIZZAZIONI_FINANZIARIE", "Immob. finanziarie"),
    "ifrs-full:NoncurrentFinancialAssets": ("IMMOBILIZZAZIONI_FINANZIARIE", "Attivita' finanziarie non correnti"),
    "ifrs-full:InvestmentsInSubsidiaries": ("IMMOBILIZZAZIONI_FINANZIARIE", "Partecipazioni controllate"),
    "ifrs-full:InvestmentsInAssociates": ("IMMOBILIZZAZIONI_FINANZIARIE", "Partecipazioni collegate"),
    "ifrs-full:DeferredTaxAssets": ("CREDITI", "Imposte anticipate"),
    "ifrs-full:NoncurrentAssets": ("IMMOBILIZZAZIONI_MATERIALI", "Totale attivo non corrente"),
    "ifrs-full:Assets": ("CREDITI", "Totale attivo"),
    # Passivo corrente
    "ifrs-full:TradeAndOtherCurrentPayables": ("DEBITI", "Debiti vs fornitori"),
    "ifrs-full:TradePayables": ("DEBITI", "Debiti commerciali"),
    "ifrs-full:CurrentTradePayables": ("DEBITI", "Debiti commerciali correnti"),
    "ifrs-full:OtherCurrentPayables": ("DEBITI", "Altri debiti correnti"),
    "ifrs-full:ShorttermBorrowings": ("DEBITI", "Debiti vs banche breve"),
    "ifrs-full:CurrentBorrowings": ("DEBITI", "Finanziamenti correnti"),
    "ifrs-full:CurrentTaxLiabilities": ("DEBITI", "Debiti tributari correnti"),
    "ifrs-full:CurrentLeaseLiabilities": ("DEBITI", "Debiti leasing correnti"),
    "ifrs-full:CurrentLiabilities": ("DEBITI", "Totale passivo corrente"),
    # Passivo non corrente
    "ifrs-full:NoncurrentPortionOfNoncurrentBorrowings": ("DEBITI", "Debiti lungo termine"),
    "ifrs-full:NoncurrentBorrowings": ("DEBITI", "Finanziamenti non correnti"),
    "ifrs-full:NoncurrentLeaseLiabilities": ("DEBITI", "Debiti leasing non correnti"),
    "ifrs-full:EmployeeBenefits": ("FONDI", "TFR e fondi personale"),
    "ifrs-full:Provisions": ("FONDI", "Fondi rischi e oneri"),
    "ifrs-full:NoncurrentProvisions": ("FONDI", "Fondi non correnti"),
    "ifrs-full:DeferredTaxLiabilities": ("FONDI", "Imposte differite"),
    "ifrs-full:NoncurrentLiabilities": ("DEBITI", "Totale passivo non corrente"),
    "ifrs-full:Liabilities": ("DEBITI", "Totale passivo"),
    # Patrimonio netto
    "ifrs-full:Equity": ("CAPITALE", "Patrimonio netto"),
    "ifrs-full:EquityAttributableToOwnersOfParent": ("CAPITALE", "PN di pertinenza"),
    "ifrs-full:IssuedCapital": ("CAPITALE", "Capitale sociale"),
    "ifrs-full:SharePremium": ("CAPITALE", "Sovrapprezzo azioni"),
    "ifrs-full:RetainedEarnings": ("UTILE_PERDITA_A_NUOVO", "Utili a nuovo"),
    "ifrs-full:OtherReserves": ("CAPITALE", "Altre riserve"),
    "ifrs-full:RevaluationSurplus": ("CAPITALE", "Riserva rivalutazione"),
    "ifrs-full:TreasuryShares": ("CAPITALE", "Azioni proprie"),
    "ifrs-full:ProfitLoss": ("UTILE_PERDITA_ESERCIZIO", "Utile/perdita esercizio"),
    "ifrs-full:ProfitLossAttributableToOwnersOfParent": ("UTILE_PERDITA_ESERCIZIO", "Utile di pertinenza"),
    "ifrs-full:NoncontrollingInterests": ("CAPITALE", "Interessi di minoranza"),
    # ── Settore bancario / finanziario (IFRS) ──
    "ifrs-full:FinancialAssetsAtAmortisedCost": ("CREDITI", "Att. finanziarie a costo ammort."),
    "ifrs-full:FinancialAssetsAtFairValueThroughProfitOrLoss": ("CREDITI", "Att. fin. FVTPL"),
    "ifrs-full:FinancialAssetsAtFairValueThroughProfitOrLossClassifiedAsHeldForTrading": ("CREDITI", "Att. fin. trading"),
    "ifrs-full:FinancialAssetsAtFairValueThroughProfitOrLossDesignatedAsUponInitialRecognition": ("CREDITI", "Att. fin. designate FVTPL"),
    "ifrs-full:FinancialAssetsAtFairValueThroughProfitOrLossMandatorilyMeasuredAtFairValue": ("CREDITI", "Att. fin. obblig. FVTPL"),
    "ifrs-full:FinancialAssetsMeasuredAtFairValueThroughOtherComprehensiveIncome": ("IMMOBILIZZAZIONI_FINANZIARIE", "Att. fin. FVOCI"),
    "ifrs-full:LoansAndAdvancesToCustomers": ("CREDITI", "Crediti vs clientela"),
    "ifrs-full:LoansAndAdvancesToBanks": ("CREDITI", "Crediti vs banche"),
    "ifrs-full:DebtSecurities": ("IMMOBILIZZAZIONI_FINANZIARIE", "Titoli di debito"),
    "ifrs-full:DerivativeFinancialAssetsHeldForHedging": ("CREDITI", "Derivati attivi di copertura"),
    "ifrs-full:InvestmentAccountedForUsingEquityMethod": ("IMMOBILIZZAZIONI_FINANZIARIE", "Partecipazioni equity method"),
    "ifrs-full:IntangibleAssetsAndGoodwill": ("IMMOBILIZZAZIONI_IMMATERIALI", "Immob. immateriali e avviamento"),
    "ifrs-full:OtherAssets": ("CREDITI", "Altre attivita'"),
    "ifrs-full:NoncurrentAssetsOrDisposalGroupsClassifiedAsHeldForSale": ("CREDITI", "Att. non correnti in dismissione"),
    "ifrs-full:InsuranceContractsIssuedThatAreAssets": ("CREDITI", "Contratti assicurativi (attivo)"),
    "ifrs-full:ReinsuranceContractsHeldThatAreAssets": ("CREDITI", "Contratti riass. (attivo)"),
    "ifrs-full:EquityAndLiabilities": ("DEBITI", "Totale passivo e PN"),
    "ifrs-full:DepositsFromBanks": ("DEBITI", "Debiti vs banche (depositi)"),
    "ifrs-full:DepositsFromCustomers": ("DEBITI", "Debiti vs clientela (depositi)"),
    "ifrs-full:FinancialLiabilitiesAtAmortisedCost": ("DEBITI", "Pass. finanziarie costo ammort."),
    "ifrs-full:FinancialLiabilitiesAtFairValueThroughProfitOrLossClassifiedAsHeldForTrading": ("DEBITI", "Pass. fin. trading"),
    "ifrs-full:FinancialLiabilitiesAtFairValueThroughProfitOrLossDesignatedAsUponInitialRecognition": ("DEBITI", "Pass. fin. designate FVTPL"),
    "ifrs-full:DerivativeFinancialLiabilitiesHeldForHedging": ("DEBITI", "Derivati passivi di copertura"),
    "ifrs-full:OtherLiabilities": ("DEBITI", "Altre passivita'"),
    "ifrs-full:InsuranceContractsIssuedThatAreLiabilities": ("DEBITI", "Contratti assicurativi (passivo)"),
    "ifrs-full:ReinsuranceContractsHeldThatAreLiabilities": ("DEBITI", "Contratti riass. (passivo)"),
    "ifrs-full:LiabilitiesIncludedInDisposalGroupsClassifiedAsHeldForSale": ("DEBITI", "Pass. in dismissione"),
    "ifrs-full:ProfitLossAttributableToNoncontrollingInterests": ("UTILE_PERDITA_ESERCIZIO", "Utile di terzi"),
    # ── Concept specifici ISP (Intesa Sanpaolo) ──
    "isp:TotalEquity": ("CAPITALE", "Totale patrimonio netto"),
    "isp:TotalEquityAttributableToOwnersOfParent": ("CAPITALE", "PN di pertinenza"),
    "isp:TotalNoncontrollingInterests": ("CAPITALE", "Interessi di minoranza"),
    "isp:TangibleAssets": ("IMMOBILIZZAZIONI_MATERIALI", "Attivita' materiali"),
    "isp:TaxAssets": ("CREDITI", "Attivita' fiscali"),
    "isp:TaxLiabilities": ("DEBITI", "Passivita' fiscali"),
    "isp:InsuranceAssets": ("CREDITI", "Attivita' assicurative"),
    "isp:InsuranceLiabilities": ("DEBITI", "Passivita' assicurative"),
    "isp:ProvisionForEmployeeSeverancesPay": ("FONDI", "TFR"),
    "isp:PostRetirementBenefitObligation": ("FONDI", "Fondi pensione"),
    "isp:OtherProvisionsForRiskAndCharges": ("FONDI", "Altri fondi rischi e oneri"),
    "isp:ProvisionForCommittmentsAndGuaranteesGiven": ("FONDI", "Fondi garanzie e impegni"),
    "isp:ValuationReserve": ("CAPITALE", "Riserve di valutazione"),
    "isp:OtherReservesOther": ("CAPITALE", "Altre riserve"),
    "isp:EquityInstrument": ("CAPITALE", "Strumenti di capitale"),
    "isp:RedeemableShares": ("CAPITALE", "Azioni rimborsabili"),
    "isp:OfWhichGoodwill": ("IMMOBILIZZAZIONI_IMMATERIALI", "di cui: avviamento"),
    "isp:InterimDividend": ("UTILE_PERDITA_ESERCIZIO", "Acconto dividendi"),
    "isp:ProfitOrLossAttributableToOwnersOfParent": ("UTILE_PERDITA_ESERCIZIO", "Utile di pertinenza"),
}

# ─── CE (Conto Economico) — IFRS ────────────────────────────────
IFRS_TO_CE_RICLASS: dict[str, tuple[str, str]] = {
    "ifrs-full:Revenue": ("RICAVI", "Ricavi"),
    "ifrs-full:RevenueFromContractsWithCustomers": ("RICAVI", "Ricavi da contratti"),
    "ifrs-full:OtherIncome": ("RICAVI", "Altri ricavi"),
    "ifrs-full:CostOfSales": ("MATERIE_PRIME_E_MERCI", "Costi materie prime"),
    "ifrs-full:CostOfMerchandiseSold": ("MATERIE_PRIME_E_MERCI", "Costo merci vendute"),
    "ifrs-full:RawMaterialsAndConsumablesUsed": ("MATERIE_PRIME_E_MERCI", "Materie prime consumate"),
    "ifrs-full:InventoryWritedown": ("MATERIE_PRIME_E_MERCI", "Svalutazione rimanenze"),
    "ifrs-full:EmployeeBenefitsExpense": ("COSTI_PERSONALE", "Costi del personale"),
    "ifrs-full:WagesAndSalaries": ("COSTI_PERSONALE", "Salari e stipendi"),
    "ifrs-full:SocialSecurityContributions": ("COSTI_PERSONALE", "Contributi sociali"),
    "ifrs-full:DepreciationAndAmortisationExpense": ("AMMORTAMENTI_MATERIALI", "Ammortamenti"),
    "ifrs-full:DepreciationExpense": ("AMMORTAMENTI_MATERIALI", "Ammortamenti materiali"),
    "ifrs-full:AmortisationExpense": ("AMMORTAMENTI_IMMATERIALI", "Ammortamenti immateriali"),
    "ifrs-full:ImpairmentLoss": ("AMMORTAMENTI_MATERIALI", "Svalutazioni"),
    "ifrs-full:OtherExpenseByNature": ("SERVIZI", "Servizi e altri costi"),
    "ifrs-full:OtherExpense": ("SERVIZI", "Altre spese operative"),
    "ifrs-full:AdministrativeExpense": ("SERVIZI", "Spese amministrative"),
    "ifrs-full:SellingExpense": ("SERVIZI", "Spese commerciali"),
    "ifrs-full:DistributionCosts": ("SERVIZI", "Costi distribuzione"),
    "ifrs-full:FinanceIncome": ("PROVENTI_FINANZIARI", "Proventi finanziari"),
    "ifrs-full:InterestIncomeOnFinancialAssets": ("PROVENTI_FINANZIARI", "Interessi attivi"),
    "ifrs-full:FinanceCosts": ("ONERI_FINANZIARI", "Oneri finanziari"),
    "ifrs-full:InterestExpense": ("ONERI_FINANZIARI", "Interessi passivi"),
    "ifrs-full:InterestExpenseOnBorrowings": ("ONERI_FINANZIARI", "Interessi su finanziamenti"),
    "ifrs-full:IncomeTaxExpenseContinuingOperations": ("IMPOSTE", "Imposte sul reddito"),
    "ifrs-full:CurrentTaxExpense": ("IMPOSTE", "Imposte correnti"),
    "ifrs-full:DeferredTaxExpenseIncome": ("IMPOSTE", "Imposte differite"),
    "ifrs-full:ProfitLossFromOperatingActivities": ("RICAVI", "Risultato operativo"),
    "ifrs-full:ProfitLossBeforeTax": ("RICAVI", "Risultato ante imposte"),
    "ifrs-full:ProfitLossFromContinuingOperations": ("RICAVI", "Risultato att. in funzionamento"),
    "ifrs-full:ProfitLossFromDiscontinuedOperations": ("RICAVI", "Risultato att. dismesse"),
    # ── Settore bancario / finanziario (IFRS) ──
    "ifrs-full:InterestRevenueCalculatedUsingEffectiveInterestMethod": ("RICAVI", "Interessi attivi (eff. interest)"),
    "ifrs-full:FeeAndCommissionIncome": ("RICAVI", "Commissioni attive"),
    "ifrs-full:FeeAndCommissionExpense": ("SERVIZI", "Commissioni passive"),
    "ifrs-full:FeeAndCommissionIncomeExpense": ("RICAVI", "Commissioni nette"),
    "ifrs-full:TradingIncomeExpense": ("RICAVI", "Risultato negoziazione"),
    "ifrs-full:RevenueFromDividends": ("PROVENTI_FINANZIARI", "Dividendi percepiti"),
    "ifrs-full:InsuranceRevenue": ("RICAVI", "Ricavi assicurativi"),
    "ifrs-full:InsuranceServiceExpensesFromInsuranceContractsIssued": ("SERVIZI", "Costi servizio assicurativo"),
    "ifrs-full:InsuranceServiceResult": ("RICAVI", "Risultato servizio assicurativo"),
    "ifrs-full:InsuranceFinanceIncomeExpensesFromInsuranceContractsIssuedRecognisedInProfitOrLoss": ("PROVENTI_FINANZIARI", "Risultato fin. assicurativo"),
    "ifrs-full:FinanceIncomeExpensesFromReinsuranceContractsHeldRecognisedInProfitOrLoss": ("PROVENTI_FINANZIARI", "Risultato fin. riassicurativo"),
    "ifrs-full:ImpairmentLossImpairmentGainAndReversalOfImpairmentLossDeterminedInAccordanceWithIFRS9": ("AMMORTAMENTI_MATERIALI", "Rettifiche/riprese IFRS 9"),
    "ifrs-full:ShareOfProfitLossOfAssociatesAndJointVenturesAccountedForUsingEquityMethod": ("PROVENTI_FINANZIARI", "Quota utili partecipate"),
    "ifrs-full:GainsLossesOnDisposalsOfInvestments": ("PROVENTI_FINANZIARI", "Utili/perdite cessione investimenti"),
    "ifrs-full:OtherOperatingIncomeExpense": ("RICAVI", "Altri proventi/oneri di gestione"),
    "ifrs-full:ComprehensiveIncome": ("RICAVI", "Risultato complessivo"),
    "ifrs-full:ComprehensiveIncomeAttributableToOwnersOfParent": ("RICAVI", "Risultato complessivo di pertinenza"),
    "ifrs-full:ComprehensiveIncomeAttributableToNoncontrollingInterests": ("RICAVI", "Risultato complessivo di terzi"),
    "ifrs-full:BasicEarningsLossPerShare": ("RICAVI", "Utile per azione base"),
    "ifrs-full:DilutedEarningsLossPerShare": ("RICAVI", "Utile per azione diluito"),
    # ── Concept specifici ISP (Intesa Sanpaolo) CE ──
    "isp:InterestIncomeAndSimilarRevenues": ("RICAVI", "Interessi attivi e proventi sim."),
    "isp:InterestExpenseAndSimilarCharges": ("ONERI_FINANZIARI", "Interessi passivi e oneri sim."),
    "isp:NetInterestMargin": ("RICAVI", "Margine d'interesse"),
    "isp:GrossIncome": ("RICAVI", "Margine di intermediazione"),
    "isp:NetProfitFromFinancialActivities": ("RICAVI", "Risultato netto att. finanziarie"),
    "isp:ProfitLossFromFinancialAndInsuranceActivities": ("RICAVI", "Risultato att. fin. e assicur."),
    "isp:OperatingCosts": ("SERVIZI", "Costi operativi"),
    "isp:AdministrativeExpenseStaffCosts": ("COSTI_PERSONALE", "Spese per il personale"),
    "isp:OtherAdministrativeExpense": ("SERVIZI", "Altre spese amministrative"),
    "isp:NetValueAdjustmentsWriteBacksOnTangibleAndIntangibleAssets": ("AMMORTAMENTI_MATERIALI", "Rettifiche su att. materiali e immat."),
    "isp:NetProvisionsForRisksAndCharges": ("FONDI", "Accantonamenti netti fondi rischi"),
    "isp:NetProvisionsForRisksAndChargesAndOtherExpensesIncome": ("SERVIZI", "Accantonamenti e altri oneri/proventi"),
    "isp:NetProvisionsForRisksAndChargesCommitmentsAndFinancialGuaranteesGiven": ("FONDI", "Accantonamenti garanzie"),
    "isp:NetProvisionsForRisksAndChargesOtherNetProvision": ("FONDI", "Altri accantonamenti netti"),
    "isp:NetLossesRecoveriesOnCreditImpairment": ("AMMORTAMENTI_MATERIALI", "Rettifiche/riprese per rischio credito"),
    "isp:GainLossOnFinancialAssetsHeldForTradingAndOnOtherFinancialAssetsLiabilitiesAtFairValueThroughProfitOrLoss": ("PROVENTI_FINANZIARI", "Risultato att. fin. trading/FVTPL"),
    "isp:GainsLossesOnFinancialAssetsLiabilitiesMandatorilyAtFairValueThroughProfitOrLoss": ("PROVENTI_FINANZIARI", "Risultato att. obblig. FVTPL"),
    "isp:GainsLossesOnFinancialAssetsLiabilitiesDesignatedAtFairValueThroughProfitOrLoss": ("PROVENTI_FINANZIARI", "Risultato att. designate FVTPL"),
    "isp:NetGainsLossesOnOtherFinancialAssetsLiabilitiesAtFairValueThroughProfitOrLoss": ("PROVENTI_FINANZIARI", "Risultato altre att. FVTPL"),
    "isp:GainsLossesOnDisposalsandRepurchaseOfFinancialAssetsandLiabilities": ("PROVENTI_FINANZIARI", "Utili/perdite cessione att./pass. fin."),
    "isp:GainLossOnDisposalOfFinancialAssetsAtFairValueThroughOtherComprehensiveIncome": ("PROVENTI_FINANZIARI", "Utili/perdite cessione FVOCI"),
    "isp:GainLossArisingFromDisposalOfFinancialAssetsMeasuredAtAmortisedCost": ("PROVENTI_FINANZIARI", "Utili/perdite cessione costo ammort."),
    "isp:GainLossArisingFromRepurchaseOfFinancialLiabilities": ("PROVENTI_FINANZIARI", "Utili/perdite riacquisto passivita'"),
    "isp:GainLossOnHedgeAccounting": ("PROVENTI_FINANZIARI", "Risultato coperture"),
    "isp:NetGainsLossesFromHedgeAccounting": ("PROVENTI_FINANZIARI", "Risultato netto coperture"),
    "isp:ImpairmentLossImpairmentGainAndReversalOfImpairmentLossDeterminedInAccordanceWithIFRS9OnFinancialAssetsAtAmortisedCost": ("AMMORTAMENTI_MATERIALI", "Rettifiche IFRS9 costo ammort."),
    "isp:ImpairmentLossImpairmentGainAndReversalOfImpairmentLossDeterminedInAccordanceWithIFRS9OnFinancialAssetsAtFairValueThroughOtherComprehensiveIncome": ("AMMORTAMENTI_MATERIALI", "Rettifiche IFRS9 FVOCI"),
    "isp:GoodwillImpairment": ("AMMORTAMENTI_IMMATERIALI", "Svalutazione avviamento"),
    "isp:DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLossTangibleAssets": ("AMMORTAMENTI_MATERIALI", "Ammort. e rettifiche att. materiali"),
    "isp:DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLossIntangibleAssetsOtherThanGoodwill": ("AMMORTAMENTI_IMMATERIALI", "Ammort. e rettifiche att. immateriali"),
    "isp:GainsLossesOnTangibleAndIntangibleAssetsOtherThanGoodwillMeasuredAtFairValue": ("PROVENTI_FINANZIARI", "Risultato att. mat./immat. a FV"),
    "isp:UnpaidDutiesTaxesAndTaxCredits": ("IMPOSTE", "Imposte e tasse non pagate"),
    "isp:GainsLossesFromContractualChangesWithoutDerecognition": ("PROVENTI_FINANZIARI", "Utili/perdite modif. contrattuali"),
    "isp:BalanceOfFinanceIncomeExpensesFromInsuranceActivities": ("PROVENTI_FINANZIARI", "Saldo proventi/oneri fin. assicur."),
    "isp:NetRevenuesAndCostsOfInsuranceContractsIssuedAndReinsuranceCeded": ("RICAVI", "Ricavi/costi netti contratti assicur."),
    "isp:IncomeFromReinsuranceContractsHeld": ("RICAVI", "Proventi riassicurazione"),
    "isp:ExpensesFromReinsuranceContractsHeld": ("SERVIZI", "Costi riassicurazione"),
    "isp:ImpairmentWriteBacksAfterTaxOnDiscontinuedOperations": ("RICAVI", "Rettifiche att. dismesse"),
}

# ─── SP (Stato Patrimoniale) — IT-GAAP / OIC (tassonomia itcc-ci) ───
ITCC_TO_SP_RICLASS: dict[str, tuple[str, str]] = {
    # Crediti verso soci
    "itcc-ci:CredVersoci": ("CREDITI", "Crediti verso soci"),
    "itcc-ci:CredVSociPerVersAncoraDouvit": ("CREDITI", "Crediti vs soci per vers. dovuti"),
    # Immobilizzazioni
    "itcc-ci:TotaleImmobilizzazioniImmateriali": ("IMMOBILIZZAZIONI_IMMATERIALI", "Tot. immob. immateriali"),
    "itcc-ci:ImmobilizzazioniImmateriali": ("IMMOBILIZZAZIONI_IMMATERIALI", "Immob. immateriali"),
    "itcc-ci:CostiDiImpianto": ("IMMOBILIZZAZIONI_IMMATERIALI", "Costi di impianto"),
    "itcc-ci:CostiDiSviluppo": ("IMMOBILIZZAZIONI_IMMATERIALI", "Costi di sviluppo"),
    "itcc-ci:Avviamento": ("IMMOBILIZZAZIONI_IMMATERIALI", "Avviamento"),
    "itcc-ci:TotaleImmobilizzazioniMateriali": ("IMMOBILIZZAZIONI_MATERIALI", "Tot. immob. materiali"),
    "itcc-ci:ImmobilizzazioniMateriali": ("IMMOBILIZZAZIONI_MATERIALI", "Immob. materiali"),
    "itcc-ci:Terreni": ("IMMOBILIZZAZIONI_MATERIALI", "Terreni"),
    "itcc-ci:Fabbricati": ("IMMOBILIZZAZIONI_MATERIALI", "Fabbricati"),
    "itcc-ci:ImpiantiEMacchinario": ("IMMOBILIZZAZIONI_MATERIALI", "Impianti e macchinari"),
    "itcc-ci:TotaleImmobilizzazioniFinanziarie": ("IMMOBILIZZAZIONI_FINANZIARIE", "Tot. immob. finanziarie"),
    "itcc-ci:ImmobilizzazioniFinanziarie": ("IMMOBILIZZAZIONI_FINANZIARIE", "Immob. finanziarie"),
    "itcc-ci:Partecipazioni": ("IMMOBILIZZAZIONI_FINANZIARIE", "Partecipazioni"),
    "itcc-ci:TotaleImmobilizzazioni": ("IMMOBILIZZAZIONI_MATERIALI", "Tot. immobilizzazioni"),
    # Attivo circolante
    "itcc-ci:TotaleRimanenze": ("RIMANENZE", "Tot. rimanenze"),
    "itcc-ci:Rimanenze": ("RIMANENZE", "Rimanenze"),
    "itcc-ci:MateriePrime": ("RIMANENZE", "Materie prime"),
    "itcc-ci:ProdottiFiniti": ("RIMANENZE", "Prodotti finiti"),
    "itcc-ci:TotaleCrediti": ("CREDITI", "Tot. crediti"),
    "itcc-ci:CreditiVClienti": ("CREDITI", "Crediti vs clienti"),
    "itcc-ci:CreditiTributari": ("CREDITI", "Crediti tributari"),
    "itcc-ci:CreditiVersoAltri": ("CREDITI", "Crediti verso altri"),
    "itcc-ci:AttivitaFinanziarieNonImmobilizzate": ("CREDITI", "Attivita' fin. non immob."),
    "itcc-ci:DisponibilitaLiquide": ("LIQUIDITA_E_ESIGIBILITA_IMMEDIATE", "Disponibilita' liquide"),
    "itcc-ci:DepositiBancariEPostali": ("LIQUIDITA_E_ESIGIBILITA_IMMEDIATE", "Depositi bancari"),
    "itcc-ci:DenaroEValoriInCassa": ("LIQUIDITA_E_ESIGIBILITA_IMMEDIATE", "Denaro in cassa"),
    "itcc-ci:TotaleAttivoCircolante": ("CREDITI", "Tot. attivo circolante"),
    "itcc-ci:RateiERiscontiAttivi": ("CREDITI", "Ratei e risconti attivi"),
    "itcc-ci:TotaleAttivo": ("CREDITI", "Tot. attivo"),
    # Patrimonio netto
    "itcc-ci:PatrimonioNetto": ("CAPITALE", "Patrimonio netto"),
    "itcc-ci:TotalePatrimonioNetto": ("CAPITALE", "Tot. patrimonio netto"),
    "itcc-ci:CapitaleSociale": ("CAPITALE", "Capitale sociale"),
    "itcc-ci:Capitale": ("CAPITALE", "Capitale"),
    "itcc-ci:RiservaLegale": ("CAPITALE", "Riserva legale"),
    "itcc-ci:RiservaSovrapprezzo": ("CAPITALE", "Riserva sovrapprezzo"),
    "itcc-ci:AltreRiserve": ("CAPITALE", "Altre riserve"),
    "itcc-ci:RiservaRivalutazione": ("CAPITALE", "Riserva rivalutazione"),
    "itcc-ci:UtiliPerditaPortatiANuovo": ("UTILE_PERDITA_A_NUOVO", "Utili/perdite a nuovo"),
    "itcc-ci:UtilePerdita": ("UTILE_PERDITA_ESERCIZIO", "Utile/perdita esercizio"),
    "itcc-ci:UtilePerdEsercizio": ("UTILE_PERDITA_ESERCIZIO", "Utile/perdita esercizio"),
    # Fondi
    "itcc-ci:FondiPerRischiEdOneri": ("FONDI", "Fondi rischi e oneri"),
    "itcc-ci:FondiRischiOneri": ("FONDI", "Fondi rischi e oneri"),
    "itcc-ci:TFR": ("FONDI", "TFR"),
    "itcc-ci:TrattamentoFineRapporto": ("FONDI", "TFR"),
    # Debiti
    "itcc-ci:Debiti": ("DEBITI", "Debiti"),
    "itcc-ci:TotaleDebiti": ("DEBITI", "Tot. debiti"),
    "itcc-ci:DebitiVersoBanche": ("DEBITI", "Debiti vs banche"),
    "itcc-ci:DebitiVersoFornitori": ("DEBITI", "Debiti vs fornitori"),
    "itcc-ci:DebitiTributari": ("DEBITI", "Debiti tributari"),
    "itcc-ci:DebitiVIstitutiPrevidenzialiESicurezzaSociale": ("DEBITI", "Debiti previdenziali"),
    "itcc-ci:AltriDebiti": ("DEBITI", "Altri debiti"),
    "itcc-ci:RateiERiscontiPassivi": ("DEBITI", "Ratei e risconti passivi"),
    "itcc-ci:TotalePassivo": ("DEBITI", "Tot. passivo"),
}

# ─── CE (Conto Economico) — IT-GAAP / OIC (tassonomia itcc-ci) ──
ITCC_TO_CE_RICLASS: dict[str, tuple[str, str]] = {
    # Ricavi
    "itcc-ci:RicaviDelleVendite": ("RICAVI", "Ricavi delle vendite"),
    "itcc-ci:RicaviVenditeEPrestazioni": ("RICAVI", "Ricavi vendite e prestazioni"),
    "itcc-ci:AltriRicaviEProventi": ("RICAVI", "Altri ricavi e proventi"),
    "itcc-ci:ValoreDellaProduzione": ("RICAVI", "Valore della produzione"),
    "itcc-ci:TotaleValoreProduzione": ("RICAVI", "Tot. valore produzione"),
    # Costi produzione
    "itcc-ci:VariazioneRimanenze": ("MATERIE_PRIME_E_MERCI", "Variazione rimanenze"),
    "itcc-ci:VariazRimanenzeProdFiniti": ("MATERIE_PRIME_E_MERCI", "Var. rimanenze prod. finiti"),
    "itcc-ci:CostiMateriePrime": ("MATERIE_PRIME_E_MERCI", "Costi materie prime"),
    "itcc-ci:CostiMatPrimeSussConsMerci": ("MATERIE_PRIME_E_MERCI", "Costi mat. prime e merci"),
    "itcc-ci:CostiServizi": ("SERVIZI", "Costi per servizi"),
    "itcc-ci:CostiPerServizi": ("SERVIZI", "Costi per servizi"),
    "itcc-ci:CostiGodimentoBeniTerzi": ("SERVIZI", "Godimento beni terzi"),
    "itcc-ci:CostiPersonale": ("COSTI_PERSONALE", "Costi del personale"),
    "itcc-ci:CostoDelPersonale": ("COSTI_PERSONALE", "Costo del personale"),
    "itcc-ci:SalariEStipendi": ("COSTI_PERSONALE", "Salari e stipendi"),
    "itcc-ci:OneriSociali": ("COSTI_PERSONALE", "Oneri sociali"),
    "itcc-ci:Ammortamenti": ("AMMORTAMENTI_MATERIALI", "Ammortamenti"),
    "itcc-ci:AmmortamentiImmMateriali": ("AMMORTAMENTI_MATERIALI", "Ammort. immob. materiali"),
    "itcc-ci:AmmortamentiImmImmateriali": ("AMMORTAMENTI_IMMATERIALI", "Ammort. immob. immateriali"),
    "itcc-ci:AmmortamentiESvalutazioni": ("AMMORTAMENTI_MATERIALI", "Ammort. e svalutazioni"),
    "itcc-ci:Svalutazioni": ("AMMORTAMENTI_MATERIALI", "Svalutazioni"),
    "itcc-ci:OneriDiversiDiGestione": ("SERVIZI", "Oneri diversi di gestione"),
    "itcc-ci:TotaleCostiProduzione": ("SERVIZI", "Tot. costi produzione"),
    "itcc-ci:CostiDellaProduzione": ("SERVIZI", "Costi della produzione"),
    # Proventi e oneri finanziari
    "itcc-ci:ProventiOneriFinanziari": ("PROVENTI_FINANZIARI", "Proventi/oneri finanziari"),
    "itcc-ci:ProventiFinanziari": ("PROVENTI_FINANZIARI", "Proventi finanziari"),
    "itcc-ci:AltriProventiFinanziari": ("PROVENTI_FINANZIARI", "Altri proventi finanziari"),
    "itcc-ci:InteressiEAltriOneriFinanziari": ("ONERI_FINANZIARI", "Interessi e oneri finanziari"),
    "itcc-ci:OneriFinanziari": ("ONERI_FINANZIARI", "Oneri finanziari"),
    # Rettifiche e straordinari
    "itcc-ci:RettificheAttivitaFinanziarie": ("PROVENTI_FINANZIARI", "Rettifiche att. finanziarie"),
    "itcc-ci:ProventiOneriStraordinari": ("RICAVI", "Proventi/oneri straordinari"),
    # Imposte
    "itcc-ci:ImposteSulReddito": ("IMPOSTE", "Imposte sul reddito"),
    "itcc-ci:ImposteReddito": ("IMPOSTE", "Imposte sul reddito"),
    "itcc-ci:ImposteSulRedditoEsercizio": ("IMPOSTE", "Imposte reddito esercizio"),
    # Risultati intermedi
    "itcc-ci:DifferenzaValoreCostiProduzione": ("RICAVI", "Diff. valore/costi produzione"),
    "itcc-ci:RisultatoPrimaDelleImposte": ("RICAVI", "Risultato ante imposte"),
    "itcc-ci:UtilePerdEsercizio": ("RICAVI", "Utile/perdita esercizio"),
}

# ─── Indice unificato per lookup rapido per local name ───────────
# Costruisce un dict {local_name: (tipo, riclass_code, riclass_desc)}
# dove local_name e' la parte dopo ":" (es. "Revenue", "CostiServizi")
# In caso di conflitto, il primo vince (IFRS ha precedenza).
_LOCAL_NAME_INDEX: dict[str, tuple[str, str, str]] = {}


def _build_local_name_index():
    """Popola l'indice per local name da tutti i dizionari."""
    for concept, (code, desc) in IFRS_TO_SP_RICLASS.items():
        local = concept.split(":")[-1]
        if local not in _LOCAL_NAME_INDEX:
            _LOCAL_NAME_INDEX[local] = ("SP", code, desc)
    for concept, (code, desc) in IFRS_TO_CE_RICLASS.items():
        local = concept.split(":")[-1]
        if local not in _LOCAL_NAME_INDEX:
            _LOCAL_NAME_INDEX[local] = ("CE", code, desc)
    for concept, (code, desc) in ITCC_TO_SP_RICLASS.items():
        local = concept.split(":")[-1]
        if local not in _LOCAL_NAME_INDEX:
            _LOCAL_NAME_INDEX[local] = ("SP", code, desc)
    for concept, (code, desc) in ITCC_TO_CE_RICLASS.items():
        local = concept.split(":")[-1]
        if local not in _LOCAL_NAME_INDEX:
            _LOCAL_NAME_INDEX[local] = ("CE", code, desc)


_build_local_name_index()

# Regex per estrarre local name da namespace URI: {http://...}LocalName
_NS_URI_RE = re.compile(r"\{[^}]+\}(.+)")


def _normalize_concept(concept: str) -> str:
    """
    Normalizza un concept XBRL in forma prefix:localName o solo localName.

    Gestisce:
    - "{http://www.infocamere.it/...}NomeVoce" -> "NomeVoce"
    - "itcc-ci:NomeVoce" -> "itcc-ci:NomeVoce" (invariato)
    - "NomeVoce" -> "NomeVoce" (invariato)
    """
    m = _NS_URI_RE.match(concept)
    if m:
        return m.group(1)
    return concept


def classify_xbrl_fact(concept: str) -> Optional[Tuple[str, str, str]]:
    """
    Classifica un concept XBRL (IFRS o IT-GAAP).

    Ritorna (tipo, riclass_code, riclass_desc) o None se non mappato.
    tipo = "SP" | "CE"
    """
    if not concept:
        return None

    # Normalizza: rimuove eventuale namespace URI
    key = _normalize_concept(concept)

    # 1) Lookup diretto (concept gia' in forma prefix:localName)
    if key in IFRS_TO_SP_RICLASS:
        code, desc = IFRS_TO_SP_RICLASS[key]
        return ("SP", code, desc)
    if key in IFRS_TO_CE_RICLASS:
        code, desc = IFRS_TO_CE_RICLASS[key]
        return ("CE", code, desc)
    if key in ITCC_TO_SP_RICLASS:
        code, desc = ITCC_TO_SP_RICLASS[key]
        return ("SP", code, desc)
    if key in ITCC_TO_CE_RICLASS:
        code, desc = ITCC_TO_CE_RICLASS[key]
        return ("CE", code, desc)

    # 2) Se non ha prefisso, prova aggiungendo prefissi noti
    if ":" not in key:
        for prefix in ("ifrs-full", "itcc-ci"):
            prefixed = f"{prefix}:{key}"
            if prefixed in IFRS_TO_SP_RICLASS:
                code, desc = IFRS_TO_SP_RICLASS[prefixed]
                return ("SP", code, desc)
            if prefixed in IFRS_TO_CE_RICLASS:
                code, desc = IFRS_TO_CE_RICLASS[prefixed]
                return ("CE", code, desc)
            if prefixed in ITCC_TO_SP_RICLASS:
                code, desc = ITCC_TO_SP_RICLASS[prefixed]
                return ("SP", code, desc)
            if prefixed in ITCC_TO_CE_RICLASS:
                code, desc = ITCC_TO_CE_RICLASS[prefixed]
                return ("CE", code, desc)

        # 3) Fallback: lookup per local name nell'indice unificato
        if key in _LOCAL_NAME_INDEX:
            return _LOCAL_NAME_INDEX[key]
    else:
        # Ha un prefisso sconosciuto (es. "itcc-f:NomeVoce"): prova il local name
        local = key.split(":")[-1]
        if local in _LOCAL_NAME_INDEX:
            return _LOCAL_NAME_INDEX[local]

    return None


def get_all_mapped_concepts() -> set[str]:
    """Ritorna l'insieme di tutti i concept mappati (per diagnostica unmapped)."""
    all_concepts: set[str] = set()
    all_concepts.update(IFRS_TO_SP_RICLASS.keys())
    all_concepts.update(IFRS_TO_CE_RICLASS.keys())
    all_concepts.update(ITCC_TO_SP_RICLASS.keys())
    all_concepts.update(ITCC_TO_CE_RICLASS.keys())
    # Aggiungi anche i local name
    all_concepts.update(_LOCAL_NAME_INDEX.keys())
    return all_concepts
