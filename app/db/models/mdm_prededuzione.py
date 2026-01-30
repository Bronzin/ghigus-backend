# app/db/models/mdm_prededuzione.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmPrededuzioneMonthly(Base):
    __tablename__ = "mdm_prededuzione_monthly"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    voce_type = Column(String(64), nullable=False)   # COMPENSO_CURATORE, COMPENSO_ATTESTATORE, etc.
    voce_code = Column(String(128), nullable=False)
    importo_totale = Column(Numeric(18, 2), default=0)
    period_index = Column(Integer, nullable=False)    # 0-119
    importo_periodo = Column(Numeric(18, 2), default=0)
    debito_residuo = Column(Numeric(18, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
