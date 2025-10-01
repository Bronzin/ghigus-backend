# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import cases_delete

# Importa i modelli SENZA sovrascrivere la variabile 'app'
from app.db import base as _models  # noqa: F401  (registra tutte le tabelle nel metadata)

app = FastAPI(title="Ghigus API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases_delete.router)

from app.api.routers import uploads as uploads_router
app.include_router(uploads_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}

# Routers (wrappati in try per tolleranza)
try:
    from app.api.routers import cases as cases_router
    app.include_router(cases_router.router)
except Exception:
    pass

try:
    from app.api.routers import uploads as uploads_router
    app.include_router(uploads_router.router)
except Exception:
    pass

try:
    from app.api.routers.processing import router as processing_router
    app.include_router(processing_router)
except Exception:
    pass

try:
    from app.api.routers.riclass import router as riclass_router
    app.include_router(riclass_router)
except Exception:
    pass

try:
    from app.api.routers.maps import router as maps_router
    app.include_router(maps_router)
except Exception:
    pass
