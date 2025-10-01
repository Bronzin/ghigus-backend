"""US-03: staging & riclass tables (safe, case_id TEXT FK, no drops)

Revision ID: 4177385be080
Revises: 10cb19ea9a1e
Create Date: 2025-09-23 17:45:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "4177385be080"
down_revision = "10cb19ea9a1e"
branch_labels = None
depends_on = None


def upgrade():
    # -----------------------
    # STAGING
    # -----------------------
    op.create_table(
        "stg_tb_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("account_code", sa.String(length=64), nullable=False),
        sa.Column("account_name", sa.String(length=256), nullable=True),
        sa.Column("debit", sa.Numeric(18, 2), nullable=True),
        sa.Column("credit", sa.Numeric(18, 2), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "stg_xbrl_facts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("concept", sa.String(length=256), nullable=True),
        sa.Column("context_ref", sa.String(length=128), nullable=True),
        sa.Column("unit", sa.String(length=64), nullable=True),
        sa.Column("decimals", sa.String(length=16), nullable=True),
        sa.Column("value", sa.Numeric(20, 4), nullable=True),
        sa.Column("instant", sa.Date(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("raw_json", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "stg_map_sp",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("imported_code", sa.String(length=64), nullable=False),
        sa.Column("imported_desc", sa.String(length=256), nullable=True),
        sa.Column("riclass_code", sa.String(length=64), nullable=False),
        sa.Column("riclass_desc", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "stg_map_ce",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("imported_code", sa.String(length=64), nullable=False),
        sa.Column("imported_desc", sa.String(length=256), nullable=True),
        sa.Column("riclass_code", sa.String(length=64), nullable=False),
        sa.Column("riclass_desc", sa.String(length=256), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )

    # -----------------------
    # FINALI
    # -----------------------
    op.create_table(
        "fin_sp_riclass",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("riclass_code", sa.String(length=64), nullable=False),
        sa.Column("riclass_desc", sa.String(length=256), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "fin_ce_riclass",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("riclass_code", sa.String(length=64), nullable=False),
        sa.Column("riclass_desc", sa.String(length=256), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "fin_kpi_standard",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
    )

    # NB: NON tocchiamo tabelle preesistenti (companies, cases, uploads, ecc.)
    # Nessun DROP QUI.
    return


def downgrade():
    # Drop in ordine inverso
    op.drop_table("fin_kpi_standard")
    op.drop_table("fin_ce_riclass")
    op.drop_table("fin_sp_riclass")
    op.drop_table("stg_map_ce")
    op.drop_table("stg_map_sp")
    op.drop_table("stg_xbrl_facts")
    op.drop_table("stg_tb_entries")
    return
