# app/services/processing.py
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Iterable, Dict, Tuple, Optional

from app.db.models.staging import TBEntry, XbrlFact, MapSP, MapCE
from app.db.models.final import SpRiclass, CeRiclass, KpiStandard
from app.services.loaders import (
    get_latest_upload_path,
    parse_tb_csv,
    parse_xbrl_xml,
)

# -------------------------
# STAGING: helper
# -------------------------
def clear_staging(db: Session, case_id: str) -> None:
    db.query(TBEntry).filter(TBEntry.case_id == case_id).delete()
    db.query(XbrlFact).filter(XbrlFact.case_id == case_id).delete()
    db.commit()

def stage_tb(db: Session, case_id: str, rows: Iterable[Dict]) -> int:
    """
    Staging del Bilancio Contabile.
    Regola importi:
      entry_amount = amount se presente, altrimenti (credit - debit)
    """
    count = 0
    for r in rows:
        # valori numerici “safe”
        debit = r.get("debit") or Decimal(0)
        credit = r.get("credit") or Decimal(0)

        amount = r.get("amount")
        if amount is None:
            amount = credit - debit
        # normalizza eventuali tipi non-Decimal
        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(str(amount))
            except Exception:
                amount = Decimal(0)

        db.add(
            TBEntry(
                case_id=case_id,
                account_code=str(r.get("account_code") or "").strip(),
                account_name=(r.get("account_name") or None),
                debit=debit,
                credit=credit,
                amount=amount,
            )
        )
        count += 1

    db.commit()
    return count


def stage_xbrl(db: Session, case_id: str, facts: Iterable[Dict]) -> int:
    count = 0
    for f in facts:
        db.add(
            XbrlFact(
                case_id=case_id,
                concept=f.get("concept"),
                context_ref=f.get("context_ref"),
                unit=f.get("unit"),
                decimals=str(f.get("decimals")) if f.get("decimals") is not None else None,
                value=f.get("value"),
                instant=f.get("instant"),
                start_date=f.get("start_date"),
                end_date=f.get("end_date"),
                raw_json=f.get("raw_json"),
            )
        )
        count += 1
    db.commit()
    return count

# -------------------------
# MAPPE: costruzione dict (override per-pratica -> fallback globale)
# -------------------------
def _build_map_sp(db: Session, case_id: str) -> Dict[str, Tuple[str, Optional[str]]]:
    try:
        specific = {
            m.imported_code: (m.riclass_code, m.riclass_desc)
            for m in db.query(MapSP).filter(MapSP.case_id == case_id).all()
        }
    except Exception:
        db.rollback()
        return {}
    if specific:
        base = {
            m.imported_code: (m.riclass_code, m.riclass_desc)
            for m in db.query(MapSP).filter(MapSP.case_id.is_(None)).all()
            if m.imported_code not in specific
        }
        specific.update(base)
        return specific
    else:
        return {
            m.imported_code: (m.riclass_code, m.riclass_desc)
            for m in db.query(MapSP).filter(MapSP.case_id.is_(None)).all()
        }

def _build_map_ce(db: Session, case_id: str) -> Dict[str, Tuple[str, Optional[str]]]:
    try:
        specific = {
            m.imported_code: (m.riclass_code, m.riclass_desc)
            for m in db.query(MapCE).filter(MapCE.case_id == case_id).all()
        }
    except Exception:
        db.rollback()
        return {}
    if specific:
        base = {
            m.imported_code: (m.riclass_code, m.riclass_desc)
            for m in db.query(MapCE).filter(MapCE.case_id.is_(None)).all()
            if m.imported_code not in specific
        }
        specific.update(base)
        return specific
    else:
        return {
            m.imported_code: (m.riclass_code, m.riclass_desc)
            for m in db.query(MapCE).filter(MapCE.case_id.is_(None)).all()
        }

# -------------------------
# DATAMART: riclass & KPI
# -------------------------
def compute_sp(db: Session, case_id: str) -> int:
    db.query(SpRiclass).filter(SpRiclass.case_id == case_id).delete()

    maps = _build_map_sp(db, case_id)
    if not maps:
        db.commit()
        return 0

    totals: Dict[Tuple[str, Optional[str]], Decimal] = {}
    for row in db.query(TBEntry).filter(TBEntry.case_id == case_id):
        key = row.account_code
        if key not in maps:
            continue
        ric_code, ric_desc = maps[key]
        k = (ric_code, ric_desc)
        totals[k] = totals.get(k, Decimal(0)) + (row.amount or Decimal(0))

    for (code, desc), amount in totals.items():
        db.add(SpRiclass(case_id=case_id, riclass_code=code, riclass_desc=desc, amount=amount))
    db.commit()
    return len(totals)

