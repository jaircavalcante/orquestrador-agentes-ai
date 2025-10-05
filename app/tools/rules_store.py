# app/tools/rules_store.py
from typing import Dict, List
import time

_RULES = {
    "AAA111": [
        {
            "rule_id": "R-A1",
            "description": "Troca por defeito em até 30 dias da compra",
            "max_days": 30,
            "requires_photos": True,
            "allow_credit": True
        }
    ]
}

def lookup_rules_for_id_item_pedido(id_item_pedido: str) -> List[Dict]:
    time.sleep(0.1)
    return _RULES.get(id_item_pedido, [])
