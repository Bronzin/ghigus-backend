"""MDM: concordato monthly

Revision ID: mdm_05_concordato
Revises: mdm_04_projections
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_05_concordato"
down_revision = "mdm_04_projections"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mdm_concordato_monthly",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("creditor_class", sa.String(64), nullable=False),
        sa.Column("debito_iniziale", sa.Numeric(18, 2), server_default="0"),
        sa.Column("pagamento", sa.Numeric(18, 2), server_default="0"),
        sa.Column("debito_residuo", sa.Numeric(18, 2), server_default="0"),
        sa.Column("pct_soddisfazione", sa.Numeric(8, 4), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_conc_case_period", "mdm_concordato_monthly", ["case_id", "period_index"])
    op.create_index("ix_mdm_conc_case_class", "mdm_concordato_monthly", ["case_id", "creditor_class"])


def downgrade():
    op.drop_table("mdm_concordato_monthly")
