# app/db/models/mdm_scenario.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from datetime import datetime
from app.db.base_class import Base


class MdmScenario(Base):
    __tablename__ = "mdm_scenarios"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_slug = Column(String(64), nullable=False)       # "base", "ottimistico", "pessimistico"
    name = Column(String(256), nullable=False)                # "Scenario Base"
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
