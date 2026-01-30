# app/services/iva_settlement.py
"""
Liquidazione IVA:
  IVA debito (vendite) - IVA credito (acquisti)
  Pagamento con ritardo di 1 mese.
"""

from decimal import Decimal
from typing import List


def compute_iva_monthly(
    iva_debito_by_period: List[Decimal],
    iva_credito_by_period: List[Decimal],
    delay_months: int = 1,
) -> List[Decimal]:
    """
    Calcola il pagamento IVA mensile.

    Args:
        iva_debito_by_period: IVA a debito per ogni periodo
        iva_credito_by_period: IVA a credito per ogni periodo
        delay_months: ritardo di pagamento (default 1 mese)

    Returns:
        Lista di pagamenti IVA (positivo = pagamento, negativo = credito)
    """
    n = len(iva_debito_by_period)
    saldo_iva = []
    for i in range(n):
        debito = iva_debito_by_period[i] if i < len(iva_debito_by_period) else Decimal(0)
        credito = iva_credito_by_period[i] if i < len(iva_credito_by_period) else Decimal(0)
        saldo_iva.append(debito - credito)

    # Applica il ritardo
    pagamenti = [Decimal(0)] * n
    for i in range(n):
        target = i + delay_months
        if target < n:
            pagamenti[target] += saldo_iva[i]

    return pagamenti
