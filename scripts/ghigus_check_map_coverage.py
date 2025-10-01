# P:\Github\ghigus-backend\scripts\ghigus_check_map_coverage.py
import os, sys
from sqlalchemy import create_engine, text, inspect

DB=os.environ.get("DATABASE_URL") or sys.exit("Set DATABASE_URL")
eng=create_engine(DB)
with eng.begin() as c:
    # quanti codici ci sono in TB?
    total = c.execute(text("select count(distinct account_code) from stg_tb_entries")).scalar_one()
    print("Distinct account_code in TB:", total)

    # SP: quanti non coperti (dopo normalizzazione come nel JOIN)
    not_cov_sp = c.execute(text(r"""
        with e as (
          select distinct upper(regexp_replace(account_code, '[^0-9A-Za-z]', '', 'g')) as code
          from stg_tb_entries
        ), m as (
          select distinct upper(regexp_replace(imported_code, '[^0-9A-Za-z]', '', 'g')) as code
          from stg_map_sp
        )
        select count(*) from e left join m using(code) where m.code is null
    """)).scalar_one()
    print("SP - account_code NON mappati:", not_cov_sp)

    # CE: quanti non coperti
    not_cov_ce = c.execute(text(r"""
        with e as (
          select distinct upper(regexp_replace(account_code, '[^0-9A-Za-z]', '', 'g')) as code
          from stg_tb_entries
        ), m as (
          select distinct upper(regexp_replace(imported_code, '[^0-9A-Za-z]', '', 'g')) as code
          from stg_map_ce
        )
        select count(*) from e left join m using(code) where m.code is null
    """)).scalar_one()
    print("CE - account_code NON mappati:", not_cov_ce)

    # mostra fino a 20 codici TB non mappati su SP
    rows = c.execute(text(r"""
        with e as (
          select distinct upper(regexp_replace(account_code, '[^0-9A-Za-z]', '', 'g')) as code
          from stg_tb_entries
        ), m as (
          select distinct upper(regexp_replace(imported_code, '[^0-9A-Za-z]', '', 'g')) as code
          from stg_map_sp
        )
        select e.code from e left join m using(code) where m.code is null limit 20
    """)).fetchall()
    if rows:
        print("Esempi non mappati (SP):", [r[0] for r in rows])
