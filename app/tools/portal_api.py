# app/tools/portal_api.py
from typing import Dict
import time

def dados_protocolo(protocol_id: str) -> Dict:
    """
    Mock Portal API: Retorna dados do protocolo (cliente, order, anexos).
    """
    # Simulando latência da chamada http
    time.sleep(0.2)

    # Exemplo de retorno
    return {
        "protocol_id": protocol_id,
        "customer": {
            "name": "João Silva",
            "cpf": "123.456.789-00",
            "email": "joao@example.com"
        },
        "order": {
            "order_id": "ORD-1001",
            "items": [
                {"id_item_pedido": "AAA111", "qty": 1, "description": "Produto AAA111"}
            ],
            "purchase_date": "2025-09-01"
        },
        "attachments": {
            "invoice_image_path": "/path/to/invoice_{}.jpg".format(protocol_id),
            "product_image_path": "/path/to/product_{}.jpg".format(protocol_id)
        }
    }
