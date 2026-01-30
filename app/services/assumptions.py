# app/services/assumptions.py
"""Service layer per la gestione delle Assumptions."""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.schemas.assumptions import AssumptionsData, ParametriPiano
from app.services.timeline import build_timeline, PeriodInfo
from typing import List


def get_assumptions(db: Session, case_id: str, scenario_id: str = "base") -> Optional[AssumptionsData]:
    """Legge le assumptions dal DB; ritorna None se non esistono."""
    row = db.execute(
        text("SELECT data FROM assumptions WHERE case_id = :cid AND scenario_id = :sid ORDER BY created_at DESC LIMIT 1"),
        {"cid": case_id, "sid": scenario_id},
    ).fetchone()
    if not row:
        return None
    raw = row[0]
    if raw is None:
        return None
    return AssumptionsData.model_validate(raw)


def save_assumptions(db: Session, case_id: str, data: AssumptionsData, scenario_id: str = "base") -> None:
    """Salva (upsert) le assumptions per un caso e scenario."""
    existing = db.execute(
        text("SELECT id FROM assumptions WHERE case_id = :cid AND scenario_id = :sid LIMIT 1"),
        {"cid": case_id, "sid": scenario_id},
    ).fetchone()

    payload = data.model_dump(mode="json")

    if existing:
        db.execute(
            text("UPDATE assumptions SET data = :data WHERE case_id = :cid AND scenario_id = :sid"),
            {"cid": case_id, "sid": scenario_id, "data": payload},
        )
    else:
        import uuid
        db.execute(
            text("INSERT INTO assumptions (id, case_id, scenario_id, data) VALUES (:id, :cid, :sid, :data)"),
            {"id": str(uuid.uuid4()), "cid": case_id, "sid": scenario_id, "data": payload},
        )
    db.commit()


def get_plan_timeline(db: Session, case_id: str, scenario_id: str = "base") -> List[PeriodInfo]:
    """Costruisce la timeline di piano a partire dalle assumptions."""
    assumptions = get_assumptions(db, case_id, scenario_id)
    if assumptions is None:
        piano = ParametriPiano()
    else:
        piano = assumptions.piano
    return build_timeline(piano.start_year, piano.start_month, piano.duration_months)


def get_assumptions_or_default(db: Session, case_id: str, scenario_id: str = "base") -> AssumptionsData:
    """Restituisce le assumptions o i default se non configurate."""
    data = get_assumptions(db, case_id, scenario_id)
    if data is None:
        return AssumptionsData()
    return data
