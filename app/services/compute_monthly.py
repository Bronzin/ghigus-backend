from uuid import uuid4
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

def upsert_sp_monthly_from_staging(db: Session, slug: str) -> int:
    run_id = str(uuid4())
    sql = text("""
    WITH c AS (
      SELECT slug, COALESCE(ref_date::date, now()::date) AS ref_date
      FROM cases
      WHERE slug = :slug
    ),
    pick AS (  -- UNA sola riga di mapping per codice (specifica -> globale)
      SELECT imported_code, riclass_code
      FROM (
        SELECT imported_code, riclass_code,
               ROW_NUMBER() OVER (PARTITION BY imported_code ORDER BY (case_id IS NULL)) AS rn
        FROM stg_map_sp
        WHERE case_id IS NULL OR case_id = :slug
      ) x WHERE rn = 1
    )
    INSERT INTO fin_sp_monthly (case_id, period_key, riclass_code, amount, source, run_id)
    SELECT  t.case_id AS case_id,
            (EXTRACT(YEAR FROM COALESCE(t.period_end, c.ref_date, now()::date))::int * 100
             + EXTRACT(MONTH FROM COALESCE(t.period_end, c.ref_date, now()::date))::int) AS period_key,
            p.riclass_code,
            SUM(t.amount) AS amount,
            'TB' AS source,
            :run_id AS run_id
    FROM stg_tb_entries t
    JOIN c ON c.slug = t.case_id
    JOIN pick p ON p.imported_code = t.account_code
    WHERE t.case_id = :slug
    GROUP BY t.case_id, period_key, p.riclass_code
    ON CONFLICT (case_id, period_key, riclass_code)
    DO UPDATE SET amount = EXCLUDED.amount, source = EXCLUDED.source, run_id = EXCLUDED.run_id
    """)
    res = db.execute(sql, {"slug": slug, "run_id": run_id})
    db.commit()
    return res.rowcount or 0

def upsert_ce_monthly_from_staging(db: Session, slug: str) -> int:
    run_id = str(uuid4())
    sql = text("""
    WITH c AS (
      SELECT slug, COALESCE(ref_date::date, now()::date) AS ref_date
      FROM cases
      WHERE slug = :slug
    ),
    pick AS (
      SELECT imported_code, riclass_code
      FROM (
        SELECT imported_code, riclass_code,
               ROW_NUMBER() OVER (PARTITION BY imported_code ORDER BY (case_id IS NULL)) AS rn
        FROM stg_map_ce
        WHERE case_id IS NULL OR case_id = :slug
      ) x WHERE rn = 1
    )
    INSERT INTO fin_ce_monthly (case_id, period_key, riclass_code, amount, source, run_id)
    SELECT  t.case_id AS case_id,
            (EXTRACT(YEAR FROM COALESCE(t.period_end, c.ref_date, now()::date))::int * 100
             + EXTRACT(MONTH FROM COALESCE(t.period_end, c.ref_date, now()::date))::int) AS period_key,
            p.riclass_code,
            SUM(t.amount) AS amount,
            'TB' AS source,
            :run_id AS run_id
    FROM stg_tb_entries t
    JOIN c ON c.slug = t.case_id
    JOIN pick p ON p.imported_code = t.account_code
    WHERE t.case_id = :slug
    GROUP BY t.case_id, period_key, p.riclass_code
    ON CONFLICT (case_id, period_key, riclass_code)
    DO UPDATE SET amount = EXCLUDED.amount, source = EXCLUDED.source, run_id = EXCLUDED.run_id
    """)
    res = db.execute(sql, {"slug": slug, "run_id": run_id})
    db.commit()
    return res.rowcount or 0

def compute_case_monthly(
    db: Session,
    slug: str,
    period_from: Optional[int] = None,
    period_to: Optional[int] = None,
    full_refresh: bool = False
) -> dict:
    if full_refresh:
        params, cond = {"case_id": slug}, "case_id = :case_id"
        if period_from: cond += " AND period_key >= :pf"; params["pf"] = period_from
        if period_to:   cond += " AND period_key <= :pt"; params["pt"] = period_to
        db.execute(text(f"DELETE FROM fin_sp_monthly WHERE {cond}"), params)
        db.execute(text(f"DELETE FROM fin_ce_monthly WHERE {cond}"), params)
        db.commit()

    sp_rows = upsert_sp_monthly_from_staging(db, slug)
