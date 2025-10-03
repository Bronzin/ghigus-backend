# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Registra i modelli (import side-effect sul metadata)
from app.db import base as _models  # noqa: F401

# Router utilità indipendente
from app.routers import cases_delete

app = FastAPI(title="Ghigus API", version="0.1")

# CORS (frontend Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}

# Debug: elenco route caricate
@app.get("/_debug/routes")
def _debug_routes():
    return {"routes": [getattr(r, "path", str(r)) for r in app.routes]}

# Router delete (incluso esplicitamente)
app.include_router(cases_delete.router)

# ----------------------------
# Altri router: ognuno UNA sola volta
# ----------------------------

# uploads (tollerante in dev)
try:
    from app.api.routers import uploads as uploads_router
    app.include_router(uploads_router.router)
except Exception:
    pass

# cases (tollerante in dev)
try:
    from app.api.routers import cases as cases_router
    app.include_router(cases_router.router)
except Exception:
    pass

# ✅ processing (DEVE essere fuori da try/except)
from app.api.routers.processing import router as processing_router
import app.api.routers.processing as _proc_mod  # solo per log utili
print("PROCESSING_MODULE_FILE =", _proc_mod.__file__)
print("PROCESSING_ROUTER_COUNT_BEFORE_INCLUDE =", len(getattr(processing_router, "routes", [])))
app.include_router(processing_router)

# riclass (tollerante in dev)
try:
    from app.api.routers.riclass import router as riclass_router
    app.include_router(riclass_router)
except Exception:
    pass

# maps (tollerante in dev)
try:
    from app.api.routers.maps import router as maps_router
    app.include_router(maps_router)
except Exception:
    pass
