# app/tools/inventory_api.py
from typing import Dict
import time
import uuid

_STOCK = {"AAA111": 3, "BBB222": 0}

def check_and_reserve(id_item_pedido: str, qty: int, idempotency_key: str) -> Dict:
    time.sleep(0.15)
    avail = _STOCK.get(id_item_pedido, 0)
    if avail >= qty:
        _STOCK[id_item_pedido] = avail - qty
        reservation_id = str(uuid.uuid4())
        return {"available": True, "reservation_id": reservation_id}
    else:
        return {"available": False, "reservation_id": None}
