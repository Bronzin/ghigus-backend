"""MDM: attivo schedule + modalita/link, nuovi finanziamenti, PFN

Revision ID: mdm_09_attivo_fin
Revises: mdm_08_riclass_period
Create Date: 2026-01-31
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_09_attivo_fin"
down_revision = "mdm_08_riclass_period"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Attivo: modalita (CONTINUITA/REALIZZO) + link a passivo
    op.add_column("mdm_attivo_items",
                  sa.Column("modalita", sa.String(16), server_default="CONTINUITA", nullable=False))
    op.add_column("mdm_attivo_items",
                  sa.Column("linked_passivo_id", sa.Integer,
                            sa.ForeignKey("mdm_passivo_items.id", ondelete="SET NULL"),
                            nullable=True))

    # 2. Tabella schedulazione incassi attivo (mese per mese)
    op.create_table(
        "mdm_attivo_schedule",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("attivo_item_id", sa.Integer,
                  sa.ForeignKey("mdm_attivo_items.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("importo", sa.Numeric(18, 2), nullable=False, server_default="0"),
    )

    # 3. Nuovi finanziamenti
    op.create_table(
        "mdm_nuovo_finanziamento",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("scenario_id", sa.String(64), server_default="base", nullable=False),
        sa.Column("label", sa.String(256), nullable=False),
        sa.Column("importo_capitale", sa.Numeric(18, 2), nullable=False),
        sa.Column("tasso_annuo", sa.Numeric(8, 4), nullable=False, server_default="3.0"),
        sa.Column("durata_mesi", sa.Integer, nullable=False, server_default="60"),
        sa.Column("mese_erogazione", sa.Integer, nullable=False, server_default="0"),
        sa.Column("tipo_ammortamento", sa.String(16), nullable=False, server_default="FRANCESE"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_mdm_nuovo_fin_case_scenario",
                    "mdm_nuovo_finanziamento", ["case_id", "scenario_id"])

    # 4. Schedule rate finanziamento (calcolato)
    op.create_table(
        "mdm_finanziamento_schedule",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("finanziamento_id", sa.Integer,
                  sa.ForeignKey("mdm_nuovo_finanziamento.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("period_index", sa.Integer, nullable=False),
        sa.Column("quota_capitale", sa.Numeric(18, 2), server_default="0"),
        sa.Column("quota_interessi", sa.Numeric(18, 2), server_default="0"),
        sa.Column("rata", sa.Numeric(18, 2), server_default="0"),
        sa.Column("debito_residuo", sa.Numeric(18, 2), server_default="0"),
    )


def downgrade():
    op.drop_table("mdm_finanziamento_schedule")
    op.drop_table("mdm_nuovo_finanziamento")
    op.drop_table("mdm_attivo_schedule")
    op.drop_column("mdm_attivo_items", "linked_passivo_id")
    op.drop_column("mdm_attivo_items", "modalita")
