# app/services/timeline.py
"""Utility per costruire la timeline di piano (120 mesi max)."""

from dataclasses import dataclass
from typing import List


@dataclass
class PeriodInfo:
    """Informazioni su un singolo periodo mensile."""
    index: int          # 0-based
    year: int
    month: int          # 1-12
    label: str          # "Gen-2025", "Feb-2025", ...
    period_key: int     # YYYYMM  (es. 202501)

    @property
    def quarter(self) -> int:
        return (self.month - 1) // 3 + 1

    @property
    def is_year_end(self) -> bool:
        return self.month == 12


_MONTH_LABELS = [
    "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
    "Lug", "Ago", "Set", "Ott", "Nov", "Dic",
]


def build_timeline(
    start_year: int,
    start_month: int,
    duration: int = 120,
) -> List[PeriodInfo]:
    """
    Costruisce una lista di PeriodInfo da (start_year, start_month) per `duration` mesi.

    Args:
        start_year:  anno di inizio piano (es. 2025)
        start_month: mese di inizio piano (1-12)
        duration:    numero di mesi (default 120 = 10 anni)

    Returns:
        Lista ordinata di PeriodInfo con index 0..duration-1
    """
    periods: List[PeriodInfo] = []
    y, m = start_year, start_month
    for i in range(duration):
        label = f"{_MONTH_LABELS[m - 1]}-{y}"
        periods.append(PeriodInfo(
            index=i,
            year=y,
            month=m,
            label=label,
            period_key=y * 100 + m,
        ))
        # avanza di un mese
        m += 1
        if m > 12:
            m = 1
            y += 1
    return periods
