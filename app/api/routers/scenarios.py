# app/api/routers/scenarios.py
"""CRUD per la gestione degli scenari MDM."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional

from app.db.session import get_db
from app.db.models.mdm_scenario import MdmScenario

router = APIRouter(tags=["scenarios"])


def _ensure_case(db: Session, slug: str):
    row = db.execute(text("SELECT 1 FROM cases WHERE id = :slug LIMIT 1"), {"slug": slug}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")


class ScenarioCreate(BaseModel):
    scenario_slug: str
    name: str
    description: Optional[str] = None
    is_default: bool = False


class ScenarioOut(BaseModel):
    id: int
    case_id: str
    scenario_slug: str
    name: str
    description: Optional[str] = None
    is_default: bool

    class Config:
        from_attributes = True


class ScenariosResponse(BaseModel):
    case_id: str
    scenarios: List[ScenarioOut]


@router.get("/cases/{slug}/scenarios", response_model=ScenariosResponse)
def list_scenarios(slug: str, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    items = (
        db.query(MdmScenario)
        .filter(MdmScenario.case_id == slug)
        .order_by(MdmScenario.is_default.desc(), MdmScenario.id)
        .all()
    )
    return ScenariosResponse(case_id=slug, scenarios=items)


@router.post("/cases/{slug}/scenarios", response_model=ScenarioOut, status_code=201)
def create_scenario(slug: str, body: ScenarioCreate, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    existing = (
        db.query(MdmScenario)
        .filter(MdmScenario.case_id == slug, MdmScenario.scenario_slug == body.scenario_slug)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail=f"Scenario '{body.scenario_slug}' already exists for this case")

    scenario = MdmScenario(
        case_id=slug,
        scenario_slug=body.scenario_slug,
        name=body.name,
        description=body.description,
        is_default=body.is_default,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


@router.delete("/cases/{slug}/scenarios/{scenario_slug}", status_code=204)
def delete_scenario(slug: str, scenario_slug: str, db: Session = Depends(get_db)):
    _ensure_case(db, slug)
    if scenario_slug == "base":
        raise HTTPException(status_code=400, detail="Cannot delete the 'base' scenario")

    scenario = (
        db.query(MdmScenario)
        .filter(MdmScenario.case_id == slug, MdmScenario.scenario_slug == scenario_slug)
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    db.delete(scenario)
    db.commit()
