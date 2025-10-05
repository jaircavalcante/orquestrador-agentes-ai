import json
import uuid
import logging

from app.agents.document_agent import build_document_agent
from app.agents.ocr_agent import build_ocr_vision_agent
from app.agents.rules_agent import build_rules_agent
from app.agents.inventory_agent import build_inventory_agent
from app.agents.decision_agent import build_decision_agent
from app.tools.portal_api import dados_protocolo

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Configuração padrão do modelo
MODEL = "gpt-4o-mini"


def init_agents(model: str = MODEL):
    """Inicializa todos os agentes e retorna um dicionário."""
    return {
        "document_agent": build_document_agent(True),
        "ocr_agent": build_ocr_vision_agent(model),
        "rules_agent": build_rules_agent(model),
        "inventory_agent": build_inventory_agent(model),
        "decision_agent": build_decision_agent(model)
    }


def orquestrador(protocol_id: str, agents: dict):
    logger.info(f"Recebendo protocolo para iniciar validação: {protocol_id}")

    idempotency_key = f"{protocol_id}-{uuid.uuid4()}"
    logger.info(f"Identificador único gerado: {idempotency_key}")

    # ========================================================================================================================
    # 1️⃣ Document Agent
    # ========================================================================================================================
    doc_json = {}
    try:
        doc_resp = agents["document_agent"].invoke({"input": protocol_id})
        doc_json = json.loads(doc_resp.get("output", doc_resp)) if isinstance(doc_resp, dict) else json.loads(doc_resp)
    except Exception as e:
        doc_json = {"raw": str(doc_resp), "confidence": 0.6}
        logger.warning(f"Document Agent falhou: {e}")

    # ========================================================================================================================
    # 2️⃣ OCR/Vision Agent
    # ========================================================================================================================
    ocr_json = {}
    try:
        ocr_inputs = {
            "input": {
                "invoice_image": doc_json.get("attachments", {}).get("invoice_image_path"),
                "product_image": doc_json.get("attachments", {}).get("product_image_path")
            }
        }
        ocr_resp = agents["ocr_agent"].invoke(ocr_inputs)
        ocr_json = ocr_resp.get("output", ocr_resp) if isinstance(ocr_resp, dict) else ocr_resp
    except Exception as e:
        ocr_json = {"raw": str(ocr_resp), "confidence": 0.6}
        logger.warning(f"OCR Agent falhou: {e}")

    # ========================================================================================================================
    # 3️⃣ Rules Agent
    # ========================================================================================================================
    
    rules_json = {}
    try:
        code_product = ocr_json.get("ocr", {}).get("extracted", {}).get("code_product") \
              or doc_json.get("order", {}).get("items", [{}])[0].get("code_product", "code_product-MOCK")
        rules_inputs = {"input": {"code_product": code_product, "ocr": ocr_json}}
        rules_resp = agents["rules_agent"].invoke(rules_inputs)
        rules_json = rules_resp.get("output", rules_resp) if isinstance(rules_resp, dict) else rules_resp
    except Exception as e:
        rules_json = {"raw": str(rules_resp), "eligible": True, "confidence": 0.7}
        logger.warning(f"Rules Agent falhou: {e}")

    # ========================================================================================================================
    # 4️⃣ Inventory Agent
    # ========================================================================================================================

    inventory_json = {"available": False, "reservation_id": None, "confidence": 0.0}
    try:
        need_reserve = True
        if need_reserve:
            inv_inputs = {"messages": [{"role": "user", "content": json.dumps({
                "code_product": code_product, "qty": 1, "idempotency_key": idempotency_key
            })}]}

            inv_resp = agents["inventory_agent"].invoke(inv_inputs)
            inventory_json = json.loads(inv_resp) if isinstance(inv_resp, str) else inv_resp

    except Exception as e:
        inventory_json = {"raw": str(inv_resp), "available": False, "confidence": 0.5}
        logger.warning(f"Inventory Agent falhou: {e}")

    # ========================================================================================================================
    # 5️⃣ Decision Agent
    # ========================================================================================================================
    decision_json = {}
    try:
        decision_inputs = {
            "input": {
                "document": doc_json,
                "ocr": ocr_json,
                "rules": rules_json,
                "inventory": inventory_json,
                "protocol_id": protocol_id,
                "idempotency_key": idempotency_key
            }
        }
        decision_resp = agents["decision_agent"].invoke(decision_inputs)
        decision_json = decision_resp.get("output", decision_resp) if isinstance(decision_resp, dict) else decision_resp
    except Exception as e:
        decision_json = {"raw": str(decision_resp), "decision": "escalate", "confidence": 0.4}
        logger.warning(f"Decision Agent falhou: {e}")

    # ========================================================================================================================
    # 6️⃣ Logging final / Auditoria
    # ========================================================================================================================
    logger.info("=== Resultado da Análise ===")
    logger.info(f"Protocol: {protocol_id}")
    logger.info(f"Decision: {json.dumps(decision_json, indent=2, ensure_ascii=False)}")

    return {
        "protocol": protocol_id,
        "decision": decision_json,
        "audit": {
            "document": doc_json,
            "ocr": ocr_json,
            "rules": rules_json,
            "inventory": inventory_json
        }
    }