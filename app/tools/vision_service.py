# app/tools/vision_service.py
from typing import Dict
import time

def classify_damage(image_path: str) -> Dict:
    """
    Mock vision classifier: detecta se há dano.
    Substituir pela integração com um modelo de visão (ViT, YOLO, etc).
    """
    time.sleep(0.2)
    return {
        "label": "defeito_visivel",
        "confidence": 0.92,
        "notes": "Risco: rachadura na carcaça detectada."
    }
