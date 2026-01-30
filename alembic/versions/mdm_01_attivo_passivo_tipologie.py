"""MDM: attivo, passivo, tipologie creditore

Revision ID: mdm_01_attivo
Revises: maps_caseid_nullable
Create Date: 2026-01-30
"""
from alembic import op
import sqlalchemy as sa

revision = "mdm_01_attivo"
down_revision = "maps_caseid_nullable"
branch_labels = None
depends_on = None


def upgrade():
    # ── mdm_attivo_items ──
    op.create_table(
        "mdm_attivo_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("category", sa.String(128), nullable=False, index=True),
        sa.Column("item_label", sa.String(256), nullable=True),
        sa.Column("saldo_contabile", sa.Numeric(18, 2), server_default="0"),
        sa.Column("cessioni", sa.Numeric(18, 2), server_default="0"),
        sa.Column("compensazioni", sa.Numeric(18, 2), server_default="0"),
        sa.Column("rettifiche_economiche", sa.Numeric(18, 2), server_default="0"),
        sa.Column("rettifica_patrimoniale", sa.Numeric(18, 2), server_default="0"),
        sa.Column("fondo_svalutazione", sa.Numeric(18, 2), server_default="0"),
        sa.Column("pct_svalutazione", sa.Numeric(8, 4), server_default="0"),
        sa.Column("totale_rettifiche", sa.Numeric(18, 2), server_default="0"),
        sa.Column("attivo_rettificato", sa.Numeric(18, 2), server_default="0"),
        sa.Column("continuita_realizzo", sa.Numeric(18, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )

    # ── mdm_passivo_items ──
    op.create_table(
        "mdm_passivo_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("category", sa.String(128), nullable=False, index=True),
        sa.Column("item_label", sa.String(256), nullable=True),
        sa.Column("saldo_contabile", sa.Numeric(18, 2), server_default="0"),
        sa.Column("incrementi", sa.Numeric(18, 2), server_default="0"),
        sa.Column("decrementi", sa.Numeric(18, 2), server_default="0"),
        sa.Column("compensato", sa.Numeric(18, 2), server_default="0"),
        sa.Column("fondo_rischi", sa.Numeric(18, 2), server_default="0"),
        sa.Column("sanzioni_accessori", sa.Numeric(18, 2), server_default="0"),
        sa.Column("interessi", sa.Numeric(18, 2), server_default="0"),
        sa.Column("totale_rettifiche", sa.Numeric(18, 2), server_default="0"),
        sa.Column("passivo_rettificato", sa.Numeric(18, 2), server_default="0"),
        sa.Column("tipologia_creditore", sa.String(64), nullable=True),
        sa.Column("classe_creditore", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )

    # ── mdm_passivo_tipologie ──
    op.create_table(
        "mdm_passivo_tipologie",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("case_id", sa.String, sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sezione", sa.String(32), nullable=False),
        sa.Column("slot_order", sa.Integer, nullable=False),
        sa.Column("classe", sa.String(64), nullable=False),
        sa.Column("specifica", sa.String(256), nullable=True),
        sa.Column("codice_ordinamento", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()"), nullable=False),
    )


def downgrade():
    op.drop_table("mdm_passivo_tipologie")
    op.drop_table("mdm_passivo_items")
    op.drop_table("mdm_attivo_items")
