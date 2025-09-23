"""uploads.kind + case_snapshots

Revision ID: def1231365ec
Revises: 63cda0798e8c
Create Date: 2025-09-22 14:41:17.631599
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'def1231365ec'
down_revision = '63cda0798e8c'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Aggiungi 'kind' a uploads + indice utile
    with op.batch_alter_table("uploads") as batch:
        batch.add_column(sa.Column("kind", sa.String(), nullable=False, server_default="raw"))
    op.create_index("ix_uploads_case_kind_created", "uploads", ["case_id", "kind", "created_at"])

    # 2) Crea tabella case_snapshots
    op.create_table(
        "case_snapshots",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False, index=True),
        sa.Column("xbrl_upload_id", sa.Integer(), nullable=True),
        sa.Column("tb_upload_id", sa.Integer(), nullable=True),
        sa.Column("canonical", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )


def downgrade():
    # rollback step 2
    op.drop_table("case_snapshots")
    # rollback step 1
    op.drop_index("ix_uploads_case_kind_created", table_name="uploads")
    with op.batch_alter_table("uploads") as batch:
        batch.drop_column("kind")
