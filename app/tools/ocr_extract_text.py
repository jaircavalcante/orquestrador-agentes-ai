from typing import Dict
import time

def ocr_extract_text(image_path: str) -> Dict:
    """
    Mock OCR: retorna campos extraídos da nota.
    Substituir pela integração (Tesseract, Google Vision, Textract, etc).
    """
    time.sleep(0.3)
    return {
        "raw_text": "Nota fiscal ... ID_ITEM_PEDIDO: AAA111 Quantidade: 1 Valor: 199.90 Data: 2025-09-01",
        "extracted": {
            "id_item_pedido": "AAA111",
            "quantity": 1,
            "value": 199.9,
            "date": "2025-09-01",
            "invoice_number": "NF-12345"
        },
        "confidence": 0.95
    }
