"""MDM: prededuzione, affitto, cessione monthly

Revision ID: mdm_03_auxiliary
Revises: mdm_02_scenari
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_03_auxiliary"
down_revision = "mdm_02_scenari"
branch_labels = None
depends_on = None


def upgrade():
    # ── mdm_prededuzione_monthly ──
    op.create_table(
        "mdm_prededuzione_monthly",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("voce_type", sa.String(64), nullable=False),
        sa.Column("voce_code", sa.String(128), nullable=False),
        sa.Column("importo_totale", sa.Numeric(18, 2), server_default="0"),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("importo_periodo", sa.Numeric(18, 2), server_default="0"),
        sa.Column("debito_residuo", sa.Numeric(18, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_preded_case_period", "mdm_prededuzione_monthly", ["case_id", "period_index"])

    # ── mdm_affitto_monthly ──
    op.create_table(
        "mdm_affitto_monthly",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("canone", sa.Numeric(18, 2), server_default="0"),
        sa.Column("iva", sa.Numeric(18, 2), server_default="0"),
        sa.Column("totale", sa.Numeric(18, 2), server_default="0"),
        sa.Column("incasso", sa.Numeric(18, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_affitto_case_period", "mdm_affitto_monthly", ["case_id", "period_index"])

    # ── mdm_cessione_monthly ──
    op.create_table(
        "mdm_cessione_monthly",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("component", sa.String(64), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_cessione_case_period", "mdm_cessione_monthly", ["case_id", "period_index"])


def downgrade():
    op.drop_table("mdm_cessione_monthly")
    op.drop_table("mdm_affitto_monthly")
    op.drop_table("mdm_prededuzione_monthly")
