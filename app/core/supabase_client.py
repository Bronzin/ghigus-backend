# app/core/supabase_client.py
from functools import lru_cache
from supabase import create_client, Client
from app.core.config import settings

@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Istanzia e riusa un unico client Supabase per processo."""
    return create_client(settings.supabase_url, settings.supabase_service_key)
