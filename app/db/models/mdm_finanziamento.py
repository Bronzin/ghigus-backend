# app/db/models/mdm_finanziamento.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmNuovoFinanziamento(Base):
    """Nuovo finanziamento con piano di ammortamento."""
    __tablename__ = "mdm_nuovo_finanziamento"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    label = Column(String(256), nullable=False)
    importo_capitale = Column(Numeric(18, 2), nullable=False)
    tasso_annuo = Column(Numeric(8, 4), nullable=False, default=3.0)
    durata_mesi = Column(Integer, nullable=False, default=60)
    mese_erogazione = Column(Integer, nullable=False, default=0)  # period_index
    tipo_ammortamento = Column(String(16), nullable=False, default="FRANCESE")  # FRANCESE|ITALIANO|BULLET
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MdmFinanziamentoSchedule(Base):
    """Singola rata del piano di ammortamento."""
    __tablename__ = "mdm_finanziamento_schedule"

    id = Column(Integer, primary_key=True)
    finanziamento_id = Column(Integer,
                              ForeignKey("mdm_nuovo_finanziamento.id", ondelete="CASCADE"),
                              nullable=False, index=True)
    period_index = Column(Integer, nullable=False)
    quota_capitale = Column(Numeric(18, 2), default=0)
    quota_interessi = Column(Numeric(18, 2), default=0)
    rata = Column(Numeric(18, 2), default=0)
    debito_residuo = Column(Numeric(18, 2), default=0)