def compute_ce(db: Session, case_id: str) -> int:
    db.query(CeRiclass).filter(CeRiclass.case_id == case_id).delete()

    maps = _build_map_ce(db, case_id)
    if not maps:
        db.commit()
        return 0

    totals: Dict[Tuple[str, Optional[str]], Decimal] = {}
    for row in db.query(TBEntry).filter(TBEntry.case_id == case_id):
        key = row.account_code
        if key not in maps:
            continue
        ric_code, ric_desc = maps[key]
        k = (ric_code, ric_desc)
        totals[k] = totals.get(k, Decimal(0)) + (row.amount or Decimal(0))

    for (code, desc), amount in totals.items():
        db.add(CeRiclass(case_id=case_id, riclass_code=code, riclass_desc=desc, amount=amount))
    db.commit()
    return len(totals)

def compute_kpi(db: Session, case_id: str) -> int:
    db.query(KpiStandard).filter(KpiStandard.case_id == case_id).delete()

    def sum_by_prefix(model, prefix: str) -> Decimal:
        q = db.query(model).filter(model.case_id == case_id, model.riclass_code.startswith(prefix))
        s = sum((r.amount or Decimal(0)) for r in q.all())
        return Decimal(s)

    assets    = sum_by_prefix(SpRiclass, "A")
    current   = sum_by_prefix(SpRiclass, "A1")
    liab      = sum_by_prefix(SpRiclass, "P")
    curr_liab = sum_by_prefix(SpRiclass, "P1")

    ebitda    = sum_by_prefix(CeRiclass, "EBITDA")
    revenue   = sum_by_prefix(CeRiclass, "RICAVI")

    kpis = [
        ("Leverage",      (liab / assets) if assets else 0, "x"),
        ("Current Ratio", (current / curr_liab) if curr_liab else 0, "x"),
        ("EBITDA Margin", (ebitda / revenue * 100) if revenue else 0, "%"),
    ]
    for name, val, unit in kpis:
        db.add(KpiStandard(case_id=case_id, name=name, value=Decimal(val), unit=unit))
    db.commit()
    return len(kpis)

# -------------------------
# XBRL -> Riclassificati multi-anno
# -------------------------
def compute_sp_from_xbrl(db: Session, case_id: str) -> int:
    """Riclassifica fatti XBRL di tipo SP, raggruppati per anno."""
    from app.services.xbrl_mapping import classify_xbrl_fact

    # Elimina solo righe con period != None (preserva quelle da TB)
    db.query(SpRiclass).filter(
        SpRiclass.case_id == case_id,
        SpRiclass.period.isnot(None),
    ).delete(synchronize_session=False)

    facts = db.query(XbrlFact).filter(
        XbrlFact.case_id == case_id,
        XbrlFact.value.isnot(None),
    ).all()

    # Aggrega per (riclass_code, period)
    totals: Dict[Tuple[str, str, str], Decimal] = {}  # (code, desc, period) -> amount
    for f in facts:
        cls = classify_xbrl_fact(f.concept)
        if cls is None or cls[0] != "SP":
            continue
        _, code, desc = cls
        # Determina period dall'anno di instant o end_date
        year = None
        if f.instant:
            year = str(f.instant.year)
        elif f.end_date:
            year = str(f.end_date.year)
        if not year:
            continue
        k = (code, desc, year)
        totals[k] = totals.get(k, Decimal(0)) + Decimal(str(f.value))

    for (code, desc, period), amount in totals.items():
        db.add(SpRiclass(
            case_id=case_id,
            riclass_code=code,
            riclass_desc=desc,
            amount=amount,
            period=period,
        ))
    db.commit()
    return len(totals)


def compute_ce_from_xbrl(db: Session, case_id: str) -> int:
    """Riclassifica fatti XBRL di tipo CE, raggruppati per anno."""
    from app.services.xbrl_mapping import classify_xbrl_fact

    db.query(CeRiclass).filter(
        CeRiclass.case_id == case_id,
        CeRiclass.period.isnot(None),
    ).delete(synchronize_session=False)

    facts = db.query(XbrlFact).filter(
        XbrlFact.case_id == case_id,
        XbrlFact.value.isnot(None),
    ).all()

    totals: Dict[Tuple[str, str, str], Decimal] = {}
    for f in facts:
        cls = classify_xbrl_fact(f.concept)
        if cls is None or cls[0] != "CE":
            continue
        _, code, desc = cls
        # CE: anno dalla end_date (periodo duration) o instant
        year = None
        if f.end_date:
            year = str(f.end_date.year)
        elif f.instant:
            year = str(f.instant.year)
        if not year:
            continue
        k = (code, desc, year)
        totals[k] = totals.get(k, Decimal(0)) + Decimal(str(f.value))

    for (code, desc, period), amount in totals.items():
        db.add(CeRiclass(
            case_id=case_id,
            riclass_code=code,
            riclass_desc=desc,
            amount=amount,
            period=period,
        ))
    db.commit()
    return len(totals)


