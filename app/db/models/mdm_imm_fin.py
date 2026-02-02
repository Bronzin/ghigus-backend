# app/db/models/mdm_imm_fin.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmImmFinMovimento(Base):
    """Movimenti immobilizzazioni finanziarie (acquisizioni/dismissioni)."""
    __tablename__ = "mdm_imm_fin_movimenti"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    label = Column(String(256), nullable=False)
    period_index = Column(Integer, nullable=False)
    tipo = Column(String(32), nullable=False)  # ACQUISIZIONE | DISMISSIONE
    importo = Column(Numeric(18, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
