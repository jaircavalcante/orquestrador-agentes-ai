# app/agents/decision_agent.py
import random
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from app.tools.operations_api import create_exchange


@tool
def operations_create_exchange(payload: dict, idempotency_key: str) -> Dict:
    """Chama a API de operações para criar a troca/exchange."""
    return create_exchange(payload, idempotency_key)


DECISION_PROMPT = """
Você é o Agente de Decisão. Receberá saídas estruturadas de:
- DocumentAgent
- OCR/Vision Agent
- RulesAgent
- InventoryAgent

Aplique a política:
- Aprovação automática se eligible True E confiança combinada >= 0.90
- Proposta de crédito se eligible True E estoque indisponível
- Escalar se incompatibilidade do cliente ou confiança baixa

Retorne JSON:
{
  "decision": "aprovado|aprovado_com_condicoes|proposta_credito|escalado|revisao_humana",
  "action_payload": {...} ou null,
  "confidence": 0.0-1.0,
  "explanation": "texto curto",
  "audit_refs": [...]
}
Retorne SOMENTE JSON.
"""

DECISION_POLICY = {
    "auto_approve_threshold": 0.9,
    "low_confidence_threshold": 0.6
}


def build_decision_agent(model: str = "gpt-4o-mini", mock: bool = True):
    """
    Constrói o DecisionAgent.
    Se mock=True, retorna um agente de teste com lógica simulada.
    """

    if mock:
        class MockDecisionAgent:
            def invoke(self, inputs):
                data = inputs.get("input", {})
                
                # Extrai dados principais
                rules = data.get("rules", {})
                inventory = data.get("inventory", {})

                elegivel = rules.get("eligible", True)
                confianca = rules.get("confidence", 0.9)
                estoque_disponivel = inventory.get("available", True)

                # Pequena chance de encaminhar para revisão humana
                if random.random() < 0.2:
                    return {
                        "decision": "revisao_humana",
                        "action_payload": None,
                        "confidence": confianca,
                        "explanation": "Sistema incerto — análise humana necessária",
                        "audit_refs": ["HUMAN-REVIEW-RANDOM"]
                    }

                # Lógica principal de decisão
                if not elegivel or confianca < DECISION_POLICY["low_confidence_threshold"]:
                    decision = "escalado"
                    explanation = "Produto inelegível ou confiança baixa"
                    action_payload = None
                elif elegivel and confianca >= DECISION_POLICY["auto_approve_threshold"]:
                    if estoque_disponivel:
                        decision = "aprovado"
                        explanation = "Troca aprovada automaticamente"
                        action_payload = {"exchange_id": "MOCK-EXCHANGE-123"}
                    else:
                        decision = "proposta_credito"
                        explanation = "Produto elegível, mas sem estoque — sugerir crédito"
                        action_payload = {"exchange_id": "MOCK-EXCHANGE-123"}
                else:
                    decision = "aprovado_com_condicoes"
                    explanation = "Troca aprovada, mas requer observações adicionais"
                    action_payload = {"exchange_id": "MOCK-EXCHANGE-123"}

                return {
                    "decision": decision,
                    "action_payload": action_payload,
                    "confidence": confianca,
                    "explanation": explanation,
                    "audit_refs": ["LOG-DECISAO-AGENTE"]
                }

        return MockDecisionAgent()

    # Versão real com LLM
    llm = ChatOpenAI(model=model, temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", DECISION_PROMPT),
        ("user", "{input}")
    ])

    agent = create_openai_functions_agent(
        llm=llm,
        tools=[operations_create_exchange],
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=[operations_create_exchange],
        verbose=True
    )

    return agent_executor
