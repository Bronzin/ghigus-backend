# P:\Github\ghigus-backend\scripts\ghigus_compute_riclass.py
r"""
Backfill mirato per UNA pratica (slug o id).

SP
- saldo all'ULTIMO period_end (se non esiste period_end, usa tutte le righe disponibili)

CE
- tenta JOIN per CODICE (solo cifre, rimozione zeri iniziali, prefisso bidirezionale, prefisso più lungo)
- fallback su DESCRIZIONE SOLO SE la mappa ha 'imported_desc' e TB ha 'account_name'
- Importi: preferisci debit-credit, altrimenti amount
"""
import argparse, os
from typing import Optional, Tuple, List
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

MAP_SP = "stg_map_sp"
MAP_CE = "stg_map_ce"
TB_RAW = "stg_tb_entries"
FIN_SP = "fin_sp_riclass"
FIN_CE = "fin_ce_riclass"
FIN_CASE_COL = "case_id"

ACCOUNT_ALIASES = ["imported_code", "account_code", "code", "codice", "account", "chart_code", "accountnumber", "account_no"]
RICLASS_CODE_ALIASES = ["riclass_code", "class_code", "riclass", "sp_code", "ce_code", "cluster", "bucket"]
RICLASS_DESC_ALIASES = ["riclass_desc", "class_desc", "descrizione", "description", "desc"]
RAW_CASE_ALIASES    = ["case_id", "pratica_id", "case_slug", "slug"]
TB_NAME_ALIASES     = ["account_name", "descrizione", "description", "account_desc", "nome_conto", "name"]

def connect(db_url: Optional[str]) -> Engine:
    url = db_url or os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL non impostata e --db mancante")
    return create_engine(url)

def find_first_existing_table(inspector, candidates: List[str]) -> Optional[str]:
    existing = set(inspector.get_table_names())
    for c in candidates:
        if c in existing:
            return c
    return None

def type_category(sqlatype_obj) -> str:
    s=str(sqlatype_obj).lower()
    if any(k in s for k in ["int","serial","bigint","smallint"]): return "int"
    if any(k in s for k in ["char","text","varchar"]): return "str"
    return "other"

def pick(colnames: List[str], aliases: List[str]) -> Optional[str]:
    low = {n.lower(): n for n in colnames}
    for a in aliases:
        if a in low: return low[a]
    return None

def col_exists(engine: Engine, table: str, col: str) -> bool:
    with engine.begin() as c:
        row = c.execute(text("""
            select 1
            from information_schema.columns
            where table_name=:t and column_name=:c
            limit 1
        """), {"t": table, "c": col}).fetchone()
    return row is not None

def resolve_case_keys(engine: Engine, pratica: str):
    insp = inspect(engine)
    cases = find_first_existing_table(insp, ["cases","pratiche","practice","case"])
    if not cases: raise SystemExit("Tabella cases/pratiche non trovata")
    cols_meta = insp.get_columns(cases)
    cols = [c["name"] for c in cols_meta]
    pk_cols = inspect(engine).get_pk_constraint(cases).get("constrained_columns") or []
    if not pk_cols: pk_cols = ["id"] if "id" in cols else []
    if not pk_cols and "slug" in cols: pk_cols = ["slug"]
    if not pk_cols: raise SystemExit(f"Impossibile determinare la PK di {cases}")
    pk_col = pk_cols[0]
    pk_type = type_category(next(cm for cm in cols_meta if cm["name"]==pk_col)["type"])
    slug_col = next((c for c in ("slug","name","code","pratica_slug","case_slug") if c in cols), None)
    num_id_col = None
    for cand in ("id","case_id","pratica_id"):
        if cand in cols:
            t = type_category(next(cm for cm in cols_meta if cm["name"]==cand)["type"])
            if t=="int": num_id_col=cand; break

    with engine.begin() as c:
        if pratica.isdigit():
            if num_id_col:
                row = c.execute(text(f"select {pk_col}" + (f", {slug_col}" if slug_col else "") +
                                     f" from {cases} where {num_id_col}=:nid limit 1"),
                                {"nid": int(pratica)}).fetchone()
            elif pk_type=="int":
                row = c.execute(text(f"select {pk_col}" + (f", {slug_col}" if slug_col else "") +
                                     f" from {cases} where {pk_col}=:nid limit 1"),
                                {"nid": int(pratica)}).fetchone()
            else:
                raise SystemExit("ID numerico passato ma cases non ha id numerico utilizzabile.")
            if not row: raise SystemExit(f"Pratica id {pratica} non trovata")
            pk_value=row[0]; slug_value=str(row[1]) if slug_col and len(row)>1 else None
            numeric_id_value = int(pratica) if num_id_col else (int(pk_value) if pk_type=="int" else None)
        else:
            if slug_col:
                row = c.execute(text(f"select {pk_col}" + (f", {slug_col}" if slug_col else "") +
                                     (f", {num_id_col}" if num_id_col else "") +
                                     f" from {cases} where {slug_col}=:s limit 1"),
                                {"s": pratica}).fetchone()
            else:
                if pk_type!="str": raise SystemExit("Nessun slug e PK non testuale")
                row = c.execute(text(f"select {pk_col} from {cases} where {pk_col}=:s limit 1"),
                                {"s": pratica}).fetchone()
            if not row: raise SystemExit(f"Pratica slug '{pratica}' non trovata")
            if slug_col and num_id_col:
                pk_value, slug_value, numeric_id_value = row[0], row[1], row[2]
            elif slug_col:
                pk_value, slug_value, numeric_id_value = row[0], row[1], None
            else:
                pk_value, slug_value, numeric_id_value = row[0], None, None

    return {"cases_table":cases,"pk_col":pk_col,"pk_type":pk_type,"slug_col":slug_col,
            "num_id_col":num_id_col,"pk_value":pk_value,"slug_value":slug_value,"numeric_id_value":numeric_id_value}

