from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base

# -----------------------
# FINALI (riclassificati)
# -----------------------

class SpRiclass(Base):
    __tablename__ = "fin_sp_riclass"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    riclass_code = Column(String(64), index=True, nullable=False)
    riclass_desc = Column(String(256))
    amount = Column(Numeric(18, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CeRiclass(Base):
    __tablename__ = "fin_ce_riclass"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    riclass_code = Column(String(64), index=True, nullable=False)
    riclass_desc = Column(String(256))
    amount = Column(Numeric(18, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class KpiStandard(Base):
    __tablename__ = "fin_kpi_standard"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(128), index=True, nullable=False)  # es: Leverage, EBITDA Margin
    value = Column(Numeric(18, 4), nullable=False)
    unit = Column(String(16), nullable=True)                # %, x, EUR
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
