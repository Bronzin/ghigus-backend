"""MDM: scadenziari debiti tributari + finanziamenti existing

Revision ID: mdm_10_scad_trib
Revises: mdm_09_attivo_fin
Create Date: 2026-01-31
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_10_scad_trib"
down_revision = "mdm_09_attivo_fin"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Scadenziari tributari (header)
    op.create_table(
        "mdm_scadenziario_tributario",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String,
                  sa.ForeignKey("cases.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("scenario_id", sa.String(64), server_default="base", nullable=False),
        sa.Column("ente", sa.String(32), nullable=False),
        sa.Column("descrizione", sa.String(256), nullable=True),
        sa.Column("debito_originario", sa.Numeric(18, 2), server_default="0"),
        sa.Column("num_rate", sa.Integer, server_default="12"),
        sa.Column("tasso_interessi", sa.Numeric(8, 4), server_default="0"),
        sa.Column("sanzioni_totali", sa.Numeric(18, 2), server_default="0"),
        sa.Column("mese_inizio", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )

    # 2. Rate scadenziari tributari
    op.create_table(
        "mdm_scadenziario_tributario_rate",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("scadenziario_id", sa.Integer,
                  sa.ForeignKey("mdm_scadenziario_tributario.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("quota_capitale", sa.Numeric(18, 2), server_default="0"),
        sa.Column("quota_interessi", sa.Numeric(18, 2), server_default="0"),
        sa.Column("quota_sanzioni", sa.Numeric(18, 2), server_default="0"),
        sa.Column("importo_rata", sa.Numeric(18, 2), server_default="0"),
        sa.Column("debito_residuo", sa.Numeric(18, 2), server_default="0"),
    )

    # 3. Finanziamenti: campi per prestiti esistenti
    op.add_column("mdm_nuovo_finanziamento",
                  sa.Column("is_existing", sa.Boolean, server_default="false", nullable=False))
    op.add_column("mdm_nuovo_finanziamento",
                  sa.Column("debito_residuo_iniziale", sa.Numeric(18, 2), nullable=True))
    op.add_column("mdm_nuovo_finanziamento",
                  sa.Column("rate_rimanenti", sa.Integer, nullable=True))


def downgrade():
    op.drop_column("mdm_nuovo_finanziamento", "rate_rimanenti")
    op.drop_column("mdm_nuovo_finanziamento", "debito_residuo_iniziale")
    op.drop_column("mdm_nuovo_finanziamento", "is_existing")
    op.drop_table("mdm_scadenziario_tributario_rate")
    op.drop_table("mdm_scadenziario_tributario")
