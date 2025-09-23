"""uploads.created_at default now()

Revision ID: 10cb19ea9a1e
Revises: def1231365ec
Create Date: 2025-09-22 16:59:25.944725
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10cb19ea9a1e'
down_revision = 'def1231365ec'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE uploads ALTER COLUMN created_at SET DEFAULT NOW();")
    op.execute("UPDATE uploads SET created_at = NOW() WHERE created_at IS NULL;")

def downgrade():
    op.execute("ALTER TABLE uploads ALTER COLUMN created_at DROP DEFAULT;")
