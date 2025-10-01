import os, sys
from sqlalchemy import create_engine, text
DB=os.environ.get("DATABASE_URL") or sys.exit("Set DATABASE_URL")
eng=create_engine(DB)

sql=r"""
with e as (
  select distinct regexp_replace(account_code,'[^0-9]','','g') as d
  from stg_tb_entries
  where regexp_replace(account_code,'[^0-9]','','g')<> ''
),
m as (
  select distinct regexp_replace(imported_code,'[^0-9]','','g') as d
  from stg_map_sp
  where regexp_replace(imported_code,'[^0-9]','','g')<> ''
)
select len,
       sum(case when exists (
             select 1 from m where e.d like left(m.d,len) || '%'
           ) then 1 else 0 end) as covered,
       count(*) as total
from e, lateral (values (1),(2),(3),(4)) as L(len)
group by len order by len;
"""
with eng.begin() as c:
    rows=c.execute(text(sql)).fetchall()
    for len_, covered, total in rows:
        print(f"prefix_len={len_}: covered={covered}/{total}")
