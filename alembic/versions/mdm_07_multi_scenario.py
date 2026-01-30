"""MDM: multi-scenario support

Revision ID: mdm_07_multi_scenario
Revises: mdm_06_concordato_scheduling
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_07_multi_scenario"
down_revision = "mdm_06_concordato_scheduling"
branch_labels = None
depends_on = None

# All tables that need scenario_id
MDM_TABLES = [
    "mdm_attivo_items",
    "mdm_passivo_items",
    "mdm_passivo_tipologie",
    "mdm_liquidazione",
    "mdm_test_piat",
    "mdm_prededuzione_monthly",
    "mdm_affitto_monthly",
    "mdm_cessione_monthly",
    "mdm_ce_projection",
    "mdm_sp_projection",
    "mdm_cflow_projection",
    "mdm_banca_projection",
    "mdm_concordato_monthly",
]


def upgrade():
    # 1. Create scenarios table
    op.create_table(
        "mdm_scenarios",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("scenario_slug", sa.String(64), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_default", sa.Boolean, server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_scenarios_case_slug", "mdm_scenarios", ["case_id", "scenario_slug"], unique=True)

    # 2. Add scenario_id to assumptions table
    op.add_column("assumptions",
                  sa.Column("scenario_id", sa.String(64), server_default="base", nullable=False))

    # 3. Add scenario_id to all MDM tables
    for table in MDM_TABLES:
        op.add_column(table,
                      sa.Column("scenario_id", sa.String(64), server_default="base", nullable=False))
        op.create_index(f"ix_{table}_scenario", table, ["case_id", "scenario_id"])


def downgrade():
    for table in reversed(MDM_TABLES):
        op.drop_index(f"ix_{table}_scenario", table_name=table)
        op.drop_column(table, "scenario_id")

    op.drop_column("assumptions", "scenario_id")
    op.drop_table("mdm_scenarios")
