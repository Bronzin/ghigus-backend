# app/db/models/mdm_cessione.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmCessioneMonthly(Base):
    __tablename__ = "mdm_cessione_monthly"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    period_index = Column(Integer, nullable=False)    # 0-119
    component = Column(String(64), nullable=False)    # LORDO, ACCOLLO_TFR, ACCOLLO_DEBITI, NETTO
    amount = Column(Numeric(18, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
