# app/db/session.py
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Carica .env (se presente)
try:
    from dotenv import load_dotenv, find_dotenv
    _path = find_dotenv()
    if _path:
        load_dotenv(_path)
except Exception:
    # ok se manca python-dotenv in ambienti dove l'ENV è già settata
    pass

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL non impostata. Aggiungila nel file .env o come variabile d'ambiente."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
