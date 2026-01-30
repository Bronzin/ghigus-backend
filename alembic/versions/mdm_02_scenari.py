"""MDM: liquidazione e test perseguibilita

Revision ID: mdm_02_scenari
Revises: mdm_01_attivo
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_02_scenari"
down_revision = "mdm_01_attivo"
branch_labels = None
depends_on = None


def upgrade():
    # ── mdm_liquidazione ──
    op.create_table(
        "mdm_liquidazione",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("section", sa.String(64), nullable=False),
        sa.Column("line_code", sa.String(128), nullable=False),
        sa.Column("line_label", sa.String(256), nullable=True),
        sa.Column("importo_totale", sa.Numeric(18, 2), server_default="0"),
        sa.Column("importo_massa_1", sa.Numeric(18, 2), server_default="0"),
        sa.Column("importo_massa_2", sa.Numeric(18, 2), server_default="0"),
        sa.Column("importo_massa_3", sa.Numeric(18, 2), server_default="0"),
        sa.Column("pct_soddisfazione", sa.Numeric(8, 4), server_default="0"),
        sa.Column("credito_residuo", sa.Numeric(18, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )

    # ── mdm_test_piat ──
    op.create_table(
        "mdm_test_piat",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("section", sa.String(8), nullable=False),
        sa.Column("line_code", sa.String(128), nullable=False),
        sa.Column("line_label", sa.String(256), nullable=True),
        sa.Column("sign", sa.Integer, server_default="1"),
        sa.Column("amount", sa.Numeric(18, 2), server_default="0"),
        sa.Column("total_a", sa.Numeric(18, 2), server_default="0"),
        sa.Column("total_b", sa.Numeric(18, 2), server_default="0"),
        sa.Column("ratio_ab", sa.Numeric(12, 6), server_default="0"),
        sa.Column("interpretation", sa.String(256), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )


def downgrade():
    op.drop_table("mdm_test_piat")
    op.drop_table("mdm_liquidazione")
