# app/services/xbrl_ingest.py
from typing import Dict, Any

def parse_xbrl_bytes(data: bytes) -> Dict[str, Any]:
    """
    Stub: parser XBRL da rimpiazzare quando avrai il file reale.
    Per ora ritorna una struttura 'canonica' vuota.
    """
    return {
        "meta": {"source": "xbrl", "ok": True},
        "bs": {"assets": {}, "liabilities": {}},
        "pl": {},
    }
