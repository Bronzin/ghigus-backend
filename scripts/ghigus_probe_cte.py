# P:\Github\ghigus-backend\scripts\ghigus_probe_cte.py
import os, sys
from sqlalchemy import create_engine, text, inspect

DB=os.environ.get("DATABASE_URL") or sys.exit("Set DATABASE_URL")
PRATICA=os.environ.get("GHIGUS_PRATICA","pratica4")

eng=create_engine(DB)
insp=inspect(eng)

def type_category(t)->str:
    s=str(t).lower()
    if any(k in s for k in ["int","serial","bigint","smallint"]): return "int"
    if any(k in s for k in ["char","text","varchar"]): return "str"
    return "other"

def resolve_case():
    cases = next((t for t in insp.get_table_names() if t in ("cases","pratiche","practice","case")), None)
    if not cases: raise SystemExit("Tabella cases/pratiche non trovata")
    cols_meta = insp.get_columns(cases)
    cols = [c["name"] for c in cols_meta]
    pk = "id" if "id" in cols else ( "slug" if "slug" in cols else cols[0] )
    pk_type = type_category(next(cm for cm in cols_meta if cm["name"]==pk)["type"])
    slug_col = "slug" if "slug" in cols else None

    with eng.begin() as c:
        if PRATICA.isdigit():
            row = c.execute(text(f"select {pk}" + (f", {slug_col}" if slug_col else "") + f" from {cases} where {pk}=:v limit 1"), {"v": int(PRATICA)}).fetchone()
        else:
            if slug_col:
                row = c.execute(text(f"select {pk}, {slug_col} from {cases} where {slug_col}=:v limit 1"), {"v": PRATICA}).fetchone()
            else:
                row = c.execute(text(f"select {pk} from {cases} where {pk}=:v limit 1"), {"v": PRATICA}).fetchone()
        if not row: raise SystemExit(f"Pratica '{PRATICA}' non trovata")
        pk_val=row[0]
        slug_val=row[1] if slug_col and len(row)>1 else None
    return {"cases":cases,"pk":pk,"pk_type":pk_type,"slug_col":slug_col,"pk_val":pk_val,"slug_val":slug_val}

def resolve_tb():
    TB="stg_tb_entries"
    cols_meta=insp.get_columns(TB)
    cols=[c["name"] for c in cols_meta]
    case_col="case_id" if "case_id" in cols else ("slug" if "slug" in cols else None)
    if not case_col: raise SystemExit(f"{TB} non ha né case_id né slug")
    case_type=type_category(next(cm for cm in cols_meta if cm["name"]==case_col)["type"])
    acc_col = "account_code" if "account_code" in cols else next((c for c in cols if "code" in c.lower()), None)
    if not acc_col: raise SystemExit(f"{TB} non ha una colonna account_code/code")
    amt_expr = "coalesce(e.debit,0) - coalesce(e.credit,0)" if "debit" in cols and "credit" in cols else ("e.amount" if "amount" in cols else "0")
    name_col = "account_name" if "account_name" in cols else None
    return {"TB":TB,"case_col":case_col,"case_type":case_type,"acc_col":acc_col,"amt_expr":amt_expr,"name_col":name_col}

def resolve_map(table):
    cols=[c["name"] for c in insp.get_columns(table)]
    map_acc = "imported_code" if "imported_code" in cols else ("account_code" if "account_code" in cols else None)
    map_rc  = "riclass_code" if "riclass_code" in cols else None
    map_rd  = "riclass_desc" if "riclass_desc" in cols else None
    if not (map_acc and map_rc): raise SystemExit(f"{table}: mappa priva di imported_code/riclass_code (cols={cols})")
    imp_desc = "imported_desc" if "imported_desc" in cols else None
    return {"map_acc":map_acc,"map_rc":map_rc,"map_rd":map_rd,"imp_desc":imp_desc}

ctx_case=resolve_case()
ctx_tb  =resolve_tb()
ctx_sp  =resolve_map("stg_map_sp")
ctx_ce  =resolve_map("stg_map_ce")

