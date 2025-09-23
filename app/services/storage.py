# app/services/storage.py
from __future__ import annotations
from typing import Optional, Any, Dict, Union, IO

from app.core.config import settings

BUCKET = settings.storage_bucket

# Tenteremo prima con 'supabase' (v2). In fallback 'storage3'.
_sb_create_client = None
_st_create_client = None

try:
    from supabase import create_client as _supabase_create_client  # supabase-py v2
    _sb_create_client = _supabase_create_client
except Exception:
    _sb_create_client = None

if _sb_create_client is None:
    try:
        from storage3 import create_client as _storage3_create_client  # storage3
        _st_create_client = _storage3_create_client
    except Exception:
        _st_create_client = None

_client_singleton: Any = None


def _client() -> Any:
    """Crea/fornisce un client Supabase sincrono, compatibile con 'supabase' o 'storage3'."""
    global _client_singleton
    if _client_singleton is not None:
        return _client_singleton

    url = settings.supabase_url
    key = settings.supabase_service_key

    if _sb_create_client is not None:
        # supabase-py v2: firma = create_client(url, key)
        _client_singleton = _sb_create_client(url, key)
        return _client_singleton

    if _st_create_client is not None:
        # storage3: alcune versioni richiedono is_async=False, altre no
        try:
            _client_singleton = _st_create_client(url, key, is_async=False)
        except TypeError:
            _client_singleton = _st_create_client(url, key)
        return _client_singleton

    raise RuntimeError("Nessun client Supabase trovato. Installa 'supabase' oppure 'storage3'.")


def upload_bytes(path: str, data: bytes, content_type: Optional[str] = None, upsert: bool = True) -> str:
    """Carica bytes nel bucket alla chiave 'path'."""
    file_options: Dict[str, Any] = {}
    if content_type:
        file_options["contentType"] = content_type

    # ⚠️ Alcune versioni del client pretendono stringhe, non bool, per l'header x-upsert
    if upsert is True:
        file_options["upsert"] = "true"
    elif upsert is False:
        file_options["upsert"] = "false"
    # se upsert è None, non lo mettiamo

    _client().storage.from_(BUCKET).upload(path, data, file_options=file_options)
    return path

def download_bytes(path: str) -> bytes:
    """
    Scarica i bytes dall'oggetto 'path' nel bucket.
    Compatibile con 'supabase' e 'storage3'.
    """
    res = _client().storage.from_(BUCKET).download(path)
    # alcune versioni restituiscono direttamente bytes, altre un dict
    if isinstance(res, (bytes, bytearray)):
        return bytes(res)
    if isinstance(res, dict):
        # tentativi comuni
        for k in ("data", "file", "content"):
            if k in res and isinstance(res[k], (bytes, bytearray)):
                return bytes(res[k])
    # fallback: prova ad accedere come attributo 'data'
    data = getattr(res, "data", None)
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    raise RuntimeError("Download failed: unexpected response type")



def upload_file(
    path: str,
    file_or_bytes: Union[str, bytes, bytearray, IO[bytes]],
    content_type: Optional[str] = None,
    upsert: bool = True,
) -> str:
    """
    Wrapper retro-compatibile:
    - se passi bytes/bytearray → carica direttamente;
    - se passi un file-like (ha .read()) → legge e carica;
    - se passi un percorso su disco (str) → apre, legge e carica.
    """
    if isinstance(file_or_bytes, (bytes, bytearray)):
        data = file_or_bytes
    elif hasattr(file_or_bytes, "read"):
        data = file_or_bytes.read()
    else:
        with open(str(file_or_bytes), "rb") as fh:
            data = fh.read()
    return upload_bytes(path, data, content_type=content_type, upsert=upsert)


def signed_url(path: str, expires_in: int = 600) -> str:
    """Genera una signed URL; gestisce sia 'signed_url' sia 'signedURL'."""
    res = _client().storage.from_(BUCKET).create_signed_url(path, expires_in)
    return res.get("signed_url") or res.get("signedURL") or ""
