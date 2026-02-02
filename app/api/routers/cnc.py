# app/api/routers/cnc.py
"""Router for CNC PowerPoint generation."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.services.cnc_generator import generate

logger = logging.getLogger(__name__)

router = APIRouter(tags=["cnc"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(
        text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


@router.post("/cases/{slug}/genera-cnc")
def genera_cnc(
    slug: str,
    scenario: str = Query("base"),
    db: Session = Depends(get_db),
):
    """Generate CNC PowerPoint presentation for a case.

    Returns a downloadable .pptx file.
    """
    _ensure_case(db, slug)

    try:
        buf = generate(
            db=db,
            case_id=slug,
            scenario_id=scenario,
            use_mock=settings.cnc_use_mock,
        )
    except Exception as exc:
        logger.exception("CNC generation failed for case=%s", slug)
        raise HTTPException(
            status_code=500,
            detail=f"CNC generation failed: {exc}",
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"CNC_Presentazione_{slug}_{timestamp}.pptx"

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
