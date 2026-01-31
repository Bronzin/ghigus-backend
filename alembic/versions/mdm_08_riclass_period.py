"""MDM: add period column to fin_sp_riclass, fin_ce_riclass, fin_kpi_standard

Revision ID: mdm_08_riclass_period
Revises: mdm_07_multi_scenario
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_08_riclass_period"
down_revision = "mdm_07_multi_scenario"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("fin_sp_riclass",
                  sa.Column("period", sa.String(16), nullable=True))
    op.create_index("ix_fin_sp_riclass_period", "fin_sp_riclass", ["period"])

    op.add_column("fin_ce_riclass",
                  sa.Column("period", sa.String(16), nullable=True))
    op.create_index("ix_fin_ce_riclass_period", "fin_ce_riclass", ["period"])

    op.add_column("fin_kpi_standard",
                  sa.Column("period", sa.String(16), nullable=True))
    op.create_index("ix_fin_kpi_standard_period", "fin_kpi_standard", ["period"])


def downgrade():
    op.drop_index("ix_fin_kpi_standard_period", table_name="fin_kpi_standard")
    op.drop_column("fin_kpi_standard", "period")

    op.drop_index("ix_fin_ce_riclass_period", table_name="fin_ce_riclass")
    op.drop_column("fin_ce_riclass", "period")

    op.drop_index("ix_fin_sp_riclass_period", table_name="fin_sp_riclass")
    op.drop_column("fin_sp_riclass", "period")
