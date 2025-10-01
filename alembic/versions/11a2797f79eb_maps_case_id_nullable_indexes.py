"""maps: case_id nullable + indexes

Revision ID: maps_caseid_nullable
Revises: 4177385be080
Create Date: 2025-09-24
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "maps_caseid_nullable"
down_revision = "4177385be080"
branch_labels = None
depends_on = None


def upgrade():
    # Rendi case_id nullable (SP/CE)
    op.alter_column("stg_map_sp", "case_id", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("stg_map_ce", "case_id", existing_type=sa.VARCHAR(), nullable=True)

    # Indici utili (non-unique)
    op.create_index("ix_stg_map_sp_case_code", "stg_map_sp", ["case_id", "imported_code"], unique=False)
    op.create_index("ix_stg_map_ce_case_code", "stg_map_ce", ["case_id", "imported_code"], unique=False)

    # Indici parziali per lookup globale (Postgres)
    op.execute("CREATE INDEX IF NOT EXISTS ix_stg_map_sp_imported_code_global ON stg_map_sp (imported_code) WHERE case_id IS NULL;")
    op.execute("CREATE INDEX IF NOT EXISTS ix_stg_map_ce_imported_code_global ON stg_map_ce (imported_code) WHERE case_id IS NULL;")


def downgrade():
    # Drop indici
    op.execute("DROP INDEX IF EXISTS ix_stg_map_sp_imported_code_global;")
    op.execute("DROP INDEX IF EXISTS ix_stg_map_ce_imported_code_global;")
    op.drop_index("ix_stg_map_sp_case_code", table_name="stg_map_sp")
    op.drop_index("ix_stg_map_ce_case_code", table_name="stg_map_ce")

    # Torna NOT NULL (attenzione: fallisce se esistono righe con NULL)
    op.alter_column("stg_map_sp", "case_id", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("stg_map_ce", "case_id", existing_type=sa.VARCHAR(), nullable=False)
