# P:\Github\ghigus-backend\scripts\ghigus_probe_ce_snapshot.py
import os, sys
from sqlalchemy import create_engine, text

DB = os.environ.get("DATABASE_URL") or sys.exit("Set DATABASE_URL")
PRATICA = os.environ.get("GHIGUS_PRATICA", "pratica4")
eng = create_engine(DB)

def col_exists(c, table, col):
    return c.execute(text("""
        select 1
        from information_schema.columns
        where table_name=:t and column_name=:c
        limit 1
    """), {"t": table, "c": col}).fetchone() is not None

with eng.begin() as c:
    # capiamo come filtrare TB: case_id (testo) o slug
    tb = "stg_tb_entries"
    use_case_id = col_exists(c, tb, "case_id")
    use_slug    = col_exists(c, tb, "slug")
    if use_case_id:
        tb_filter_col = "case_id"; tbval = PRATICA
    elif use_slug:
        tb_filter_col = "slug"; tbval = PRATICA
    else:
        sys.exit(f"{tb} non ha né case_id né slug.")

    print(f"[TB] filtro: {tb}.{tb_filter_col} = {tbval!r}")

    # quante righe TB per la pratica
    cnt = c.execute(text(f"select count(*) from {tb} where {tb_filter_col}=:v"), {"v": tbval}).scalar_one()
    print("[TB] righe pratica:", cnt)

    # periodi disponibili
    has_period = col_exists(c, tb, "period_end")
    if has_period:
        periods = c.execute(text(f"""
            select period_end, count(*) as n, sum(coalesce(debit,0)-coalesce(credit,0)) as tot_dc,
                   sum(coalesce(amount,0)) as tot_amt
            from {tb}
            where {tb_filter_col}=:v
            group by period_end
            order by period_end
        """), {"v": tbval}).fetchall()
        print("[TB] periodi:", periods)
        last = c.execute(text(f"select max(period_end) from {tb} where {tb_filter_col}=:v"), {"v": tbval}).scalar()
        prev = c.execute(text(f"select max(period_end) from {tb} where {tb_filter_col}=:v and period_end < :last"),
                         {"v": tbval, "last": last}).scalar() if last is not None else None
        print("[TB] last:", last, "prev:", prev)
    else:
        print("[TB] Nessuna colonna period_end")

    # mappa CE: che forma hanno i codici?
    # conta righe e quanti imported_code/distinct ci danno cifre utili
    rows, distinct_codes = c.execute(text("""
        select count(*), count(distinct imported_code)
        from stg_map_ce
    """)).fetchone()
    print("[CE map] righe:", rows, "distinct imported_code:", distinct_codes)

    digits_stats = c.execute(text(r"""
        with m as (
          select imported_code,
                 nullif(regexp_replace(regexp_replace(imported_code,'[^0-9]','','g'), '^0+', ''), '') as digits
          from stg_map_ce
        )
        select count(*) filter (where digits is not null) as with_digits,
               count(*) filter (where digits is null)     as without_digits
        from m
    """)).fetchone()
    print("[CE map] with_digits / without_digits:", digits_stats)

    # esempi CE imported_code -> digits (prime 15)
    sample_ce = c.execute(text(r"""
        select imported_code,
               nullif(regexp_replace(regexp_replace(imported_code,'[^0-9]','','g'), '^0+', ''), '') as digits
        from stg_map_ce
        limit 15
    """)).fetchall()
    print("[CE map] esempi imported_code→digits:", sample_ce)

    # esempi TB account_code -> digits (prime 15)
    sample_tb = c.execute(text(rf"""
        select distinct account_code,
               nullif(regexp_replace(regexp_replace(account_code,'[^0-9]','','g'), '^0+', ''), '') as digits
        from {tb}
        where {tb_filter_col}=:v
        limit 15
    """), {"v": tbval}).fetchall()
    print("[TB] esempi account_code→digits:", sample_tb)
