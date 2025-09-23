from sqlalchemy.exc import SQLAlchemyError
from app.core.db import SessionLocal
from app.db.models import Upload

s = SessionLocal()
try:
    r = Upload(
        case_id="probe",
        object_path="foo/bar.txt",
        original_name="bar.txt",
        mime_type="text/plain",
        size_bytes=1,
    )
    s.add(r)
    s.commit()
    s.refresh(r)
    print("OK upload_id:", r.id, "created_at:", r.created_at)
except SQLAlchemyError as e:
    print("TYPE:", type(e).__name__)
    print("ORIG:", type(e.orig).__name__ if getattr(e, "orig", None) else None)
    print("DETAIL:", str(e.orig) if getattr(e, "orig", None) else str(e))
    s.rollback()
finally:
    s.close()
