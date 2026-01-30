"""MDM: proiezioni CE, SP, CFlow, Banca

Revision ID: mdm_04_projections
Revises: mdm_03_auxiliary
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_04_projections"
down_revision = "mdm_03_auxiliary"
branch_labels = None
depends_on = None


def upgrade():
    # ── mdm_ce_projection ──
    op.create_table(
        "mdm_ce_projection",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("line_code", sa.String(128), nullable=False),
        sa.Column("line_label", sa.String(256), nullable=True),
        sa.Column("section", sa.String(64), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("is_subtotal", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_ce_case_period", "mdm_ce_projection", ["case_id", "period_index"])
    op.create_index("ix_mdm_ce_case_line", "mdm_ce_projection", ["case_id", "line_code"])

    # ── mdm_sp_projection ──
    op.create_table(
        "mdm_sp_projection",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("line_code", sa.String(128), nullable=False),
        sa.Column("line_label", sa.String(256), nullable=True),
        sa.Column("section", sa.String(64), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("is_subtotal", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_sp_case_period", "mdm_sp_projection", ["case_id", "period_index"])
    op.create_index("ix_mdm_sp_case_line", "mdm_sp_projection", ["case_id", "line_code"])

    # ── mdm_cflow_projection ──
    op.create_table(
        "mdm_cflow_projection",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("line_code", sa.String(128), nullable=False),
        sa.Column("line_label", sa.String(256), nullable=True),
        sa.Column("section", sa.String(64), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_cflow_case_period", "mdm_cflow_projection", ["case_id", "period_index"])

    # ── mdm_banca_projection ──
    op.create_table(
        "mdm_banca_projection",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("line_code", sa.String(128), nullable=False),
        sa.Column("line_label", sa.String(256), nullable=True),
        sa.Column("section", sa.String(64), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_banca_case_period", "mdm_banca_projection", ["case_id", "period_index"])


def downgrade():
    op.drop_table("mdm_banca_projection")
    op.drop_table("mdm_cflow_projection")
    op.drop_table("mdm_sp_projection")
    op.drop_table("mdm_ce_projection")
