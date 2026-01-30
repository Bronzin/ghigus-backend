# app/db/models/mdm_affitto.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmAffittoMonthly(Base):
    __tablename__ = "mdm_affitto_monthly"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    period_index = Column(Integer, nullable=False)    # 0-119
    canone = Column(Numeric(18, 2), default=0)
    iva = Column(Numeric(18, 2), default=0)
    totale = Column(Numeric(18, 2), default=0)
    incasso = Column(Numeric(18, 2), default=0)       # con dilazione

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
