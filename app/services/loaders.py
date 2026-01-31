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
    Legge il Bilancio Contabile (BC) da CSV.

    Colonne attese (case-insensitive, alias supportati):
      - account_code  (alias: Account, code)
      - account_name  (alias: Description, name)
      - debit         (alias: Debit, Dare)
      - credit        (alias: Credit, Avere)
      - amount        (alias: Amount, importo, valore, value, revenues, ricavi)  [opzionale]
      - period_end    (alias: date, data, periodend, period-end)                 [opzionale]

    Regola importi:
      entry_amount = COALESCE(amount, credit - debit)
    """
    import csv
    from typing import Optional
    from decimal import Decimal

    # 1) Sniff delimitatore (virgola / punto e virgola) mantenendo utf-8-sig
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=";,")
            delimiter = dialect.delimiter
        except Exception:
            delimiter = ","  # fallback

        reader = csv.DictReader(f, delimiter=delimiter)
        for r in reader:
            # --- Normalizzazione campi base
            code = (r.get("account_code") or r.get("Account") or r.get("code") or "").strip()
            if not code:
                continue

            name_raw = (r.get("account_name") or r.get("Description") or r.get("name") or "")
            name = name_raw.strip() or None

            debit = _to_decimal(r.get("debit") or r.get("Debit") or r.get("Dare"))
            credit = _to_decimal(r.get("credit") or r.get("Credit") or r.get("Avere"))

            # --- amount opzionale: usa se presente e parsabile
            raw_amount = (
                r.get("amount")  or r.get("Amount")  or r.get("importo") or r.get("valore")
                or r.get("value") or r.get("revenues") or r.get("ricavi")
            )
            amount: Optional[Decimal] = _to_decimal(raw_amount) if raw_amount not in (None, "") else None

            # --- period_end opzionale (lascia stringa così com'è; validazione a valle)
            period_end = (
                r.get("period_end") or r.get("date") or r.get("data")
                or r.get("periodend") or r.get("period-end") or ""
            )
            period_end = period_end.strip() or None

            # --- entry amount: COALESCE(amount, credit - debit)
            entry_amount: Decimal = amount if amount is not None else (credit or Decimal(0)) - (debit or Decimal(0))

            yield {
                "account_code": code,
                "account_name": name,
                "debit": debit or Decimal(0),
                "credit": credit or Decimal(0),
                "amount": entry_amount,
                "period_end": period_end,
            }


# ---------------------------------------------------------
# XBRL: auto-detect dispatcher
# ---------------------------------------------------------
NS_IX = "http://www.xbrl.org/2013/inlineXBRL"
NS_XBRLI = "http://www.xbrl.org/2003/instance"
NS_XBRLDI = "http://xbrl.org/2006/xbrldi"


def _is_ixbrl(file_path: str) -> bool:
    """Rileva se il file è iXBRL (inline XBRL in XHTML)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".xhtml", ".html", ".htm"):
        return True
    # Controlla i primi 4KB per il namespace inlineXBRL
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(4096)
        return "inlineXBRL" in head or NS_IX in head
    except Exception:
        return False


def parse_xbrl_xml(file_path: str) -> Iterable[Dict]:
    """Dispatcher: rileva formato e delega al parser appropriato."""
    if _is_ixbrl(file_path):
        yield from _parse_ixbrl(file_path)
    else:
        yield from _parse_plain_xbrl(file_path)