with eng.begin() as c:
    # valore per filtrare TB
    if ctx_tb["case_type"]=="int":
        # prova a ricavare id numerico dalla cases (se pk è int usa quello, altrimenti cerca una colonna id numerica)
        # prova rapida: prima cerca case_id nella TB presente con lo stesso valore della PK se è int
        tbval = ctx_case["pk_val"] if ctx_case["pk_type"]=="int" else None
        if tbval is None:
            # tenta di recuperare un id numerico dalla tabella cases
            # best effort: prova "id" anche se non è PK
            try:
                row=c.execute(text(f"select id from {ctx_case['cases']} where {ctx_case['slug_col']}=:s"),{"s":ctx_case["slug_val"]}).fetchone() if ctx_case["slug_col"] else None
                tbval=int(row[0]) if row else None
            except Exception:
                tbval=None
        if tbval is None:
            print(f"[ERRORE] {ctx_tb['TB']}.{ctx_tb['case_col']} è INT ma non ho un id numerico per '{PRATICA}'"); sys.exit(1)
    else:
        tbval = ctx_case["slug_val"] or (str(ctx_case["pk_val"]) if ctx_case["pk_type"]=="str" else None)
        if tbval is None:
            print(f"[ERRORE] {ctx_tb['TB']}.{ctx_tb['case_col']} è testo ma non ho slug"); sys.exit(1)

    print(f"[info] TB filter: {ctx_tb['TB']}.{ctx_tb['case_col']} = {tbval!r}")

    # quante righe TB dopo filtro?
    tb_cnt = c.execute(text(f"select count(*) from {ctx_tb['TB']} e where e.{ctx_tb['case_col']}=:v"), {"v": tbval}).scalar_one()
    print(f"[info] TB rows after filter: {tb_cnt}")

    def run_probe(map_table, ctx_map):
        # conta match in ogni fase per capire dove si svuota
        # 1) quanti codici TB (solo cifre) abbiamo?
        e_codes = c.execute(text(f"""
            with e as (
              select distinct regexp_replace(e.{ctx_tb['acc_col']}, '[^0-9]', '', 'g') as code_digits
              from {ctx_tb['TB']} e
              where e.{ctx_tb['case_col']}=:v
            )
            select count(*) from e where code_digits<>''
        """), {"v": tbval}).scalar_one()

        # 2) quanti codici mappa (solo cifre)?
        m_codes = c.execute(text(f"""
            with m as (
              select distinct regexp_replace(m.{ctx_map['map_acc']}, '[^0-9]', '', 'g') as map_digits
              from {map_table} m
            )
            select count(*) from m where map_digits<>''
        """)).scalar_one()

        # 3) quante coppie prefisso (pairs)?
        pairs_cnt = c.execute(text(f"""
            with e as (
              select distinct regexp_replace(e.{ctx_tb['acc_col']}, '[^0-9]', '', 'g') as code_digits
              from {ctx_tb['TB']} e
              where e.{ctx_tb['case_col']}=:v
            ),
            m as (
              select distinct regexp_replace(m.{ctx_map['map_acc']}, '[^0-9]', '', 'g') as map_digits
              from {map_table} m
            ),
            pairs as (
              select e.code_digits, m.map_digits, char_length(m.map_digits) as l
              from e join m on e.code_digits like m.map_digits || '%'
            )
            select count(*) from pairs
        """), {"v": tbval}).scalar_one()

        # 4) quante 'best' (dopo scelta prefisso più lungo)?
        best_cnt = c.execute(text(f"""
            with e as (
              select distinct regexp_replace(e.{ctx_tb['acc_col']}, '[^0-9]', '', 'g') as code_digits
              from {ctx_tb['TB']} e
              where e.{ctx_tb['case_col']}=:v
            ),
            m as (
              select distinct regexp_replace(m.{ctx_map['map_acc']}, '[^0-9]', '', 'g') as map_digits
              from {map_table} m
            ),
            pairs as (
              select e.code_digits, m.map_digits, char_length(m.map_digits) as l
              from e join m on e.code_digits like m.map_digits || '%'
            ),
            best as (
              select distinct on (code_digits) code_digits, map_digits, l
              from pairs
              order by code_digits, l desc
            )
            select count(*) from best
        """), {"v": tbval}).scalar_one()

        # 5) risultato finale: righe e somme (senza HAVING e con HAVING)
        sums = c.execute(text(f"""
            with e0 as (
              select regexp_replace(e.{ctx_tb['acc_col']}, '[^0-9]', '', 'g') as code_digits,
                     {ctx_tb['amt_expr']} as amount
              from {ctx_tb['TB']} e
              where e.{ctx_tb['case_col']}=:v
            ),
            e as (
              select code_digits, sum(amount) as amount
              from e0
              where code_digits<>''
              group by code_digits
            ),
            m as (
              select regexp_replace(m.{ctx_map['map_acc']}, '[^0-9]', '', 'g') as map_digits
                   , {ctx_map['map_rc']} as rc
                   , coalesce({ctx_map['map_rd']},{ctx_map['map_rc']}) as rd
              from {map_table} m
              where regexp_replace(m.{ctx_map['map_acc']}, '[^0-9]', '', 'g')<>''
            ),
            pairs as (
              select e.code_digits, e.amount, m.rc, m.rd, char_length(m.map_digits) as l
              from e join m on e.code_digits like m.map_digits || '%'
            ),
            best as (
              select distinct on (code_digits) code_digits, rc, rd
              from pairs
              order by code_digits, l desc
            ),
            agg as (
              select b.rc, b.rd, sum(e.amount) as amount, sum(abs(e.amount)) as abs_amount
              from best b join e on e.code_digits=b.code_digits
              group by b.rc, b.rd
            )
            select count(*) as rows_all
                 , sum(amount) as total_amount
                 , sum(abs_amount) as total_abs
                 , sum(case when amount<>0 then 1 else 0 end) as rows_nonzero
            from agg
        """), {"v": tbval}).fetchone()

        print(f"[{map_table}] e_codes={e_codes}, m_codes={m_codes}, pairs={pairs_cnt}, best={best_cnt}, rows_all={sums[0]}, total={sums[1]}, total_abs={sums[2]}, rows_nonzero={sums[3]}")

    run_probe("stg_map_sp", ctx_sp)
    run_probe("stg_map_ce", ctx_ce)
