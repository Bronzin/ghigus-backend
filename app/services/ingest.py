# app/services/ingest.py
from __future__ import annotations
import csv
import io
from typing import Dict, Any, List, Optional

def sniff_csv(text: str) -> csv.Dialect:
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(text[:2048])
    except Exception:
        class SimpleDialect(csv.excel):
            delimiter = ','
        dialect = SimpleDialect()
    return dialect

def parse_csv_bytes(data: bytes) -> Dict[str, Any]:
    """
    Ritorna KPI basilari a partire da un CSV:
    - rows: numero righe dati (escluse intestazioni, se presenti)
    - headers: lista colonne (se presenti)
    - total_amount: somma su una colonna 'amount'/'importo'/'value'/'valore'/'ricavi' se esiste
    """
    if not data:
        return {"rows": 0, "headers": [], "total_amount": None}

    text = data.decode("utf-8", errors="ignore")
    dialect = sniff_csv(text)
    f = io.StringIO(text)
    reader = csv.reader(f, dialect)

    rows: List[List[str]] = list(reader)
    if not rows:
        return {"rows": 0, "headers": [], "total_amount": None}

    headers: List[str] = []
    body: List[List[str]] = rows

    # prova a capire se la prima riga è header
    first = rows[0]
    looks_like_header = all(not cell.strip().isdigit() for cell in first)
    if looks_like_header:
        headers = [h.strip() for h in first]
        body = rows[1:]

    # prova a trovare una colonna “importi”
    candidates = {"amount", "importo", "value", "valore", "ricavi", "revenue", "revenues"}
    amount_idx: Optional[int] = None
    if headers:
        lower = [h.lower() for h in headers]
        for i, h in enumerate(lower):
            if h in candidates:
                amount_idx = i
                break

    total_amount: Optional[float] = None
    if amount_idx is not None:
        s = 0.0
        for r in body:
            try:
                # cambia eventuali virgole decimali
                val = r[amount_idx].replace(".", "").replace(",", ".")
                s += float(val)
            except Exception:
                continue
        total_amount = round(s, 2)

    return {
        "rows": len(body),
        "headers": headers,
        "total_amount": total_amount,
    }
