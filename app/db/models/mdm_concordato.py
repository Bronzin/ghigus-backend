# app/db/models/mdm_concordato.py
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.base_class import Base


class MdmConcordatoMonthly(Base):
    __tablename__ = "mdm_concordato_monthly"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    scenario_id = Column(String(64), nullable=False, default="base", server_default="base")
    period_index = Column(Integer, nullable=False)
    creditor_class = Column(String(64), nullable=False)  # PREDEDUZIONE, IPOTECARIO, PRIVILEGIATO, CHIROGRAFARIO
    debito_iniziale = Column(Numeric(18, 2), default=0)
    pagamento_proposto = Column(Numeric(18, 2), default=0)   # importo totale proposto per questa classe
    rata_pianificata = Column(Numeric(18, 2), default=0)      # rata mensile da schedule
    pagamento = Column(Numeric(18, 2), default=0)             # pagamento effettivo (può differire se cassa insufficiente)
    pagamento_cumulativo = Column(Numeric(18, 2), default=0)  # pagato cumulativo dall'inizio
    debito_residuo = Column(Numeric(18, 2), default=0)
    pct_soddisfazione = Column(Numeric(8, 4), default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
