# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

# Side-effect: registra i modelli sul metadata
from app.db import base as _models  # noqa: F401

# ----------------------------
# 1) Istanza FastAPI
# ----------------------------
app = FastAPI(title="Ghigus API", version="0.1")

# ----------------------------
# 2) Rate Limiting
# ----------------------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ----------------------------
# 3) Security Headers Middleware
# ----------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# ----------------------------
# 4) CORS (frontend Vite + production)
# ----------------------------
# In development, allow localhost ports
dev_origins = [
    f"http://{host}:{port}"
    for host in ("localhost", "127.0.0.1")
    for port in range(5173, 5200)
]
# Combine with configured allowed_origins for production
all_origins = list(set(dev_origins + settings.allowed_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# 5) Health & debug routes
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/_debug/routes")
def _debug_routes():
    return {"routes": [getattr(r, "path", str(r)) for r in app.routes]}

# ----------------------------
# 6) Auth Router (MUST be first, non-protected)
# ----------------------------
from app.api.routers.auth import router as auth_router
app.include_router(auth_router)

# ----------------------------
# 7) Protected Router (tutti i router applicativi richiedono auth)
# ----------------------------
from fastapi import APIRouter, Depends
from app.db.deps import get_current_user

# Router padre che applica l'autenticazione a tutti i sub-router
protected_router = APIRouter(dependencies=[Depends(get_current_user)])

# 7.1 Router always-on (no try/except)
from app.routers import cases_delete
protected_router.include_router(cases_delete.router)

# cases_cflow (router sincrono basato su Session)
from app.routers import cases_cflow
protected_router.include_router(cases_cflow.router)

# monthly API
from app.api.routers import monthly
protected_router.include_router(monthly.router)

# processing (DEVE restare fuori da try/except)
from app.api.routers.processing import router as processing_router
import app.api.routers.processing as _proc_mod  # per log utili
print("PROCESSING_MODULE_FILE =", _proc_mod.__file__)
print("PROCESSING_ROUTER_COUNT_BEFORE_INCLUDE =", len(getattr(processing_router, "routes", [])))
protected_router.include_router(processing_router)

# 7.2 Router opzionali (tolleranti in dev)
try:
    from app.api.routers import uploads as uploads_router
    protected_router.include_router(uploads_router.router)
except Exception as e:
    print("Warn: uploads router not loaded:", e)

try:
    # dashboard payload (nuovo endpoint)
    from app.api.routers.dashboard import router as dashboard_router
    protected_router.include_router(dashboard_router)
except Exception as e:
    print("Warn: dashboard router not loaded:", e)

try:
    from app.api.routers import cases as cases_router
    protected_router.include_router(cases_router.router)
except Exception as e:
    print("Warn: cases router not loaded:", e)

try:
    from app.api.routers.riclass import router as riclass_router
    protected_router.include_router(riclass_router)
except Exception as e:
    print("Warn: riclass router not loaded:", e)

try:
    from app.api.routers.maps import router as maps_router
    protected_router.include_router(maps_router)
except Exception as e:
    print("Warn: maps router not loaded:", e)

# ----------------------------
# 8) MDM Routers (protected)
# ----------------------------
try:
    from app.api.routers.assumptions import router as assumptions_router
    protected_router.include_router(assumptions_router)
except Exception as e:
    print("Warn: assumptions router not loaded:", e)

try:
    from app.api.routers.attivo import router as attivo_router
    protected_router.include_router(attivo_router)
except Exception as e:
    print("Warn: attivo router not loaded:", e)

try:
    from app.api.routers.passivo import router as passivo_router
    protected_router.include_router(passivo_router)
except Exception as e:
    print("Warn: passivo router not loaded:", e)

try:
    from app.api.routers.liquidazione import router as liquidazione_router
    protected_router.include_router(liquidazione_router)
except Exception as e:
    print("Warn: liquidazione router not loaded:", e)

try:
    from app.api.routers.auxiliary import router as auxiliary_router
    protected_router.include_router(auxiliary_router)
except Exception as e:
    print("Warn: auxiliary router not loaded:", e)

try:
    from app.api.routers.projections import router as projections_router
    protected_router.include_router(projections_router)
except Exception as e:
    print("Warn: projections router not loaded:", e)

try:
    from app.api.routers.concordato import router as concordato_router
    protected_router.include_router(concordato_router)
except Exception as e:
    print("Warn: concordato router not loaded:", e)

try:
    from app.api.routers.cruscotto import router as cruscotto_router
    protected_router.include_router(cruscotto_router)
except Exception as e:
    print("Warn: cruscotto router not loaded:", e)

try:
    from app.api.routers.scenarios import router as scenarios_router
    protected_router.include_router(scenarios_router)
except Exception as e:
    print("Warn: scenarios router not loaded:", e)

try:
    from app.api.routers.xbrl_facts import router as xbrl_facts_router
    protected_router.include_router(xbrl_facts_router)
except Exception as e:
    print("Warn: xbrl_facts router not loaded:", e)

try:
    from app.api.routers.finanziamenti import router as finanziamenti_router
    protected_router.include_router(finanziamenti_router)
except Exception as e:
    print("Warn: finanziamenti router not loaded:", e)

try:
    from app.api.routers.scadenziario_tributario import router as scadenziario_tributario_router
    protected_router.include_router(scadenziario_tributario_router)
except Exception as e:
    print("Warn: scadenziario_tributario router not loaded:", e)

try:
    from app.api.routers.conti import router as conti_router
    protected_router.include_router(conti_router)
except Exception as e:
    print("Warn: conti router not loaded:", e)

try:
    from app.api.routers.imm_fin import router as imm_fin_router
    protected_router.include_router(imm_fin_router)
except Exception as e:
    print("Warn: imm_fin router not loaded:", e)

try:
    from app.api.routers.cnc import router as cnc_router
    protected_router.include_router(cnc_router)
except Exception as e:
    print("Warn: cnc router not loaded:", e)

# Include il router protetto nell'app
app.include_router(protected_router)
