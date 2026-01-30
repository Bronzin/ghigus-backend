# app/db/models/mdm_projections.py
"""Modelli per le proiezioni mensili: CE, SP, Cash Flow, Banca."""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmCeProjection(Base):
    __tablename__ = "mdm_ce_projection"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    period_index = Column(Integer, nullable=False)
    line_code = Column(String(128), nullable=False)
    line_label = Column(String(256), nullable=True)
    section = Column(String(64), nullable=True)
    amount = Column(Numeric(18, 2), default=0)
    is_subtotal = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MdmSpProjection(Base):
    __tablename__ = "mdm_sp_projection"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    period_index = Column(Integer, nullable=False)
    line_code = Column(String(128), nullable=False)
    line_label = Column(String(256), nullable=True)
    section = Column(String(64), nullable=True)
    amount = Column(Numeric(18, 2), default=0)
    is_subtotal = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MdmCflowProjection(Base):
    __tablename__ = "mdm_cflow_projection"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    period_index = Column(Integer, nullable=False)
    line_code = Column(String(128), nullable=False)
    line_label = Column(String(256), nullable=True)
    section = Column(String(64), nullable=True)  # GESTIONE_REDDITUALE, INVESTIMENTO, FINANZIAMENTO
    amount = Column(Numeric(18, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MdmBancaProjection(Base):
    __tablename__ = "mdm_banca_projection"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    period_index = Column(Integer, nullable=False)
    line_code = Column(String(128), nullable=False)
    line_label = Column(String(256), nullable=True)
    section = Column(String(64), nullable=True)  # ENTRATE, USCITE, SALDI
    amount = Column(Numeric(18, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
