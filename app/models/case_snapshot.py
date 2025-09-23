from sqlalchemy import Column, String, Integer, DateTime, JSON, text
from app.db.base_class import Base

class CaseSnapshot(Base):
    __tablename__ = "case_snapshots"  # <-- se in DB è 'case_snapshot', metti esattamente: "case_snapshot"

    id = Column(String, primary_key=True)   # uuid as str
    case_id = Column(String, index=True, nullable=False)
    xbrl_upload_id = Column(Integer, nullable=True)
    tb_upload_id = Column(Integer, nullable=True)
    canonical = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
