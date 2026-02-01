# app/routers/cases_upload.py
from __future__ import annotations

from typing import Generator, Optional, List, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.core.db import SessionLocal
from app.models.case import Case
from app.models.upload import Upload
from app.services.storage import upload_bytes, signed_url

from ..db.deps import get_db


router = APIRouter(prefix="/cases", tags=["cases"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _resolve_case_id(db: Session, case_id: str) -> Optional[str]:
    case = db.execute(
        select(Case).where((Case.id == case_id) | (Case.slug == case_id)).limit(1)
    ).scalars().first()
    return case.id if case else None


@router.post("/{case_id}/upload-file", summary="Upload file", status_code=status.HTTP_201_CREATED)
async def upload_file(case_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)) -> Dict[str, Any]:
    real_id = _resolve_case_id(db, case_id)
    if not real_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    raw = await file.read()
    key = f"cases/{real_id}/raw/{uuid4()}_{file.filename}"
    path = upload_bytes(key, raw, content_type=file.content_type)

    up = Upload(
        case_id=real_id,
        object_path=path,
        original_name=file.filename,
        mime_type=file.content_type,
        size_bytes=len(raw),
    )
    db.add(up)
    db.commit()
    db.refresh(up)

    return {
        "upload_id": up.id,
        "case_id": case_id,
        "path": path,
        "signed_url": signed_url(path),
        "db_saved": True,
    }


@router.get("/{case_id}/uploads", summary="List uploads for a case")
def list_uploads(case_id: str, include_signed: bool = False, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    real_id = _resolve_case_id(db, case_id)
    if not real_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    stmt = select(Upload).where(Upload.case_id == real_id).order_by(desc(Upload.created_at))
    rows = db.execute(stmt).scalars().all()

    items: List[Dict[str, Any]] = []
    for r in rows:
        item = {
            "upload_id": r.id,
            "original_name": r.original_name,
            "mime": r.mime_type,
            "size": r.size_bytes,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "path": r.object_path,
        }
        if include_signed:
            item["signed_url"] = signed_url(r.object_path)
        items.append(item)
    return items
    
def _get_case(db: Session, case_id: str) -> Case | None:
    return db.execute(
        select(Case).where((Case.id == case_id) | (Case.slug == case_id)).limit(1)
    ).scalars().first()

def _store_upload(db: Session, case: Case, path: str, f: UploadFile, kind: str, size_bytes: int) -> Upload:
    rec = Upload(
        case_id=case.id,
        object_path=path,
        original_name=f.filename,
        mime_type=f.content_type,
        size_bytes=size_bytes,   
        kind=kind,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.post("/{case_id}/upload-xbrl", status_code=status.HTTP_201_CREATED, summary="Carica XBRL (XML)")
async def upload_xbrl(case_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    case = _get_case(db, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    if file.content_type not in ("application/xml", "text/xml", "application/xbrl+xml", "application/xhtml+xml"):
        raise HTTPException(415, "Expected XBRL/XML file")

    data = await file.read()
    size_bytes = len(data)

    key = f"cases/{case.id}/xbrl/{uuid4()}_{file.filename}"
    upload_bytes(key, data, content_type=file.content_type, upsert=True)
    rec = _store_upload(db, case, key, file, kind="xbrl", size_bytes=size_bytes)
    return {"upload_id": rec.id, "path": key}

@router.post("/{case_id}/upload-tb", status_code=status.HTTP_201_CREATED, summary="Carica bilancio contabile (CSV/XLSX)")
async def upload_tb(case_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    case = _get_case(db, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    if file.content_type not in (
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ):
        raise HTTPException(415, "Expected CSV/XLS(X) trial balance")

    data = await file.read()
    size_bytes = len(data)

    key = f"cases/{case.id}/tb/{uuid4()}_{file.filename}"
    upload_bytes(key, data, content_type=file.content_type, upsert=True)
    rec = _store_upload(db, case, key, file, kind="tb", size_bytes=size_bytes)
    return {"upload_id": rec.id, "path": key}