# ---------------------------------------------------------
# Plain XBRL (XML) parser (codice originale)
# ---------------------------------------------------------
def _parse_plain_xbrl(file_path: str) -> Iterable[Dict]:
    """
    Estrae facts numerici con attributi principali + periodo dal context.
    Supporto minimale ma robusto per MVP.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {}
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

    for el in root.iter():
        if el.tag.endswith("context") or el.tag.endswith("schemaRef"):
            continue
        text_val = (el.text or "").strip()
        if text_val == "":
            continue
        ctx_ref = el.attrib.get("contextRef")
        if not ctx_ref:
            continue
        val = _to_decimal(text_val)
        if val is None:
            continue
        concept = el.tag
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


# ---------------------------------------------------------
# iXBRL parser (lxml)
# ---------------------------------------------------------
def _build_context_map(root) -> Dict[str, Dict]:
    """Estrae tutti xbrli:context → {id: {instant, start, end, dimensions}}."""
    from lxml import etree
    contexts = {}
    for ctx in root.iter(f"{{{NS_XBRLI}}}context"):
        cid = ctx.get("id")
        if not cid:
            continue

        instant = None
        start = None
        end = None
        period = ctx.find(f"{{{NS_XBRLI}}}period")
        if period is not None:
            inst_el = period.find(f"{{{NS_XBRLI}}}instant")
            if inst_el is not None and inst_el.text:
                instant = inst_el.text.strip()
            start_el = period.find(f"{{{NS_XBRLI}}}startDate")
            end_el = period.find(f"{{{NS_XBRLI}}}endDate")
            if start_el is not None and start_el.text:
                start = start_el.text.strip()
            if end_el is not None and end_el.text:
                end = end_el.text.strip()

        # Dimensioni (explicitMember dentro entity/segment)
        dimensions = {}
        segment = ctx.find(f"{{{NS_XBRLI}}}entity/{{{NS_XBRLI}}}segment")
        if segment is not None:
            for member in segment.iter(f"{{{NS_XBRLDI}}}explicitMember"):
                dim = member.get("dimension")
                val = (member.text or "").strip()
                if dim and val:
                    dimensions[dim] = val

        contexts[cid] = {
            "instant": instant,
            "start": start,
            "end": end,
            "dimensions": dimensions if dimensions else None,
        }
    return contexts


def _build_unit_map(root) -> Dict[str, str]:
    """Estrae tutti xbrli:unit → {id: stringa misura}."""
    units = {}
    for unit in root.iter(f"{{{NS_XBRLI}}}unit"):
        uid = unit.get("id")
        if not uid:
            continue
        # Misura semplice
        measure = unit.find(f"{{{NS_XBRLI}}}measure")
        if measure is not None and measure.text:
            # "iso4217:EUR" → "EUR"
            raw = measure.text.strip()
            units[uid] = raw.split(":")[-1] if ":" in raw else raw
            continue
        # Divide (numeratore/denominatore)
        div = unit.find(f"{{{NS_XBRLI}}}divide")
        if div is not None:
            num_el = div.find(f"{{{NS_XBRLI}}}unitNumerator/{{{NS_XBRLI}}}measure")
            den_el = div.find(f"{{{NS_XBRLI}}}unitDenominator/{{{NS_XBRLI}}}measure")
            num = (num_el.text.strip().split(":")[-1]) if num_el is not None and num_el.text else "?"
            den = (den_el.text.strip().split(":")[-1]) if den_el is not None and den_el.text else "?"
            units[uid] = f"{num}/{den}"
    return units


def _get_inner_text(el) -> str:
    """Estrae tutto il testo ricorsivamente, saltando ix:exclude."""
    parts = []
    if el.text:
        parts.append(el.text)
    for child in el:
        # Salta ix:exclude
        tag = child.tag if isinstance(child.tag, str) else ""
        if tag == f"{{{NS_IX}}}exclude":
            # Solo il tail dopo ix:exclude
            if child.tail:
                parts.append(child.tail)
            continue
        parts.append(_get_inner_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def _parse_ix_number(raw: str, fmt: Optional[str]) -> Optional[Decimal]:
    """Parsa un numero iXBRL applicando il formato di trasformazione."""
    if raw is None:
        return None
    s = raw.strip()
    if s == "" or s == "-":
        return Decimal(0)

    if fmt:
        fmt_lower = fmt.lower()
        if "fixed-zero" in fmt_lower:
            return Decimal(0)
        if "num-dot-decimal" in fmt_lower:
            # EU: "1.234,56" → rimuovi punti, virgola→punto
            s = s.replace(".", "").replace(",", ".")
        elif "num-comma-decimal" in fmt_lower:
            # US/UK: "1,234.56" → rimuovi virgole
            s = s.replace(",", "")
        # else: fallback sotto

    # Pulizia generica
    s = s.replace(" ", "").replace("\u00A0", "")
    # Se contiene sia . che , cerca di capire il formato
    if not fmt:
        if "," in s and "." in s:
            # Se la virgola è dopo l'ultimo punto → EU (1.234,56)
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            else:
                # US (1,234.56)
                s = s.replace(",", "")
        elif "," in s and "." not in s:
            # Virgola potrebbe essere decimale (EU senza migliaia)
            s = s.replace(",", ".")

    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _extract_numeric_fact(el, contexts: Dict, units: Dict) -> Optional[Dict]:
    """Estrae un fatto numerico da un elemento ix:nonFraction."""
    concept = el.get("name")
    ctx_ref = el.get("contextRef")
    if not concept or not ctx_ref:
        return None

    unit_ref = el.get("unitRef")
    decimals = el.get("decimals")
    scale_str = el.get("scale")
    sign = el.get("sign")
    fmt = el.get("format")

    raw_text = _get_inner_text(el).strip()
    value = _parse_ix_number(raw_text, fmt)
    if value is None:
        return None

    # Applica scale: value * 10^scale
    if scale_str:
        try:
            scale_int = int(scale_str)
            value = value * (Decimal(10) ** scale_int)
        except (ValueError, InvalidOperation):
            pass

    # Applica sign
    if sign == "-":
        value = -value

    period = contexts.get(ctx_ref, {})
    unit_str = units.get(unit_ref) if unit_ref else None

    raw_json = {}
    if scale_str:
        raw_json["scale"] = scale_str
    if sign:
        raw_json["sign"] = sign
    if fmt:
        raw_json["format"] = fmt
    if decimals:
        raw_json["decimals"] = decimals
    dims = period.get("dimensions")
    if dims:
        raw_json["dimensions"] = dims

    return {
        "concept": concept,
        "context_ref": ctx_ref,
        "unit": unit_str,
        "decimals": decimals,
        "value": value,
        "instant": period.get("instant"),
        "start_date": period.get("start"),
        "end_date": period.get("end"),
        "raw_json": raw_json if raw_json else None,
    }


def _extract_text_fact(el, contexts: Dict) -> Optional[Dict]:
    """Estrae un fatto testuale da un elemento ix:nonNumeric."""
    concept = el.get("name")
    ctx_ref = el.get("contextRef")
    if not concept or not ctx_ref:
        return None

    text_value = _get_inner_text(el).strip()
    period = contexts.get(ctx_ref, {})
    dims = period.get("dimensions")

    raw_json = {"text_value": text_value}
    if dims:
        raw_json["dimensions"] = dims

    return {
        "concept": concept,
        "context_ref": ctx_ref,
        "unit": None,
        "decimals": None,
        "value": None,
        "instant": period.get("instant"),
        "start_date": period.get("start"),
        "end_date": period.get("end"),
        "raw_json": raw_json,
    }


def _parse_ixbrl(file_path: str) -> Iterable[Dict]:
    """Parser completo per file iXBRL (inline XBRL in XHTML)."""
    from lxml import etree

    tree = etree.parse(file_path)
    root = tree.getroot()

    contexts = _build_context_map(root)
    units = _build_unit_map(root)

    # ix:nonFraction → fatti numerici
    for el in root.iter(f"{{{NS_IX}}}nonFraction"):
        fact = _extract_numeric_fact(el, contexts, units)
        if fact is not None:
            yield fact

    # ix:nonNumeric → fatti testuali
    for el in root.iter(f"{{{NS_IX}}}nonNumeric"):
        fact = _extract_text_fact(el, contexts)
        if fact is not None:
            yield fact
