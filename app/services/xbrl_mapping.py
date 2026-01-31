# app/services/xbrl_mapping.py
"""Mapping statico IFRS concept -> riclass code per SP e CE."""

from typing import Optional, Tuple

# ─── SP (Stato Patrimoniale) ─────────────────────────────────────
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
}

# ─── CE (Conto Economico) ────────────────────────────────────────
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
}


def classify_xbrl_fact(concept: str) -> Optional[Tuple[str, str, str]]:
    """
    Classifica un concept XBRL IFRS.

    Ritorna (tipo, riclass_code, riclass_desc) o None se non mappato.
    tipo = "SP" | "CE"
    """
    if not concept:
        return None

    # Normalizza: rimuove eventuale prefisso namespace URI
    # I concept possono arrivare come "ifrs-full:Revenue" o solo "Revenue"
    key = concept
    if ":" not in key:
        key = f"ifrs-full:{key}"

    if key in IFRS_TO_SP_RICLASS:
        code, desc = IFRS_TO_SP_RICLASS[key]
        return ("SP", code, desc)
    if key in IFRS_TO_CE_RICLASS:
        code, desc = IFRS_TO_CE_RICLASS[key]
        return ("CE", code, desc)

    return None
