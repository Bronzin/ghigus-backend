from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
from app.db.base_class import Base

class Case(Base):
    __tablename__ = "cases"

    # In Supabase: id TEXT (slug della pratica)
    id = Column(String, primary_key=True)

    # Campi presenti nello schema esistente (nullable ok)
    company_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    slug = Column(String, nullable=True)
    status = Column(String, nullable=True)
