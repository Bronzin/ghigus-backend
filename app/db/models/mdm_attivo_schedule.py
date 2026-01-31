# app/db/models/mdm_attivo_schedule.py
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.db.base_class import Base


class MdmAttivoSchedule(Base):
    """Schedulazione mensile degli incassi per una voce dell'attivo."""
    __tablename__ = "mdm_attivo_schedule"

    id = Column(Integer, primary_key=True)
    attivo_item_id = Column(Integer,
                            ForeignKey("mdm_attivo_items.id", ondelete="CASCADE"),
                            nullable=False, index=True)
    period_index = Column(Integer, nullable=False)   # 0-119
    importo = Column(Numeric(18, 2), nullable=False, default=0)
