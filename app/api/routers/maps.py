from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import csv

from app.db.session import get_db
from app.db.models.staging import MapSP, MapCE

router = APIRouter(tags=["maps"])

REQUIRED_HEADERS = ["imported_code", "imported_desc", "riclass_code", "riclass_desc"]

def _case_exists(db: Session, slug: str) -> bool:
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    return bool(row)

def _parse_csv(file: UploadFile):
    try:
        content = file.file.read().decode("utf-8-sig")
    finally:
        file.file.close()
    reader = csv.DictReader(content.splitlines())
    headers = [h.strip() for h in (reader.fieldnames or [])]
    for col in REQUIRED_HEADERS:
        if col not in headers:
            raise HTTPException(
                status_code=400,
                detail=f"CSV '{file.filename}': manca la colonna richiesta '{col}'. Intestazioni presenti: {headers}",
            )
    rows = []
    for r in reader:
        rows.append({
            "imported_code": (r.get("imported_code") or "").strip(),
            "imported_desc": (r.get("imported_desc") or "").strip() or None,
            "riclass_code": (r.get("riclass_code") or "").strip(),
            "riclass_desc": (r.get("riclass_desc") or "").strip() or None,
        })
    return rows

def _import_maps(db: Session, slug: Optional[str], replace: bool, file_sp: Optional[UploadFile], file_ce: Optional[UploadFile]):
    if not file_sp and not file_ce:
        raise HTTPException(status_code=400, detail="Nessun file ricevuto. Invia file_sp e/o file_ce.")

    # Se slug è passato, verifica che il case esista; se None → import globale
    if slug is not None and not _case_exists(db, slug):
        raise HTTPException(status_code=404, detail="Case not found")

    imported = {"scope": "global" if slug is None else f"case:{slug}", "sp": 0, "ce": 0}

    if replace:
        if file_sp:
            db.query(MapSP).filter(MapSP.case_id == slug).delete()  # slug può essere None (globale)
        if file_ce:
            db.query(MapCE).filter(MapCE.case_id == slug).delete()
        db.commit()

    if file_sp:
        rows = _parse_csv(file_sp)
        for r in rows:
            if not r["imported_code"] or not r["riclass_code"]:
                continue
            db.add(MapSP(
                case_id = slug,  # None = mappa globale
                imported_code = r["imported_code"],
                imported_desc = r["imported_desc"],
                riclass_code  = r["riclass_code"],
                riclass_desc  = r["riclass_desc"],
            ))
            imported["sp"] += 1

    if file_ce:
        rows = _parse_csv(file_ce)
        for r in rows:
            if not r["imported_code"] or not r["riclass_code"]:
                continue
            db.add(MapCE(
                case_id = slug,
                imported_code = r["imported_code"],
                imported_desc = r["imported_desc"],
                riclass_code  = r["riclass_code"],
                riclass_desc  = r["riclass_desc"],
            ))
            imported["ce"] += 1

    db.commit()
    return {"status": "ok", "imported": imported}

# Import GLOBALE (default). slug opzionale come query per eventuale override per-pratica.
@router.post("/maps/import-csv")
async def import_maps_csv_global(
    db: Session = Depends(get_db),
    replace: bool = Query(True, description="Se True, cancella le mappe esistenti nello scope scelto."),
    slug: Optional[str] = Query(None, description="Se valorizzato, importa per quello slug; altrimenti globale."),
    file_sp: Optional[UploadFile] = File(None, description="CSV SP: imported_code,imported_desc,riclass_code,riclass_desc"),
    file_ce: Optional[UploadFile] = File(None, description="CSV CE: imported_code,imported_desc,riclass_code,riclass_desc"),
):
    return _import_maps(db, slug=slug, replace=replace, file_sp=file_sp, file_ce=file_ce)

# Compat: endpoint per-pratica
@router.post("/cases/{slug}/maps/import-csv")
async def import_maps_csv_case(
    slug: str,
    db: Session = Depends(get_db),
    replace: bool = Query(True, description="Se True, cancella le mappe esistenti del case prima di importare."),
    file_sp: Optional[UploadFile] = File(None, description="CSV SP"),
    file_ce: Optional[UploadFile] = File(None, description="CSV CE"),
):
    return _import_maps(db, slug=slug, replace=replace, file_sp=file_sp, file_ce=file_ce)
