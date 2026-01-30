# app/db/models/mdm_liquidazione.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmLiquidazione(Base):
    __tablename__ = "mdm_liquidazione"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    section = Column(String(64), nullable=False)  # REALIZZO_ATTIVO, PREDEDUZIONI, IPOTECARI, PRIVILEGIATI, CHIROGRAFARI
    line_code = Column(String(128), nullable=False)
    line_label = Column(String(256), nullable=True)

    importo_totale = Column(Numeric(18, 2), default=0)
    importo_massa_1 = Column(Numeric(18, 2), default=0)
    importo_massa_2 = Column(Numeric(18, 2), default=0)
    importo_massa_3 = Column(Numeric(18, 2), default=0)
    pct_soddisfazione = Column(Numeric(8, 4), default=0)
    credito_residuo = Column(Numeric(18, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MdmTestPiat(Base):
    __tablename__ = "mdm_test_piat"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    section = Column(String(8), nullable=False)  # A, B
    line_code = Column(String(128), nullable=False)
    line_label = Column(String(256), nullable=True)
    sign = Column(Integer, default=1)  # +1 or -1
    amount = Column(Numeric(18, 2), default=0)

    # Totali e risultato
    total_a = Column(Numeric(18, 2), default=0)
    total_b = Column(Numeric(18, 2), default=0)
    ratio_ab = Column(Numeric(12, 6), default=0)
    interpretation = Column(String(256), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
