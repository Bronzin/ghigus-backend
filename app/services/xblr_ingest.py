from typing import Dict, Any

def parse_xbrl_bytes(data: bytes) -> Dict[str, Any]:
    # Stub: da sostituire quando avrai l'XBRL vero
    return {
        "meta": {"source": "xbrl", "ok": True},
        "bs": {"assets": {}, "liabilities": {}},
        "pl": {},
    }
