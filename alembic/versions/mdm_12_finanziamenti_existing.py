"""Add is_existing, debito_residuo_iniziale, rate_rimanenti to mdm_nuovo_finanziamento

Revision ID: mdm_12_fin_existing
Revises: mdm_11_lkp_conti
Create Date: 2026-02-02
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_12_fin_existing"
down_revision = "mdm_11_lkp_conti"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("mdm_nuovo_finanziamento",
                  sa.Column("is_existing", sa.Boolean, server_default="0", nullable=False))
    op.add_column("mdm_nuovo_finanziamento",
                  sa.Column("debito_residuo_iniziale", sa.Numeric(18, 2), nullable=True))
    op.add_column("mdm_nuovo_finanziamento",
                  sa.Column("rate_rimanenti", sa.Integer, nullable=True))


def downgrade():
    op.drop_column("mdm_nuovo_finanziamento", "rate_rimanenti")
    op.drop_column("mdm_nuovo_finanziamento", "debito_residuo_iniziale")
    op.drop_column("mdm_nuovo_finanziamento", "is_existing")
