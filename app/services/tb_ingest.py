import csv, io
from typing import Dict, Any

def parse_tb_bytes(data: bytes) -> Dict[str, Any]:
    text = data.decode("utf-8", errors="ignore")
    f = io.StringIO(text)
    rows = list(csv.reader(f))
    headers = rows[0] if rows else []
    body = rows[1:] if rows else []
    return {"meta": {"source": "tb"}, "rows": len(body), "headers": headers}
