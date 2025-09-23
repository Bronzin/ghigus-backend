from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.case import Case
from app.models.upload import Upload
from app.models.case_snapshot import CaseSnapshot
from ..db.deps import get_db
from ..services.xbrl_ingest import parse_xbrl_bytes
from ..services.tb_ingest import parse_tb_bytes
from ..services.storage import download_bytes


router = APIRouter(prefix="/cases", tags=["cases"])

def _get_case(db: Session, case_id: str) -> Case | None:
    return db.execute(
        select(Case).where((Case.id == case_id) | (Case.slug == case_id)).limit(1)
    ).scalars().first()

@router.get("/{case_id}/snapshots", summary="Lista snapshot")
def list_snapshots(case_id: str, db: Session = Depends(get_db)):
    case = _get_case(db, case_id) or _not_found()
    q = select(
        CaseSnapshot.id, CaseSnapshot.created_at,
        CaseSnapshot.xbrl_upload_id, CaseSnapshot.tb_upload_id
    ).where(CaseSnapshot.case_id == case.id).order_by(desc(CaseSnapshot.created_at))
    rows = db.execute(q).all()
    return [dict(r._mapping) for r in rows]

@router.get("/{case_id}/snapshots/{snapshot_id}", summary="Dettaglio snapshot")
def get_snapshot(case_id: str, snapshot_id: str, db: Session = Depends(get_db)):
    case = _get_case(db, case_id) or _not_found()
    snap = db.get(CaseSnapshot, snapshot_id)
    if not snap or snap.case_id != case.id:
        raise HTTPException(404, "Snapshot not found")
    return {"id": snap.id, "created_at": snap.created_at, "canonical": snap.canonical}
    
@router.post("/{case_id}/ingest", status_code=status.HTTP_201_CREATED, summary="Costruisci snapshot canonico da XBRL + TB")
def ingest(case_id: str, db: Session = Depends(get_db)):
    case = _get_case(db, case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    xbrl = db.execute(
        select(Upload).where(Upload.case_id == case.id, Upload.kind == "xbrl").order_by(desc(Upload.created_at)).limit(1)
    ).scalars().first()
    tb = db.execute(
        select(Upload).where(Upload.case_id == case.id, Upload.kind == "tb").order_by(desc(Upload.created_at)).limit(1)
    ).scalars().first()

    if not xbrl:
        raise HTTPException(400, "Missing XBRL upload for this case")
    if not tb:
        raise HTTPException(400, "Missing TB upload for this case")

    xb = download_bytes(xbrl.object_path)
    tb_bytes = download_bytes(tb.object_path)

    x_data = parse_xbrl_bytes(xb)
    t_data = parse_tb_bytes(tb_bytes)

    canonical = {
        "meta": {"case_id": case.id},
        "xbrl": x_data,
        "tb": t_data,
    }

    snap = CaseSnapshot(
        id=str(uuid4()),
        case_id=case.id,
        xbrl_upload_id=xbrl.id,
        tb_upload_id=tb.id,
        canonical=canonical,
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return {"snapshot_id": snap.id, "xbrl_upload_id": xbrl.id, "tb_upload_id": tb.id}

@router.get("/{case_id}/canonical", summary="Leggi ultimo snapshot canonico")
def get_canonical(case_id: str, db: Session = Depends(get_db)):
    case = _get_case(db, case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    snap = db.execute(
        select(CaseSnapshot).where(CaseSnapshot.case_id == case.id).order_by(desc(CaseSnapshot.created_at)).limit(1)
    ).scalars().first()
    if not snap:
        raise HTTPException(404, "No snapshot")
    return snap.canonical
