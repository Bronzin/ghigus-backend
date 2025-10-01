from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import os, time, re, mimetypes

from app.db.session import get_db
from app.services.loaders import STORAGE_ROOT  # stesso root usato dal processing

router = APIRouter(tags=["uploads"])

def _case_exists(db: Session, slug: str) -> bool:
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    return bool(row)

def _safe_name(name: str) -> str:
    name = os.path.basename(name or "file")
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name[:200]

def _save_file(slug: str, up: UploadFile) -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{ts}_{_safe_name(up.filename or 'upload')}"
    rel_dir = os.path.join(slug)
    abs_dir = os.path.abspath(os.path.join(STORAGE_ROOT, rel_dir))
    os.makedirs(abs_dir, exist_ok=True)
    abs_path = os.path.join(abs_dir, fname)
    with open(abs_path, "wb") as f:
        while True:
            chunk = up.file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    rel_path = os.path.join(rel_dir, fname).replace("\\", "/")
    return rel_path

def _columns_info(db: Session):
    rows = db.execute(text("""
        SELECT column_name, is_nullable, data_type, column_default
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = 'uploads'
    """)).fetchall()
    # {name: {"nullable": True/False, "type": "...", "default": "..."}}
    return {r[0]: {"nullable": (r[1] != "NO"), "type": (r[2] or ""), "default": r[3]} for r in rows}

def _insert_upload_dynamic(db: Session, *, slug: str, kind: str, rel_path: str, up: UploadFile, abs_path: str):
    info = _columns_info(db)

    original_name = up.filename or _safe_name("upload")
    guessed_mime = (up.content_type or "").strip() or (mimetypes.guess_type(original_name)[0] or "application/octet-stream")
    try:
        size_bytes = os.path.getsize(abs_path)
    except OSError:
        size_bytes = None

    # Base: valorizza solo le colonne "note" e comuni; MAI 'id'
    data = {}
    reserved_skip = {"id", "created_at", "updated_at"}  # lasciamo al DB
    if "case_id" in info:        data["case_id"] = slug
    if "kind" in info:           data["kind"] = kind
    if "object_path" in info:    data["object_path"] = rel_path
    if "original_name" in info:  data["original_name"] = original_name

    # Compat: content_type vs mime_type
    if "content_type" in info:   data["content_type"] = guessed_mime
    if "mime_type" in info:      data["mime_type"] = guessed_mime

    if "size_bytes" in info and size_bytes is not None:
        data["size_bytes"] = int(size_bytes)

    # Per eventuali altre colonne NOT NULL senza default, tentiamo fallback prudenti
    for col, meta in info.items():
        if col in data or col in reserved_skip:
            continue
        if not meta["nullable"]:
            # se il DB ha un default (column_default) → lasciamo che lo applichi
            if meta.get("default"):
                continue
            t = (meta["type"] or "").lower()
            # fallback minimi; evitare tipi ignoti
            if "char" in t or "text" in t:
                data[col] = ""
            elif "int" in t or "numeric" in t or "double" in t or "real" in t or "decimal" in t:
                # ⚠️ NON impostare 'id'.. già escluso sopra
                data[col] = 0
            elif "bool" in t:
                data[col] = False
            else:
                # timestamp/date/time → lasciamo al DB (se manca default e NOT NULL, fallirà e sapremo quale campo aggiungere)
                pass

    if not data:
        raise HTTPException(status_code=500, detail="Schema 'uploads' non riconosciuto: nessuna colonna gestibile.")

    columns_sql = ", ".join(data.keys())
    placeholders = ", ".join(f":{k}" for k in data.keys())
    sql = text(f"INSERT INTO uploads ({columns_sql}) VALUES ({placeholders})")
    db.execute(sql, data)
    db.commit()

# -----------------------------
# Upload Bilancio Contabile (BC) — alias legacy /upload-tb
# -----------------------------
@router.post("/cases/{slug}/upload-tb")
@router.post("/cases/{slug}/upload-bc")
async def upload_bc(slug: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not _case_exists(db, slug):
        raise HTTPException(status_code=404, detail="Case not found")
    if not file:
        raise HTTPException(status_code=400, detail="Missing file")

    rel_path = _save_file(slug, file)
    abs_path = os.path.abspath(os.path.join(STORAGE_ROOT, rel_path))
    _insert_upload_dynamic(db, slug=slug, kind="bc", rel_path=rel_path, up=file, abs_path=abs_path)

    size = os.path.getsize(abs_path) if os.path.exists(abs_path) else None
    return {
        "status": "ok",
        "kind": "bc",
        "object_path": rel_path,
        "original_name": file.filename,
        "mime_type": (file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"),
        "size_bytes": size,
    }

# -----------------------------
# Upload XBRL (XML/XBRL)
# -----------------------------
@router.post("/cases/{slug}/upload-xbrl")
async def upload_xbrl(slug: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not _case_exists(db, slug):
        raise HTTPException(status_code=404, detail="Case not found")
    if not file:
        raise HTTPException(status_code=400, detail="Missing file")

    rel_path = _save_file(slug, file)
    abs_path = os.path.abspath(os.path.join(STORAGE_ROOT, rel_path))
    _insert_upload_dynamic(db, slug=slug, kind="xbrl", rel_path=rel_path, up=file, abs_path=abs_path)

    size = os.path.getsize(abs_path) if os.path.exists(abs_path) else None
    return {
        "status": "ok",
        "kind": "xbrl",
        "object_path": rel_path,
        "original_name": file.filename,
        "mime_type": (file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"),
        "size_bytes": size,
    }
