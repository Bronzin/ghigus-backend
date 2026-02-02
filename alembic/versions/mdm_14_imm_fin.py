"""Create mdm_imm_fin_movimenti table.

Revision ID: mdm_14_imm_fin
Revises: mdm_13_sched_existing
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_14_imm_fin"
down_revision = "mdm_13_sched_existing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mdm_imm_fin_movimenti",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario_id", sa.String(64), nullable=False, server_default="base"),
        sa.Column("label", sa.String(256), nullable=False),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("tipo", sa.String(32), nullable=False),
        sa.Column("importo", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_mdm_imm_fin_movimenti_case_id", "mdm_imm_fin_movimenti", ["case_id"])
    op.create_index("ix_mdm_imm_fin_movimenti_case_scenario", "mdm_imm_fin_movimenti", ["case_id", "scenario_id"])


def downgrade() -> None:
    op.drop_index("ix_mdm_imm_fin_movimenti_case_scenario", "mdm_imm_fin_movimenti")
    op.drop_index("ix_mdm_imm_fin_movimenti_case_id", "mdm_imm_fin_movimenti")
    op.drop_table("mdm_imm_fin_movimenti")
