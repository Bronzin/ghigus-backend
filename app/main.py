# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Side-effect: registra i modelli sul metadata
from app.db import base as _models  # noqa: F401

# ----------------------------
# 1) Istanza FastAPI
# ----------------------------
app = FastAPI(title="Ghigus API", version="0.1")

# ----------------------------
# 2) CORS (frontend Vite)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# 3) Health & debug routes
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/_debug/routes")
def _debug_routes():
    return {"routes": [getattr(r, "path", str(r)) for r in app.routes]}

# ----------------------------
# 4) Router include (ognuno UNA volta)
#    Nota: tutti gli include avvengono DOPO la creazione di `app`
# ----------------------------

# 4.1 Router always-on (no try/except)
from app.routers import cases_delete
app.include_router(cases_delete.router)

# cases_cflow (router sincrono basato su Session)
from app.routers import cases_cflow
app.include_router(cases_cflow.router)

# monthly API
from app.api.routers import monthly
app.include_router(monthly.router)

# processing (DEVE restare fuori da try/except)
from app.api.routers.processing import router as processing_router
import app.api.routers.processing as _proc_mod  # per log utili
print("PROCESSING_MODULE_FILE =", _proc_mod.__file__)
print("PROCESSING_ROUTER_COUNT_BEFORE_INCLUDE =", len(getattr(processing_router, "routes", [])))
app.include_router(processing_router)

# 4.2 Router opzionali (tolleranti in dev)
try:
    from app.api.routers import uploads as uploads_router
    app.include_router(uploads_router.router)
except Exception as e:
    print("Warn: uploads router not loaded:", e)

try:
    # dashboard payload (nuovo endpoint)
    from app.api.routers.dashboard import router as dashboard_router
    app.include_router(dashboard_router)
except Exception as e:
    print("Warn: dashboard router not loaded:", e)

try:
    from app.api.routers import cases as cases_router
    app.include_router(cases_router.router)
except Exception as e:
    print("Warn: cases router not loaded:", e)

try:
    from app.api.routers.riclass import router as riclass_router
    app.include_router(riclass_router)
except Exception as e:
    print("Warn: riclass router not loaded:", e)

try:
    from app.api.routers.maps import router as maps_router
    app.include_router(maps_router)
except Exception as e:
    print("Warn: maps router not loaded:", e)
