# app/routers/cases_compute.py
"""
Router intenzionalmente vuoto.
L'endpoint GET /cases/{case_id}/compute ora vive in app/routers/cases.py
per evitare duplicazioni di path.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/cases", tags=["cases"])
# Nessun endpoint qui.
