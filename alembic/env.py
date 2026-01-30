from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# --- PATH/PYTHONPATH ---
import os
import sys
from importlib import import_module
from pathlib import Path


# ...
# Carica .env
try:
    from dotenv import load_dotenv, find_dotenv
    _path = find_dotenv()
    if _path:
        load_dotenv(_path)
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]  # .../ghigus-backend
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Alembic config ---
config = context.config

# --- DB URL da settings o env ---
db_url = None
try:
    from app.core.config import settings
    db_url = getattr(settings, "database_url", None)
except Exception:
    pass

if not db_url:
    db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise RuntimeError("DATABASE_URL non impostata e settings.database_url non disponibile")

config.set_main_option("sqlalchemy.url", db_url)

# --- Logging alembic.ini (facoltativo) ---
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Import dinamico di Base ---
# Puoi forzare il modulo con ALEMBIC_BASE_MODULE, es: "app.models"
base_module = os.getenv("ALEMBIC_BASE_MODULE", "app.db.models")
candidates = [base_module, "app.models", "app.db.base", "app.models.base"]

Base = None
last_err = None
for mod in candidates:
    try:
        m = import_module(mod)
        Base = getattr(m, "Base")
        break
    except Exception as e:
        last_err = e
        continue

if Base is None:
    raise ImportError(
        f"Impossibile importare 'Base'. Moduli tentati: {candidates}. Ultimo errore: {last_err}"
    )

# --- Metadata dei modelli ---
target_metadata = Base.metadata


def run_migrations_offline():
    """Esegue migrazioni in modalità offline (senza connettersi)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Esegue migrazioni con connessione reale."""
    configuration = config.get_section(config.config_ini_section)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,            
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
