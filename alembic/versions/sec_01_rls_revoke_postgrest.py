"""Security: enable RLS on all tables, revoke PostgREST access, fix SECURITY DEFINER views.

Revision ID: sec_01_rls_revoke
Revises: auth_01_users
"""
from alembic import op

revision = "sec_01_rls_revoke"
down_revision = "auth_01_users"
branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Tutte le tabelle public segnalate dal linter Supabase (RLS disabled)
# ---------------------------------------------------------------------------
TABLES = [
    "users",
    "companies",
    "cases",
    "case_snapshots",
    "uploads",
    "assumptions",
    "alembic_version",
    "stg_tb_entries",
    "stg_xbrl_facts",
    "stg_map_sp",
    "stg_map_ce",
    "stg_map_sp_backup",
    "stg_map_ce_backup",
    "backup_stg_map_sp",
    "backup_stg_map_ce",
    "fin_sp_riclass",
    "fin_ce_riclass",
    "fin_sp_monthly",
    "fin_ce_monthly",
    "fin_banks_monthly",
    "fin_cflow_monthly",
    "fin_kpi_monthly",
    "fin_kpi_standard",
    "lkp_cflow_map",
    "lkp_banks_master",
    "lkp_banks_map",
    "dim_calendar",
    "dim_month",
    "mdm_attivo_items",
    "mdm_attivo_schedule",
    "mdm_scenarios",
    "mdm_passivo_items",
    "mdm_passivo_tipologie",
    "mdm_liquidazione",
    "mdm_cessione_monthly",
    "mdm_concordato_monthly",
    "mdm_affitto_monthly",
    "mdm_prededuzione_monthly",
    "mdm_ce_projection",
    "mdm_sp_projection",
    "mdm_cflow_projection",
    "mdm_banca_projection",
    "mdm_test_piat",
    "mdm_nuovo_finanziamento",
    "mdm_finanziamento_schedule",
    "mdm_scadenziario_tributario",
    "mdm_scadenziario_tributario_rate",
    "mdm_imm_fin_movimenti",
]

# ---------------------------------------------------------------------------
# Viste con SECURITY DEFINER da convertire a SECURITY INVOKER
# ---------------------------------------------------------------------------
VIEWS = [
    "vw_financials_monthly_wide",
    "vw_financials_monthly",
    "vw_financials_monthly_long_full",
    "vw_banks_monthly_wide",
    "vw_banks_monthly",
    "vw_cf_monthly",
    "vw_kpi_base",
    "vw_fin_kpi_latest",
    "vw_fin_kpi_standard_latest",
    "vw_sp_map_coverage",
    "vw_ce_map_coverage",
    "vw_sp_unmapped_sample",
    "vw_ce_unmapped_sample",
    "v_ce_monthly_summary",
    "v_sp_monthly_summary",
]

POSTGREST_ROLES = ["anon", "authenticated"]


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Revoke accesso PostgREST ai ruoli anon / authenticated
    # ------------------------------------------------------------------
    for role in POSTGREST_ROLES:
        op.execute(f"REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM {role};")
        op.execute(f"REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM {role};")
        op.execute(f"REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM {role};")
        # Impedisci accesso anche a oggetti creati in futuro
        op.execute(
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            f"REVOKE ALL ON TABLES FROM {role};"
        )
        op.execute(
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            f"REVOKE ALL ON SEQUENCES FROM {role};"
        )
        op.execute(
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            f"REVOKE ALL ON FUNCTIONS FROM {role};"
        )

    # ------------------------------------------------------------------
    # 2. Abilita RLS su tutte le tabelle (senza policy = deny-all)
    #    Il ruolo postgres / service_role bypassa RLS di default.
    # ------------------------------------------------------------------
    for table in TABLES:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")

    # ------------------------------------------------------------------
    # 3. Converti viste da SECURITY DEFINER → SECURITY INVOKER
    # ------------------------------------------------------------------
    for view in VIEWS:
        op.execute(f"ALTER VIEW public.{view} SET (security_invoker = on);")


def downgrade() -> None:
    # Ripristina viste a SECURITY DEFINER
    for view in VIEWS:
        op.execute(f"ALTER VIEW public.{view} SET (security_invoker = off);")

    # Disabilita RLS
    for table in TABLES:
        op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;")

    # Ripristina grant di default Supabase per anon/authenticated
    for role in POSTGREST_ROLES:
        op.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role};")
        op.execute(f"GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO {role};")
        op.execute(
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            f"GRANT SELECT ON TABLES TO {role};"
        )
        op.execute(
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            f"GRANT USAGE ON SEQUENCES TO {role};"
        )
