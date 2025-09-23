from sqlalchemy import Column, Integer, String, DateTime, text
from app.db.base_class import Base

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, index=True, nullable=False)
    object_path = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=False)  # se il DB è NOT NULL, meglio nullable=False
    kind = Column(String, nullable=False, default="raw")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
