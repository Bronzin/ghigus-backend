# app/db/models/mdm_scadenziario_tributario.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.db.base_class import Base


class MdmScadenziarioTributario(Base):
    __tablename__ = "mdm_scadenziario_tributario"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    ente = Column(String(32), nullable=False)            # "ADE" | "INPS" | "ALTRO"
    descrizione = Column(String(256), nullable=True)     # es. "Rateizzazione IVA 2022"
    debito_originario = Column(Numeric(18, 2), default=0)
    num_rate = Column(Integer, default=12)
    tasso_interessi = Column(Numeric(8, 4), default=0)   # annuo
    sanzioni_totali = Column(Numeric(18, 2), default=0)
    mese_inizio = Column(Integer, default=0)             # period_index (0-119)
    is_existing = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MdmScadenziarioTributarioRate(Base):
    __tablename__ = "mdm_scadenziario_tributario_rate"

    id = Column(Integer, primary_key=True)
    scadenziario_id = Column(Integer,
                             ForeignKey("mdm_scadenziario_tributario.id", ondelete="CASCADE"),
                             nullable=False, index=True)
    period_index = Column(Integer, nullable=False)
    quota_capitale = Column(Numeric(18, 2), default=0)
    quota_interessi = Column(Numeric(18, 2), default=0)
    quota_sanzioni = Column(Numeric(18, 2), default=0)
    importo_rata = Column(Numeric(18, 2), default=0)
    debito_residuo = Column(Numeric(18, 2), default=0)
