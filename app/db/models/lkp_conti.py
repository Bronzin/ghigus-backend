# app/db/models/lkp_conti.py
"""Lookup tables for standard chart of accounts (Piano dei Conti) used in reclassification."""

from sqlalchemy import Column, String
from app.db.base_class import Base


class LkpContoSP(Base):
    """Stato Patrimoniale (Balance Sheet) standard account."""
    __tablename__ = "lkp_conti_sp"

    code = Column(String(256), primary_key=True)
    description = Column(String(512), nullable=False)
    category = Column(String(128), nullable=False, index=True)


class LkpContoCE(Base):
    """Conto Economico (Income Statement) standard account."""
    __tablename__ = "lkp_conti_ce"

    code = Column(String(256), primary_key=True)
    description = Column(String(512), nullable=False)
    category = Column(String(128), nullable=False, index=True)
