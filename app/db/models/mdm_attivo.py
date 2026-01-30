# app/db/models/mdm_attivo.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text
from datetime import datetime
from app.db.base_class import Base


class MdmAttivoItem(Base):
    __tablename__ = "mdm_attivo_items"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    category = Column(String(128), nullable=False, index=True)
    item_label = Column(String(256), nullable=True)

    saldo_contabile = Column(Numeric(18, 2), default=0)
    cessioni = Column(Numeric(18, 2), default=0)
    compensazioni = Column(Numeric(18, 2), default=0)
    rettifiche_economiche = Column(Numeric(18, 2), default=0)
    rettifica_patrimoniale = Column(Numeric(18, 2), default=0)
    fondo_svalutazione = Column(Numeric(18, 2), default=0)
    pct_svalutazione = Column(Numeric(8, 4), default=0)

    # Campi calcolati
    totale_rettifiche = Column(Numeric(18, 2), default=0)
    attivo_rettificato = Column(Numeric(18, 2), default=0)
    continuita_realizzo = Column(Numeric(18, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
