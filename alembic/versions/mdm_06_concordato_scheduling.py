"""MDM: concordato scheduling columns

Revision ID: mdm_06_concordato_scheduling
Revises: mdm_05_concordato
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_06_concordato_scheduling"
down_revision = "mdm_05_concordato"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("mdm_concordato_monthly",
                  sa.Column("pagamento_proposto", sa.Numeric(18, 2), server_default="0"))
    op.add_column("mdm_concordato_monthly",
                  sa.Column("rata_pianificata", sa.Numeric(18, 2), server_default="0"))
    op.add_column("mdm_concordato_monthly",
                  sa.Column("pagamento_cumulativo", sa.Numeric(18, 2), server_default="0"))


def downgrade():
    op.drop_column("mdm_concordato_monthly", "pagamento_cumulativo")
    op.drop_column("mdm_concordato_monthly", "rata_pianificata")
    op.drop_column("mdm_concordato_monthly", "pagamento_proposto")
