from alembic import op
import sqlalchemy as sa

# Identificatori della migration
revision = "63cda0798e8c"          # deve essere una STRINGA
down_revision = "cb63aebdafcd"     # ID della migration precedente, STRINGA
branch_labels = None
depends_on = None

def upgrade():
    # 1) aggiungi colonna come nullable (compatibile con righe esistenti)
    op.add_column("uploads", sa.Column("object_path", sa.String(length=1024), nullable=True))
    # 2) valorizza eventuali NULL per evitare violazioni NOT NULL
    op.execute("update uploads set object_path = 'migrated' where object_path is null;")
    # 3) rendi NOT NULL
    op.alter_column("uploads", "object_path", existing_type=sa.String(length=1024), nullable=False)

def downgrade():
    op.drop_column("uploads", "object_path")