def resolve_map_columns(engine: Engine, table_name: str):
    insp = inspect(engine)
    cols = [c["name"] for c in insp.get_columns(table_name)]
    acc = pick(cols, ACCOUNT_ALIASES)
    rc  = pick(cols, RICLASS_CODE_ALIASES)
    rd  = pick(cols, RICLASS_DESC_ALIASES)
    if not acc or not rc:
        raise SystemExit(f"Impossibile risolvere colonne mappa per {table_name}. Colonne: {cols}")
    return acc, rc, rd

def resolve_tb_columns(engine: Engine):
    insp = inspect(engine)
    cols_meta = insp.get_columns(TB_RAW)
    cols = [c["name"] for c in cols_meta]
    tb_acc = pick(cols, ACCOUNT_ALIASES) or "account_code"
    tb_name = pick(cols, TB_NAME_ALIASES)
    tb_case = pick(cols, RAW_CASE_ALIASES) or "case_id"
    tb_case_type = type_category(next(cm for cm in cols_meta if cm["name"]==tb_case)["type"])
    if "debit" in cols and "credit" in cols:
        amt_expr = "coalesce(e.debit,0) - coalesce(e.credit,0)"
    elif "amount" in cols:
        amt_expr = "e.amount"
    else:
        amt_expr = "0"
    period_col = "period_end" if "period_end" in cols else None
    return tb_acc, tb_name, tb_case, tb_case_type, amt_expr, period_col

def resolve_fin_case_type(engine: Engine, fin_table: str) -> str:
    insp = inspect(engine)
    cols_meta = insp.get_columns(fin_table)
    col = next((cm for cm in cols_meta if cm["name"]==FIN_CASE_COL), None)
    if not col: raise SystemExit(f"{fin_table} manca la colonna '{FIN_CASE_COL}'")
    return type_category(col["type"])

def get_periods(engine: Engine, tb_case: str, period_col: Optional[str], tb_filter_val):
    if not period_col:
        return None, None
    with engine.begin() as c:
        last = c.execute(text(f"select max({period_col}) from {TB_RAW} where {tb_case}=:v"), {"v": tb_filter_val}).scalar()
        if last is None:
            return None, None
        prev = c.execute(text(f"select max({period_col}) from {TB_RAW} where {tb_case}=:v and {period_col} < :last"),
                         {"v": tb_filter_val, "last": last}).scalar()
        return last, prev

