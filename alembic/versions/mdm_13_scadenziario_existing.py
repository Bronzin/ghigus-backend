"""Add is_existing to mdm_scadenziario_tributario

Revision ID: mdm_13_sched_existing
Revises: mdm_12_fin_existing
Create Date: 2026-02-02
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_13_sched_existing"
down_revision = "mdm_12_fin_existing"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("mdm_scadenziario_tributario",
                  sa.Column("is_existing", sa.Boolean, server_default="0", nullable=False))


def downgrade():
    op.drop_column("mdm_scadenziario_tributario", "is_existing")
