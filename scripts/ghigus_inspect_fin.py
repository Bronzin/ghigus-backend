# P:\Github\ghigus-backend\scripts\ghigus_inspect_fin.py
import argparse, os, sys, re
from typing import Optional
from sqlalchemy import create_engine, text, inspect

NAMES = ["fin_sp_riclass", "fin_ce_riclass"]

def connect(db_url: Optional[str]):
    url = db_url or os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("Set DATABASE_URL or pass --db")
    return create_engine(url)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", help="SQLAlchemy DB URL (fallback: env DATABASE_URL)")
    ap.add_argument("--pratica", required=True, help="slug o id (es: pratica4)")
    ap.add_argument("--refresh", action="store_true", help="se materialized views, prova REFRESH")
    args = ap.parse_args()

    eng = connect(args.db)
    insp = inspect(eng)
    print(f"[info] Dialect: {eng.dialect.name}")

    with eng.begin() as c:
        for n in NAMES:
            kind = "unknown"
            is_mv = False
            is_view = False
            is_table = False

            if eng.dialect.name == "postgresql":
                row = c.execute(text("select relname, relkind from pg_class where relname=:n"), {"n": n}).fetchone()
                if row:
                    # relkind: r=table, v=view, m=materialized view
                    rk = row[1]
                    if rk == "r":
                        kind, is_table = "table", True
                    elif rk == "v":
                        kind, is_view = "view", True
                    elif rk == "m":
                        kind, is_mv = "materialized_view", True
                else:
                    # fallback info_schema
                    row = c.execute(text("select table_name from information_schema.views where table_name=:n"), {"n": n}).fetchone()
                    if row:
                        kind, is_view = "view", True
                print(f"{n}: {kind}")
                # prova a stampare definizione view se possibile
                if is_view or is_mv:
                    try:
                        ddl = c.execute(text("select pg_get_viewdef(:n::regclass, true)"), {"n": n}).scalar()
                        if ddl:
                            print(f"--- {n} definition (troncata a 800 char) ---")
                            print((ddl or "")[:800])
                    except Exception as e:
                        print(f"[warn] no viewdef for {n}: {e}")
                if is_mv and args.refresh:
                    try:
                        print(f"[info] Refresh MV {n} ...")
                        c.execute(text(f"refresh materialized view {n}"))
                        print("[ok] refreshed")
                    except Exception as e:
                        print(f"[err] refresh failed: {e}")
            else:
                # SQLite or others
                row = c.execute(text("select name, type from sqlite_master where name=:n"), {"n": n}).fetchone()
                if row:
                    kind = row[1]
                print(f"{n}: {kind}")

        # mostra colonne e count grezzo
        for n in NAMES:
            try:
                cols = [col["name"] for col in insp.get_columns(n)]
                print(f"\nColumns {n}: {cols}")
                sql = f"select count(*) from {n}"
                cnt = c.execute(text(sql)).scalar_one()
                print(f"Count {n}: {cnt}")
            except Exception as e:
                print(f"[warn] introspection failed for {n}: {e}")

        # scan tabelle con colonne amount/importo e possibile filtro pratica
        print("\n=== SCAN amount/importo tables ===")
        for t in insp.get_table_names():
            cols = [col["name"] for col in insp.get_columns(t)]
            has_amt = any(x in cols for x in ("amount","importo"))
            has_pratica = any(x in cols for x in ("case_id","pratica_id","slug"))
            if has_amt and has_pratica:
                # prova un conteggio filtrato
                where = []
                params = {}
                if "case_id" in cols and args.pratica.isdigit():
                    where.append("case_id = :pid"); params["pid"] = int(args.pratica)
                if "pratica_id" in cols and args.pratica.isdigit():
                    where.append("pratica_id = :pid2"); params["pid2"] = int(args.pratica)
                if "slug" in cols and not args.pratica.isdigit():
                    where.append("slug = :slug"); params["slug"] = args.pratica
                sql = f"select count(*) from {t}" + ((" where " + " or ".join(where)) if where else "")
                try:
                    cnt = c.execute(text(sql), params).scalar_one()
                    print(f"- {t}: {cnt} rows (scoped) | cols: {', '.join(cols[:8])}")
                except Exception as e:
                    print(f"- {t}: count failed ({e}) | cols: {', '.join(cols[:8])}")

if __name__ == "__main__":
    main()