# ---------------- SP (ultimo periodo) ----------------
def insert_riclass_sp(engine: Engine, case_ctx: dict, map_table: str, fin_table: str):
    insp = inspect(engine)
    for t in (TB_RAW, map_table, fin_table):
        if t not in insp.get_table_names():
            raise SystemExit(f"Tabella '{t}' non trovata nel DB")

    map_acc, map_rc, map_rd = resolve_map_columns(engine, map_table)
    tb_acc, tb_name, tb_case, tb_case_type, amt_expr, period_col = resolve_tb_columns(engine)
    fin_case_type = resolve_fin_case_type(engine, fin_table)

    if tb_case_type=="int":
        tb_filter_val = case_ctx["numeric_id_value"] or (int(case_ctx["pk_value"]) if case_ctx["pk_type"]=="int" else None)
        if tb_filter_val is None: raise SystemExit(f"{TB_RAW}.{tb_case} è INT ma non ho id numerico per la pratica.")
    else:
        tb_filter_val = case_ctx["slug_value"] or (str(case_ctx["pk_value"]) if case_ctx["pk_type"]=="str" else None)
        if tb_filter_val is None: raise SystemExit(f"{TB_RAW}.{tb_case} è testo ma non ho slug/testo per la pratica.")

    if fin_case_type=="int":
        fin_case_val = case_ctx["numeric_id_value"] or (int(case_ctx["pk_value"]) if case_ctx["pk_type"]=="int" else None)
    else:
        fin_case_val = case_ctx["slug_value"] or (str(case_ctx["pk_value"]) if case_ctx["pk_type"]=="str" else None)

    rd_select = f", coalesce(m.{map_rd}, m.{map_rc})" if map_rd else f", m.{map_rc}"
    rd_group  = f", m.{map_rd}" if map_rd else ""

    last_period, _ = get_periods(engine, tb_case, period_col, tb_filter_val)
    sql_delete = text(f"delete from {fin_table} where {FIN_CASE_COL}=:finval")
    period_filter = f"and e.{period_col} = :p_last" if last_period is not None else ""

    sql_insert = text(f"""
        with e0 as (
          select
            nullif(regexp_replace(regexp_replace(e.{tb_acc}, '[^0-9]', '', 'g'), '^0+', ''), '') as code_digits,
            {amt_expr} as amount
          from {TB_RAW} e
          where e.{tb_case} = :tbval {period_filter}
        ),
        e as (
          select code_digits, sum(amount) as amount
          from e0
          where code_digits is not null
          group by code_digits
        ),
        m as (
          select
            nullif(regexp_replace(regexp_replace(m.{map_acc}, '[^0-9]', '', 'g'), '^0+', ''), '') as map_digits,
            m.{map_rc} as riclass_code
            {rd_select} as riclass_desc
          from {map_table} m
          where nullif(regexp_replace(regexp_replace(m.{map_acc}, '[^0-9]', '', 'g'), '^0+', ''), '') is not null
        ),
        pairs as (
          select e.code_digits, e.amount, m.riclass_code, m.riclass_desc, char_length(m.map_digits) as l
          from e
          join m
            on (e.code_digits like m.map_digits || '%')
            or (m.map_digits like e.code_digits || '%')
        ),
        best as (
          select distinct on (code_digits) code_digits, riclass_code, riclass_desc, l
          from pairs
          order by code_digits, l desc
        ),
        agg as (
          select b.riclass_code, b.riclass_desc, sum(e.amount) as amount
          from best b
          join e on e.code_digits = b.code_digits
          group by b.riclass_code, b.riclass_desc
          having sum(e.amount) <> 0
        )
        insert into {fin_table} ({FIN_CASE_COL}, riclass_code, riclass_desc, amount, created_at)
        select :finval, riclass_code, riclass_desc, amount, CURRENT_TIMESTAMP
        from agg
    """)

    with engine.begin() as c:
        c.execute(sql_delete, {"finval": fin_case_val})
        params = {"finval": fin_case_val, "tbval": tb_filter_val}
        if last_period is not None:
            params["p_last"] = last_period
        c.execute(sql_insert, params)

