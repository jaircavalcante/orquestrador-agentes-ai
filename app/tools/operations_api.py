# app/tools/operations_api.py
from typing import Dict
import time
import uuid

def create_exchange(payload: Dict, idempotency_key: str) -> Dict:
    """
    Mock call to execute a trade/exchange in Operations API.
    Persistar logs, usar idempotency_key.
    """
    time.sleep(0.2)
    return {"status": "ok", "exchange_id": str(uuid.uuid4()), "payload": payload}
