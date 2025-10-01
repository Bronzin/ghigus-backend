# app/routers/cases_delete.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import List, Dict, Optional
import os

router = APIRouter(prefix="/cases", tags=["cases"])

# ---- Engine unico dal DATABASE_URL ----
_ENGINE: Optional[Engine] = None
def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL non impostata")
        _ENGINE = create_engine(url, future=True)
    return _ENGINE

# tabelle da NON toccare (mappe globali)
MAPS_BLACKLIST = {
    "stg_map_sp", "stg_map_ce", "maps", "maps_global", "maps_ce", "maps_sp"
}

def get_case_slug(engine: Engine, slug: str) -> str:
    with engine.connect() as conn:
        row = conn.execute(
            text("select slug from cases where slug=:s limit 1"),
            {"s": slug}
        ).fetchone()
        if not row:
            raise HTTPException(404, "Case not found")
        return row[0]

def get_table_columns(engine: Engine, table: str) -> Dict[str, str]:
    """{col_name: data_type} letto fuori da transazione."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                select column_name, data_type
                from information_schema.columns
                where table_schema='public' and table_name=:t
            """),
            {"t": table},
        ).fetchall()
    return {r[0]: r[1] for r in rows}

def list_base_tables(engine: Engine) -> List[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                select table_name
                from information_schema.tables
                where table_schema='public' and table_type='BASE TABLE'
            """)
        ).fetchall()
    return [r[0] for r in rows]

def table_exists(engine: Engine, name: str) -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                select 1
                from information_schema.tables
                where table_schema='public' and table_type='BASE TABLE' and table_name=:t
                limit 1
            """),
            {"t": name},
        ).fetchone()
    return row is not None

def build_where_for_table(cols: Dict[str, str], slug: str) -> Optional[str]:
    """Usa solo colonne esistenti; case_id sempre confrontato come testo."""
    conds: List[str] = []
    if "case_id" in cols:
        conds.append("case_id::text = :slug")
    if "slug" in cols:
        conds.append("slug = :slug")
    if "case_slug" in cols:
        conds.append("case_slug = :slug")
    if not conds:
        return None
    return " OR ".join(conds)

def safe_delete(engine: Engine, table: str, where_sql: str, slug: str):
    """Esegue una DELETE in transazione separata; ignora errori per non abortire tutto."""
    try:
        with engine.begin() as conn:
            conn.execute(text(f"delete from {table} where {where_sql}"), {"slug": slug})
    except Exception:
        # log silenzioso: non blocchiamo l’operazione globale
        pass

def fetch_upload_paths(engine: Engine, slug: str) -> List[str]:
    if not table_exists(engine, "uploads"):
        return []
    cols = get_table_columns(engine, "uploads")
    where_sql = build_where_for_table(cols, slug)
    if not where_sql:
        return []
    with engine.connect() as conn:
        try:
            rows = conn.execute(
                text(f"select path from uploads where {where_sql}"),
                {"slug": slug}
            ).fetchall()
            return [r[0] for r in rows if r and r[0]]
        except Exception:
            return []

@router.delete("/{slug}", status_code=204, summary="Delete Case (and related data, NOT maps)")
def delete_case(slug: str):
    """
    Cancella la pratica 'slug' e tutte le righe collegate (uploads, riclass, bilancio contabile, kpi, ecc.),
    SENZA toccare le mappe (stg_map_*). Ogni tabella viene pulita in una transazione separata.
    """
    engine = get_engine()

    # 1) verifica esistenza pratica e normalizza slug (se serve)
    case_slug = get_case_slug(engine, slug)

    # 2) raccogli, fuori transazione, eventuali path dei file
    upload_paths = fetch_upload_paths(engine, case_slug)

    # 3) pulizia tabelle note (ognuna in transazione separata)
    known_tables = (
        "fin_sp_riclass",
        "fin_ce_riclass",
        "stg_tb_entries",   # Bilancio Contabile
        "uploads",
        "kpi_standard",
        "fin_kpi", "kpi",
    )
    for t in known_tables:
        if table_exists(engine, t):
            cols = get_table_columns(engine, t)
            where_sql = build_where_for_table(cols, case_slug)
            if where_sql:
                safe_delete(engine, t, where_sql, case_slug)

    # 4) pulizia generica su tutte le BASE TABLE che hanno (case_id/slug/case_slug)
    for tname in list_base_tables(engine):
        if tname in MAPS_BLACKLIST or tname == "cases" or tname in known_tables:
            continue
        try:
            cols = get_table_columns(engine, tname)
            if not {"case_id","slug","case_slug"} & set(cols.keys()):
                continue
            where_sql = build_where_for_table(cols, case_slug)
            if where_sql:
                safe_delete(engine, tname, where_sql, case_slug)
        except Exception:
            # ignora problemi su singole tabelle (permessi, trigger, ecc.)
            continue

    # 5) elimina la riga della pratica (transazione separata)
    try:
        with engine.begin() as conn:
            conn.execute(text("delete from cases where slug=:slug"), {"slug": case_slug})
    except Exception:
        # se fallisce, lasciamo i dati già cancellati; restituiamo 500 per coerenza
        raise HTTPException(500, "Errore nell’eliminazione della riga cases")

    # 6) rimuovi i file fisici (best-effort, fuori transazione)
    for p in upload_paths:
        try:
            if p and os.path.isfile(p):
                os.remove(p)
        except Exception:
            pass

    return  # 204
