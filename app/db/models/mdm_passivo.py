# app/db/models/mdm_passivo.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmPassivoItem(Base):
    __tablename__ = "mdm_passivo_items"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    category = Column(String(128), nullable=False, index=True)
    item_label = Column(String(256), nullable=True)

    saldo_contabile = Column(Numeric(18, 2), default=0)
    incrementi = Column(Numeric(18, 2), default=0)
    decrementi = Column(Numeric(18, 2), default=0)
    compensato = Column(Numeric(18, 2), default=0)
    fondo_rischi = Column(Numeric(18, 2), default=0)
    sanzioni_accessori = Column(Numeric(18, 2), default=0)
    interessi = Column(Numeric(18, 2), default=0)

    # Campi calcolati
    totale_rettifiche = Column(Numeric(18, 2), default=0)
    passivo_rettificato = Column(Numeric(18, 2), default=0)

    # Classificazione creditore
    tipologia_creditore = Column(String(64), nullable=True)  # PREDEDUZIONE, IPOTECARIO, PRIVILEGIATO, CHIROGRAFARIO
    classe_creditore = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MdmPassivoTipologia(Base):
    __tablename__ = "mdm_passivo_tipologie"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    sezione = Column(String(32), nullable=False)  # NON_ADERENTE, ADERENTE
    slot_order = Column(Integer, nullable=False)
    classe = Column(String(64), nullable=False)
    specifica = Column(String(256), nullable=True)
    codice_ordinamento = Column(String(32), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
