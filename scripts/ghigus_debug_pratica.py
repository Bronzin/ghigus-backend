"""
Ghigus - Debug Pratica Data Visibility (v2)
-------------------------------------------
Esempi (Windows CMD):
  cd P:\Github\ghigus-backend
  .venv\Scripts\activate

  set DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/ghigus
  python P:\Github\ghigus-backend\scripts\ghigus_debug_pratica.py --pratica pratica4

  # oppure passando l'URL del DB direttamente
  python P:\Github\ghigus-backend\scripts\ghigus_debug_pratica.py --db sqlite:///P:/Github/ghigus-backend/ghigus.db --pratica pratica4
"""
import argparse
import os
import sys
from typing import List, Optional, Tuple

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

LIKELY_CASE_TABLES = ["cases", "pratiche", "practice", "case"]
LIKELY_UPLOAD_TABLES = ["uploads", "ghg_uploads", "files"]
LIKELY_RICLASS_HINTS = ["riclass", "reclass", "mapping"]
LIKELY_STAGING_HINTS = ["staging", "tmp", "raw", "ingest"]
LIKELY_SP_HINTS = ["sp", "stato_patrimoniale", "balance_sheet"]
LIKELY_CE_HINTS = ["ce", "conto_economico", "income_statement"]

def connect(db_url: Optional[str]) -> Engine:
    url = db_url or os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL not set and --db not provided.")
    return create_engine(url)

def find_first_existing_table(inspector, candidates: List[str]) -> Optional[str]:
    existing = set(inspector.get_table_names())
    for c in candidates:
        if c in existing:
            return c
    return None

def find_case_identifier(engine, pratica: str) -> Tuple[Optional[int], Optional[str]]:
    insp = inspect(engine)
    case_table = find_first_existing_table(insp, LIKELY_CASE_TABLES)
    if not case_table:
        print("[warn] Could not find a cases/pratiche table.")
        # fallback: tratteremo 'pratica' come slug
        return None, pratica

    with engine.begin() as conn:
        cols = [c["name"] for c in insp.get_columns(case_table)]

        # preferenze esplicite per colonne id/slug
        id_candidates = [c for c in ("id", "case_id", "pratica_id") if c in cols]
        slug_candidates = [c for c in ("slug", "name", "code", "pratica_slug", "case_slug") if c in cols]

        pratica_id: Optional[int] = None
        pratica_slug: Optional[str] = None

        # 1) risoluzione per id numerico (solo se abbiamo davvero una colonna id)
        if pratica.isdigit() and id_candidates:
            id_col = id_candidates[0]
            q = text(f"select {id_col} from {case_table} where {id_col} = :pid limit 1")
            row = conn.execute(q, {"pid": int(pratica)}).fetchone()
            if row:
                pratica_id = int(row[0])
                print(f"[info] Resolved pratica by numeric id via {id_col}={pratica_id}")

        # 2) risoluzione per slug (non forziamo cast su int)
        if pratica_id is None and slug_candidates:
            for sc in slug_candidates:
                q = text(f"select {sc} from {case_table} where {sc} = :slug limit 1")
                row = conn.execute(q, {"slug": pratica}).fetchone()
                if row:
                    pratica_slug = str(row[0])
                    print(f"[info] Resolved pratica by slug via {sc}='{pratica_slug}'")
                    break

        # 3) fallback Postgres ILIKE
        if pratica_id is None and pratica_slug is None and "postgresql" in str(engine.url):
            for sc in slug_candidates:
                q = text(f"select {sc} from {case_table} where {sc} ilike :slug limit 1")
                row = conn.execute(q, {"slug": pratica}).fetchone()
                if row:
                    pratica_slug = str(row[0])
                    print(f"[info] Resolved pratica by slug (ilike) via {sc}='{pratica_slug}'")
                    break

        return pratica_id, pratica_slug

def candidate_tables(inspector, hints: List[str]) -> List[str]:
    names = inspector.get_table_names()
    out = []
    for n in names:
        ln = n.lower()
        if any(h in ln for h in hints):
            out.append(n)
    return out

def try_count_for_pratica(engine: Engine, table: str, pratica_id: Optional[int], pratica_slug: Optional[str]) -> Tuple[int, Optional[List[str]]]:
    insp = inspect(engine)
    cols = [c["name"] for c in insp.get_columns(table)]
    where = None
    params = {}

    # Applica solo i filtri che hanno un valore disponibile
    if "pratica_id" in cols and pratica_id is not None:
        where = "pratica_id = :pid"
        params["pid"] = pratica_id
    elif "case_id" in cols and pratica_id is not None:
        where = "case_id = :pid"
        params["pid"] = pratica_id
    elif "slug" in cols and pratica_slug:
        where = "slug = :slug"
        params["slug"] = pratica_slug

    sql = f"select count(*) from {table}"
    if where:
        sql += f" where {where}"

    with engine.begin() as conn:
        try:
            cnt = conn.execute(text(sql), params).scalar_one()
            sample_cols = [c for c in cols if c in ("id","code","codice","descrizione","description","amount","importo","period","anno")]
            return int(cnt), sample_cols[:6] if sample_cols else None
        except Exception as e:
            print(f"[warn] count failed on {table}: {e}")
            return -1, None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", help="SQLAlchemy DB URL (fallback to env DATABASE_URL)")
    ap.add_argument("--pratica", required=True, help="Pratica slug or numeric id (e.g., 'pratica4')")
    args = ap.parse_args()

    engine = connect(args.db)
    insp = inspect(engine)

    pratica_id, pratica_slug = find_case_identifier(engine, args.pratica)
    if pratica_id is None and pratica_slug is None:
        print("[error] Could not resolve pratica in cases/pratiche table. Proceeding with global counts.")

    upload_tbls = candidate_tables(insp, LIKELY_UPLOAD_TABLES)
    riclass_tbls = candidate_tables(insp, LIKELY_RICLASS_HINTS) + candidate_tables(insp, LIKELY_SP_HINTS) + candidate_tables(insp, LIKELY_CE_HINTS)
    staging_tbls = candidate_tables(insp, LIKELY_STAGING_HINTS)

    print("\n=== TABLE DISCOVERY ===")
    print("Uploads:", upload_tbls or "—")
    print("Riclass:", riclass_tbls or "—")
    print("Staging:", staging_tbls or "—")

    some_data = False
    print("\n=== ROW COUNTS (scoped to pratica when possible) ===")
    for group_name, tbls in (("UPLOADS", upload_tbls), ("RICLASS", list(dict.fromkeys(riclass_tbls))), ("STAGING", staging_tbls)):
        print(f"\n[{group_name}]")
        if not tbls:
            print("  (none)")
            continue
        for t in tbls:
            cnt, sample_cols = try_count_for_pratica(engine, t, pratica_id, pratica_slug)
            if cnt > 0:
                some_data = True
            print(f"  - {t}: {cnt} rows{' | sample cols: ' + ','.join(sample_cols) if sample_cols else ''}")

    if not some_data:
        print("\n[RESULT] No data found for this pratica across likely tables. Ingestion likely failed or pratica mapping is wrong.")
        sys.exit(2)
    else:
        print("\n[RESULT] Some data exists. If the UI still shows 'Nessun dato', likely the API/serializer mapping is off (e.g., wrong pratica id/slug in filters) or the endpoint returns an empty payload.")

if __name__ == "__main__":
    main()
