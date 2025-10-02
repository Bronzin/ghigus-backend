# -*- coding: utf-8 -*-
"""
Triage SP: controlla per una pratica se:
- esistono righe in stg_tb_entries (Bilancio Contabile)
- esiste copertura mappa (stg_map_sp) sui codici
- esistono output in fin_sp_riclass
Uso:
  python scripts/ghigus_triage_sp.py --pratica pratica1
Richiede: SQLAlchemy, psycopg2; DATABASE_URL in env (come già per il backend).
"""
import argparse, os, sys
from decimal import Decimal
from sqlalchemy import create_engine, text

def env_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("[ERRORE] DATABASE_URL non impostata in ambiente.")
        sys.exit(2)
    return url

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pratica", required=True, help="slug pratica (case_id)")
    args = ap.parse_args()
    slug = args.pratica

    eng = create_engine(env_url())

    with eng.begin() as cn:
        print(f"[info] Pratica: {slug}")

        # 1) STAGING
        q = text("""
          select count(*) cnt, coalesce(sum(coalesce(debit,0)-coalesce(credit,0)),0) as total
          from stg_tb_entries where case_id = :slug
        """)
        r = cn.execute(q, {"slug": slug}).first()
        cnt_stg, tot_stg = int(r.cnt), Decimal(r.total or 0)
        print(f"[staging] stg_tb_entries: {cnt_stg} righe | totale={tot_stg}")

        # 2) MAPPA SP
        q = text("select count(*) cnt, count(distinct imported_code) d_codes from stg_map_sp")
        r = cn.execute(q).first()
        print(f"[mappa SP] stg_map_sp: {int(r.cnt)} righe | imported_code distinti={int(r.d_codes)}")

        # 3) OUTPUT SP
        q = text("""
          select count(*) cnt, coalesce(sum(amount),0) total
          from fin_sp_riclass
          where case_id = :slug
        """)
        r = cn.execute(q, {"slug": slug}).first()
        print(f"[output SP] fin_sp_riclass: {int(r.cnt)} righe | totale={Decimal(r.total)}")

        # Case_id diversi (diagnostica mismatch)
        q = text("""
          select case_id, count(*) as rows, sum(amount) as tot
          from fin_sp_riclass
          group by case_id
          order by 1
          limit 10
        """)
        rows = cn.execute(q).fetchall()
        if rows:
            print("[diagnostica] case_id presenti in fin_sp_riclass (prime 10):")
            for row in rows:
                print(f"  - {row.case_id}: {row.rows} righe (tot={row.tot})")

        # 4) Copertura prefissi (quanti codici BC matchano uno o più prefissi mappa)
        cover_sql = text("""
          with e as (
            select nullif(regexp_replace(regexp_replace(account_code, '[^0-9]', '', 'g'), '^0+', ''), '') as code_digits
            from stg_tb_entries
            where case_id = :slug
            group by 1
          ),
          m as (
            select nullif(regexp_replace(regexp_replace(imported_code, '[^0-9]', '', 'g'), '^0+', ''), '') as map_digits
            from stg_map_sp
          ),
          pairs as (
            select e.code_digits, m.map_digits
            from e join m
              on (e.code_digits is not null and m.map_digits is not null
                  and (e.code_digits like m.map_digits || '%' or m.map_digits like e.code_digits || '%'))
          )
          select
            (select count(*) from e) as bc_distinct_codes,
            (select count(distinct code_digits) from pairs) as covered_codes
        """)
        r = cn.execute(cover_sql, {"slug": slug}).first()
        bc_codes = int(r.bc_distinct_codes or 0)
        covered = int(r.covered_codes or 0)
        print(f"[copertura] codici BC distinti={bc_codes} | coperti dalla mappa={covered}")

        # 5) Esempi non coperti (max 10)
        missing_sql = text("""
          with e as (
            select nullif(regexp_replace(regexp_replace(account_code, '[^0-9]', '', 'g'), '^0+', ''), '') as code_digits
            from stg_tb_entries where case_id = :slug group by 1
          ),
          m as (
            select nullif(regexp_replace(regexp_replace(imported_code, '[^0-9]', '', 'g'), '^0+', ''), '') as map_digits
            from stg_map_sp
          ),
          matched as (
            select distinct e.code_digits
            from e join m
              on (e.code_digits is not null and m.map_digits is not null
                  and (e.code_digits like m.map_digits || '%' or m.map_digits like e.code_digits || '%'))
          )
          select e.code_digits
          from e left join matched using(code_digits)
          where matched.code_digits is null and e.code_digits is not null
          order by e.code_digits
          limit 10
        """)
        miss = [row.code_digits for row in cn.execute(missing_sql, {"slug": slug}).fetchall()]
        if miss:
            print(f"[copertura] Esempi codici NON coperti (max 10): {miss}")

if __name__ == "__main__":
    main()
