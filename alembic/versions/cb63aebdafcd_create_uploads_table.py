from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "cb63aebdafcd"       # <-- lascia il tuo valore
down_revision = "202404091200"  # <-- lascia il tuo valore
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "uploads",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.String(length=64), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_uploads_case_id", "uploads", ["case_id"])

def downgrade():
    op.drop_index("ix_uploads_case_id", table_name="uploads")
    op.drop_table("uploads")
