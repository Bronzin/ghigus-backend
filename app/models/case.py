from sqlalchemy import Column, String, Text
from app.db.base_class import Base

class Case(Base):
    __tablename__ = "cases"
    id = Column(String, primary_key=True)                # string/uuid
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    company_id = Column(String, nullable=False)          # string
    description = Column(Text)
    status = Column(String, nullable=False, default="created")
