# app/routers/debug.py
import re
from uuid import uuid4
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.storage import upload_file, signed_url
from app.core.config import settings
from app.core.supabase_client import get_supabase

router = APIRouter(prefix="/debug", tags=["debug"])
log = logging.getLogger("uvicorn.error")
SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")

def sanitize_filename(name: str) -> str:
    base = name.split("/")[-1].split("\\")[-1]
    return SAFE_CHARS.sub("_", base) or "file"

@router.post("/upload")
async def debug_upload(file: UploadFile = File(...)):
    try:
        MAX_SIZE = 50 * 1024 * 1024  # 50MB piano Free
        ALLOWED = {"xbrl", "xml", "csv", "zip", "docx", "pdf"}

        if not file.filename:
            raise HTTPException(400, "File senza nome.")
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED:
            raise HTTPException(400, f"Estensione non consentita: .{ext}")

        data = await file.read()
        if len(data) > MAX_SIZE:
            raise HTTPException(413, "File troppo grande (max 50MB).")

        safe = sanitize_filename(file.filename)
        path = f"cases/debug/raw/{uuid4()}_{safe}"

        upload_file(path, data, content_type=file.content_type or "application/octet-stream", upsert=True)
        url = signed_url(path, expires_in=3600)
        return {"path": path, "signed_url": url}

    except HTTPException:
        raise
    except Exception as e:
        log.exception("debug_upload failed")
        # Mostriamo il motivo in Swagger per debug
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/selfcheck")
def selfcheck():
    """Verifica rapida di client/bucket."""
    sb = get_supabase()
    res = sb.storage.from_(settings.storage_bucket).list(path="")
    return {
        "supabase_url_ok": bool(settings.supabase_url),
        "bucket": settings.storage_bucket,
        "list_ok": isinstance(res, list),
        "items_found": len(res) if isinstance(res, list) else None,
    }
