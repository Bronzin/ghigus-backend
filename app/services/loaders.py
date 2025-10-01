# app/services/loaders.py
import os
import csv
import re
from decimal import Decimal, InvalidOperation
from typing import Iterable, Dict, Optional, Tuple
from xml.etree import ElementTree as ET
from sqlalchemy import text
from sqlalchemy.orm import Session

STORAGE_ROOT = os.getenv("STORAGE_ROOT", "uploads")  # es. ./uploads

# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------
def _join_path(object_path: str) -> str:
    # Se è già assoluto, restituiscilo; altrimenti risolvi su STORAGE_ROOT
    if os.path.isabs(object_path):
        return object_path
    return os.path.abspath(os.path.join(STORAGE_ROOT, object_path))

def _to_decimal(val: str) -> Optional[Decimal]:
    if val is None:
        return None
    s = str(val).strip()
    if s == "":
        return None
    # gestisci formati EU: puntini migliaia e virgola decimale
    s = s.replace(" ", "").replace("\u00A0", "")
    s = re.sub(r"\.", "", s)  # togli separatore migliaia punti
    s = s.replace(",", ".")   # virgola -> punto
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

# ---------------------------------------------------------
# Upload lookup (DB → path file locale)
# ---------------------------------------------------------
def get_latest_upload_path(db: Session, case_slug: str, kinds: Tuple[str, ...]) -> Optional[str]:
    """
    Cerca nella tabella 'uploads' l'ultimo file per case/kind.
    kinds: tuple di possibili valori (case-insensitive), es: ('tb','trial_balance')
    Ritorna il path locale risolto (absolute) oppure None.
    """
    # Query robusta (senza ORM): kind case-insensitive
    sql = text("""
        SELECT object_path
        FROM uploads
        WHERE case_id = :slug
          AND lower(kind) = ANY(:kinds)
        ORDER BY created_at DESC
        LIMIT 1
    """)
    # postgres ARRAY binding
    kinds_lower = [k.lower() for k in kinds]
    row = db.execute(sql, {"slug": case_slug, "kinds": kinds_lower}).fetchone()
    if not row or not row[0]:
        return None
    return _join_path(row[0])

# ---------------------------------------------------------
# TB CSV parser
# ---------------------------------------------------------
def parse_tb_csv(file_path: str) -> Iterable[Dict]:
    """
    Atteso header: account_code,account_name,debit,credit
    """
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            code = (r.get("account_code") or r.get("Account") or r.get("code") or "").strip()
            name = (r.get("account_name") or r.get("Description") or r.get("name") or "").strip()
            debit = _to_decimal(r.get("debit") or r.get("Debit") or r.get("Dare"))
            credit = _to_decimal(r.get("credit") or r.get("Credit") or r.get("Avere"))
            if not code:
                continue
            yield {
                "account_code": code,
                "account_name": name or None,
                "debit": debit or Decimal(0),
                "credit": credit or Decimal(0),
            }

# ---------------------------------------------------------
# XBRL (XML) parser minimale
# ---------------------------------------------------------
def parse_xbrl_xml(file_path: str) -> Iterable[Dict]:
    """
    Estrae facts numerici con attributi principali + periodo dal context.
    Supporto minimale ma robusto per MVP.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Mappa contextRef → (instant | (start, end))
    ns = {}  # non servono namespace specifici per context/date
    contexts = {}
    for ctx in root.findall(".//{*}context", ns):
        cid = ctx.attrib.get("id")
        start = ctx.find(".//{*}startDate")
        end = ctx.find(".//{*}endDate")
        inst = ctx.find(".//{*}instant")
        contexts[cid] = {
            "start": start.text if start is not None else None,
            "end": end.text if end is not None else None,
            "instant": inst.text if inst is not None else None,
        }

    # Prendi elementi con valore numerico e contextRef
    # Evita di iterare <context>, <schemaRef>, ecc.
    for el in root.iter():
        if el.tag.endswith("context") or el.tag.endswith("schemaRef"):
            continue
        text_val = (el.text or "").strip()
        if text_val == "":
            continue
        # deve avere un contextRef per essere un fact
        ctx_ref = el.attrib.get("contextRef")
        if not ctx_ref:
            continue
        val = _to_decimal(text_val)
        if val is None:
            continue
        concept = el.tag  # include namespace
        unit = el.attrib.get("unitRef")
        decimals = el.attrib.get("decimals")
        period = contexts.get(ctx_ref, {})
        yield {
            "concept": concept,
            "context_ref": ctx_ref,
            "unit": unit,
            "decimals": decimals,
            "value": val,
            "instant": period.get("instant"),
            "start_date": period.get("start"),
            "end_date": period.get("end"),
        }
