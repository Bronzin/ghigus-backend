# app/services/compute_cflow.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncConnection

CFLOW_COMPUTE_SQL = """
WITH tb AS (
  SELECT
    t.case_id,
    (EXTRACT(YEAR FROM t.period_end)::int * 100 + EXTRACT(MONTH FROM t.period_end)::int) AS period_key,
    t.imported_code,
    t.amount
  FROM stg_tb_entries t
  WHERE t.case_id = :case_id
),
tb_in_range AS (
  SELECT *
  FROM tb
  WHERE period_key BETWEEN :period_from AND :period_to
),
tb_mapped AS (
  SELECT
    tb.case_id,
    tb.period_key,
    COALESCE(m.cflow_category, 'OPERATING') AS cflow_category,
    SUM(tb.amount) AS amount
  FROM tb_in_range tb
  LEFT JOIN lkp_cflow_map m ON m.imported_code = tb.imported_code
  GROUP BY tb.case_id, tb.period_key, COALESCE(m.cflow_category, 'OPERATING')
)
INSERT INTO fin_cflow_monthly (case_id, period_key, cflow_category, amount, source)
SELECT case_id, period_key, cflow_category, amount, 'TB'
FROM tb_mapped
ON CONFLICT (case_id, period_key, cflow_category)
DO UPDATE SET
  amount = EXCLUDED.amount,
  source = 'TB',
  created_at = now();
"""

CFLOW_CLEAR_SQL = """
DELETE FROM fin_cflow_monthly
WHERE case_id = :case_id
  AND period_key BETWEEN :period_from AND :period_to;
"""


async def compute_cflow_monthly(
    conn: AsyncConnection,
    case_id: str,
    period_from: int,
    period_to: int,
    full_refresh: Optional[bool] = False,
) -> None:
    """
    Calcola e scrive il Cash Flow mensile (metodo diretto) per le categorie
    OPERATING / INVESTING / FINANCING usando la lookup lkp_cflow_map.

    :param conn: Async SQLAlchemy connection
    :param case_id: slug/case id
    :param period_from: YYYYMM
    :param period_to: YYYYMM
    :param full_refresh: se True cancella e rigenera il range
    """
    if full_refresh:
        await conn.execute(
            CFLOW_CLEAR_SQL,
            {"case_id": case_id, "period_from": period_from, "period_to": period_to},
        )
    await conn.execute(
        CFLOW_COMPUTE_SQL,
        {"case_id": case_id, "period_from": period_from, "period_to": period_to},
    )
