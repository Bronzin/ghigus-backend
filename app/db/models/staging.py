from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.base_class import Base

# -----------------------
# STAGING (replica Excel)
# -----------------------

class TBEntry(Base):
    __tablename__ = "stg_tb_entries"
    id = Column(Integer, primary_key=True)
    # FK allineata a cases.id (TEXT/slug)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)

    account_code = Column(String(64), index=True, nullable=False)
    account_name = Column(String(256))
    debit = Column(Numeric(18, 2), default=0)
    credit = Column(Numeric(18, 2), default=0)
    amount = Column(Numeric(18, 2), default=0)  # credit - debit
    period_end = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class XbrlFact(Base):
    __tablename__ = "stg_xbrl_facts"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)

    concept = Column(String(256), index=True)     # es: us-gaap:Assets
    context_ref = Column(String(128))             # es: I-2024 / D-2024
    unit = Column(String(64))                     # es: EUR
    decimals = Column(String(16))
    value = Column(Numeric(20, 4), nullable=True)
    instant = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    raw_json = Column(JSONB, nullable=True)       # opzionale (debug)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# -----------------------
# MAPPE (raccordo TB -> SP/CE)
# Nota: case_id è *nullable*.
# - NULL = mappa globale, valida per tutte le pratiche
# - valorizzato = override specifico per quella pratica (se mai servisse)
# -----------------------

class MapSP(Base):
    __tablename__ = "stg_map_sp"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=True)
    imported_code = Column(String(64), index=True, nullable=False)   # conto importato (TB)
    imported_desc = Column(String(256))
    riclass_code = Column(String(64), index=True, nullable=False)    # voce riclassificata SP
    riclass_desc = Column(String(256))


class MapCE(Base):
    __tablename__ = "stg_map_ce"
    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=True)
    imported_code = Column(String(64), index=True, nullable=False)
    imported_desc = Column(String(256))
    riclass_code = Column(String(64), index=True, nullable=False)    # voce riclassificata CE
    riclass_desc = Column(String(256))