def compute_kpi_from_xbrl(db: Session, case_id: str) -> int:
    """Calcola KPI per ogni periodo XBRL distinto."""
    db.query(KpiStandard).filter(
        KpiStandard.case_id == case_id,
        KpiStandard.period.isnot(None),
    ).delete(synchronize_session=False)

    # Periodi distinti da SP e CE (escludendo None)
    sp_periods = {r[0] for r in db.query(SpRiclass.period).filter(
        SpRiclass.case_id == case_id, SpRiclass.period.isnot(None)
    ).distinct().all()}
    ce_periods = {r[0] for r in db.query(CeRiclass.period).filter(
        CeRiclass.case_id == case_id, CeRiclass.period.isnot(None)
    ).distinct().all()}
    all_periods = sp_periods | ce_periods

    count = 0
    for period in sorted(all_periods):
        def sum_sp(prefix: str) -> Decimal:
            rows = db.query(SpRiclass).filter(
                SpRiclass.case_id == case_id,
                SpRiclass.period == period,
                SpRiclass.riclass_code.startswith(prefix),
            ).all()
            return sum((r.amount or Decimal(0)) for r in rows) or Decimal(0)

        def sum_ce(prefix: str) -> Decimal:
            rows = db.query(CeRiclass).filter(
                CeRiclass.case_id == case_id,
                CeRiclass.period == period,
                CeRiclass.riclass_code.startswith(prefix),
            ).all()
            return sum((r.amount or Decimal(0)) for r in rows) or Decimal(0)

        assets = sum_sp("A") + sum_sp("LIQUIDITA") + sum_sp("CREDITI") + sum_sp("RIMANENZE") + sum_sp("IMMOBILIZZAZIONI")
        liab = sum_sp("P") + sum_sp("DEBITI") + sum_sp("FONDI")
        curr_liab = sum_sp("P1") + sum_sp("DEBITI")
        current = sum_sp("A1") + sum_sp("LIQUIDITA") + sum_sp("CREDITI") + sum_sp("RIMANENZE")

        ebitda = sum_ce("EBITDA")
        revenue = sum_ce("RICAVI")

        kpis = [
            ("Leverage", (liab / assets) if assets else Decimal(0), "x"),
            ("Current Ratio", (current / curr_liab) if curr_liab else Decimal(0), "x"),
            ("EBITDA Margin", (ebitda / revenue * 100) if revenue else Decimal(0), "%"),
        ]
        for name, val, unit in kpis:
            db.add(KpiStandard(
                case_id=case_id, name=name,
                value=Decimal(str(val)), unit=unit, period=period,
            ))
            count += 1

    db.commit()
    return count


# -------------------------
# API-level helpers
# -------------------------
def ingest_case(db: Session, case_id: str) -> dict:
    """Solo ingest: pulisce staging e carica BC/XBRL dagli ultimi upload."""
    tb_path  = get_latest_upload_path(db, case_id, kinds=("bc", "tb", "trial_balance"))
    xbrl_path = get_latest_upload_path(db, case_id, kinds=("xbrl", "bilancio_xbrl", "xml", "xhtml", "ixbrl"))

    if not tb_path and not xbrl_path:
        raise RuntimeError("Nessun Bilancio Contabile o XBRL trovato per il caso selezionato.")

    clear_staging(db, case_id)

    n_tb = 0
    if tb_path:
        tb_rows = list(parse_tb_csv(tb_path))
        n_tb = stage_tb(db, case_id, tb_rows)

    n_xbrl = 0
    if xbrl_path:
        facts = list(parse_xbrl_xml(xbrl_path))
        n_xbrl = stage_xbrl(db, case_id, facts)

    return {"staging": {"tb_rows": n_tb, "xbrl_facts": n_xbrl}}

def compute_case(db: Session, case_id: str) -> dict:
    """Solo compute: riclassifica SP/CE e calcola KPI partendo dallo staging già presente."""
    import logging
    log = logging.getLogger(__name__)

    # TB-based (può fallire se manca stg_map_sp o non c'è TB)
    n_sp = n_ce = n_kp = 0
    try:
        n_sp = compute_sp(db, case_id)
        n_ce = compute_ce(db, case_id)
        n_kp = compute_kpi(db, case_id)
    except Exception as e:
        log.warning("compute TB-based skipped (no TB data or schema issue): %s", e)
        db.rollback()

    # XBRL multi-anno
    n_sp_xbrl = compute_sp_from_xbrl(db, case_id)
    n_ce_xbrl = compute_ce_from_xbrl(db, case_id)
    n_kp_xbrl = compute_kpi_from_xbrl(db, case_id)
    return {
        "datamart": {
            "sp_rows": n_sp, "ce_rows": n_ce, "kpi": n_kp,
            "sp_xbrl": n_sp_xbrl, "ce_xbrl": n_ce_xbrl, "kpi_xbrl": n_kp_xbrl,
        }
    }

# -------------------------
# PIPELINE completa (compat)
# -------------------------
def process_case(db: Session, case_id: str) -> dict:
    """Ingest + Compute in un colpo solo."""
    s = ingest_case(db, case_id)
    d = compute_case(db, case_id)
    return {"staging": s.get("staging", {}), "datamart": d.get("datamart", {})}
