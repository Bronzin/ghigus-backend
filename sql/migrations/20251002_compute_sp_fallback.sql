-- PATCH: funzione compute SP con fallback periodo e "prefisso più lungo vince"
CREATE OR REPLACE FUNCTION gh_compute_sp(p_case_id text)
RETURNS void
LANGUAGE sql
AS $$
WITH params AS (
  SELECT p_case_id::text AS slug
),
periods AS (
  SELECT
    COUNT(*) FILTER (WHERE e.period_end IS NOT NULL) AS nonnull,
    MAX(e.period_end) AS max_pe
  FROM stg_tb_entries e
  JOIN params p ON e.case_id = p.slug
),
e AS (  -- righe TB del caso + normalizzazione codice + fallback periodo
  SELECT
    e.case_id,
    e.account_code,
    e.account_name,
    COALESCE(e.amount, (COALESCE(e.debit,0) - COALESCE(e.credit,0))) AS entry_amount,
    NULLIF(REGEXP_REPLACE(REGEXP_REPLACE(e.account_code, '[^0-9]+', ''), '^0+', ''), '') AS code_digits
  FROM stg_tb_entries e
  JOIN params p ON e.case_id = p.slug
  CROSS JOIN periods pe
  WHERE pe.nonnull = 0          -- Fallback: tutti NULL -> niente filtro per periodo
     OR e.period_end = pe.max_pe -- Caso normale: usa solo MAX(period_end)
),
m AS (  -- mappa SP (globale o specifica per il caso), normalizzata a cifre
  SELECT
    NULLIF(REGEXP_REPLACE(REGEXP_REPLACE(m.imported_code, '[^0-9]+', ''), '^0+', ''), '') AS map_digits,
    m.riclass_code,
    m.riclass_desc
  FROM stg_map_sp m
  JOIN params p ON TRUE
  WHERE m.case_id IS NULL OR m.case_id = p.slug
),
matched AS (  -- tutte le corrispondenze di prefisso
  SELECT
    e.case_id,
    e.account_code,
    e.account_name,
    e.entry_amount,
    m.riclass_code,
    m.riclass_desc,
    LENGTH(m.map_digits) AS pref_len
  FROM e
  JOIN m ON e.code_digits IS NOT NULL AND e.code_digits LIKE m.map_digits || '%'
),
best AS (  -- prefisso più lungo vince, per ciascun account_code
  SELECT *
  FROM (
    SELECT
      case_id, account_code, account_name, entry_amount, riclass_code, riclass_desc, pref_len,
      ROW_NUMBER() OVER (PARTITION BY case_id, account_code ORDER BY pref_len DESC) AS rn
    FROM matched
  ) x
  WHERE rn = 1
),
agg AS (  -- aggregazione finale per riclass
  SELECT
    case_id,
    riclass_code,
    riclass_desc,
    SUM(entry_amount) AS amount
  FROM best
  GROUP BY case_id, riclass_code, riclass_desc
),
purge AS (  -- pulizia vecchie righe del caso
  DELETE FROM fin_sp_riclass WHERE case_id = p_case_id RETURNING 1
)
INSERT INTO fin_sp_riclass (case_id, riclass_code, riclass_desc, amount, created_at)
SELECT p_case_id, riclass_code, riclass_desc, amount, NOW()
FROM agg;
$$;