# ---------------- CE (YTD) con join codice e fallback descrizione SOLO se disponibile ----------------
def insert_riclass_ce(engine: Engine, case_ctx: dict, map_table: str, fin_table: str):
    insp = inspect(engine)
    for t in (TB_RAW, map_table, fin_table):
        if t not in insp.get_table_names():
            raise SystemExit(f"Tabella '{t}' non trovata nel DB")

    map_acc, map_rc, map_rd = resolve_map_columns(engine, map_table)
    tb_acc, tb_name, tb_case, tb_case_type, amt_expr, period_col = resolve_tb_columns(engine)
    fin_case_type = resolve_fin_case_type(engine, fin_table)

    # esiste imported_desc in questa mappa?
    has_imp_desc = col_exists(engine, map_table, "imported_desc")
    # esiste account_name in TB?
    has_tb_name  = (tb_name is not None)

    if tb_case_type=="int":
        tb_filter_val = case_ctx["numeric_id_value"] or (int(case_ctx["pk_value"]) if case_ctx["pk_type"]=="int" else None)
        if tb_filter_val is None: raise SystemExit(f"{TB_RAW}.{tb_case} è INT ma non ho id numerico per la pratica.")
    else:
        tb_filter_val = case_ctx["slug_value"] or (str(case_ctx["pk_value"]) if case_ctx["pk_type"]=="str" else None)
        if tb_filter_val is None: raise SystemExit(f"{TB_RAW}.{tb_case} è testo ma non ho slug/testo per la pratica.")

    if fin_case_type=="int":
        fin_case_val = case_ctx["numeric_id_value"] or (int(case_ctx["pk_value"]) if case_ctx["pk_type"]=="int" else None)
    else:
        fin_case_val = case_ctx["slug_value"] or (str(case_ctx["pk_value"]) if case_ctx["pk_type"]=="str" else None)

    rd_select = f", coalesce(m.{map_rd}, m.{map_rc})" if map_rd else f", m.{map_rc}"
    rd_group  = f", m.{map_rd}" if map_rd else ""

    # pezzi opzionali per descrizione
    m_imp_name_norm_sel = "upper(regexp_replace(m.imported_desc, '[^0-9A-Za-z]', '', 'g')) as imp_name_norm" if has_imp_desc else "null as imp_name_norm"
    e_name_norm_sel     = f"upper(regexp_replace(e.{tb_name}, '[^0-9A-Za-z]', '', 'g')) as name_norm" if has_tb_name else "null as name_norm"
    desc_join_condition = " or m.imp_name_norm = e.name_norm" if (has_imp_desc and has_tb_name) else ""

    sql_delete = text(f"delete from {fin_table} where {FIN_CASE_COL}=:finval")

    sql_insert = text(f"""
        with e0 as (
          select
            nullif(regexp_replace(regexp_replace(e.{tb_acc}, '[^0-9]', '', 'g'), '^0+', ''), '') as code_digits,
            {amt_expr} as amount,
            {e_name_norm_sel}
          from {TB_RAW} e
          where e.{tb_case} = :tbval
        ),
        e as (
          select code_digits, sum(amount) as amount,
                 max(name_norm) as name_norm
          from e0
          where code_digits is not null or name_norm is not null
          group by code_digits
        ),
        m as (
          select
            nullif(regexp_replace(regexp_replace(m.{map_acc}, '[^0-9]', '', 'g'), '^0+', ''), '') as map_digits,
            m.{map_rc} as riclass_code
            {rd_select} as riclass_desc,
            {m_imp_name_norm_sel}
          from {map_table} m
        ),
        pairs as (
          select
            e.code_digits, e.amount, e.name_norm,
            m.riclass_code, m.riclass_desc,
            char_length(m.map_digits) as l_code,
            case when m.map_digits is not null and e.code_digits is not null
                 and (e.code_digits like m.map_digits || '%' or m.map_digits like e.code_digits || '%')
                 then 1 else 0 end as code_match,
            case when m.imp_name_norm is not null and e.name_norm is not null and m.imp_name_norm = e.name_norm
                 then 1 else 0 end as name_match
          from e
          join m on
             ( (e.code_digits is not null and m.map_digits is not null and
                 (e.code_digits like m.map_digits || '%' or m.map_digits like e.code_digits || '%'))
               {desc_join_condition}
             )
        ),
        ranked as (
          select
            code_digits,
            riclass_code, riclass_desc,
            row_number() over (
              partition by code_digits
              order by code_match desc,  -- prima i match per codice
                       name_match desc,  -- poi quelli per nome (se possibile)
                       l_code desc
            ) as rk
          from pairs
        ),
        best as (
          select code_digits, riclass_code, riclass_desc
          from ranked
          where rk = 1
        ),
        agg as (
          select b.riclass_code, b.riclass_desc, sum(e.amount) as amount
          from best b
          join e on e.code_digits = b.code_digits
          group by b.riclass_code, b.riclass_desc
          having sum(e.amount) <> 0
        )
        insert into {fin_table} ({FIN_CASE_COL}, riclass_code, riclass_desc, amount, created_at)
        select :finval, riclass_code, riclass_desc, amount, CURRENT_TIMESTAMP
        from agg
    """)

    with engine.begin() as c:
        c.execute(sql_delete, {"finval": fin_case_val})
        c.execute(sql_insert, {"finval": fin_case_val, "tbval": tb_filter_val})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", help="SQLAlchemy DB URL (fallback: env DATABASE_URL)")
    ap.add_argument("--pratica", required=True, help="slug o id pratica (es: pratica4)")
    args = ap.parse_args()

    eng = connect(args.db)
    case_ctx = resolve_case_keys(eng, args.pratica)

    insert_riclass_sp(eng, case_ctx, MAP_SP, FIN_SP)
    insert_riclass_ce(eng, case_ctx, MAP_CE, FIN_CE)

    with eng.begin() as c:
        def fin_key_value(table: str):
            t = resolve_fin_case_type(eng, table)
            return case_ctx["numeric_id_value"] if t=="int" else (case_ctx["slug_value"] or str(case_ctx["pk_value"]))
        sp = c.execute(text(f"select count(*), coalesce(sum(amount),0) from {FIN_SP} where {FIN_CASE_COL}=:v"),
                       {"v": fin_key_value(FIN_SP)}).fetchone()
        ce = c.execute(text(f"select count(*), coalesce(sum(amount),0) from {FIN_CE} where {FIN_CASE_COL}=:v"),
                       {"v": fin_key_value(FIN_CE)}).fetchone()
        print(f"[OK] {FIN_SP}: {sp[0]} righe, totale={sp[1]}")
        print(f"[OK] {FIN_CE}: {ce[0]} righe, totale={ce[1]}")

if __name__ == "__main__":
    main()
