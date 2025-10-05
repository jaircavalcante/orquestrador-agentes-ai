# app/agents/rules_agent.py
import random
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

from app.tools.rules_store import lookup_rules_for_id_item_pedido


@tool
def rules_lookup(id_item_pedido: str) -> Dict:
    """Consulta as regras aplicáveis para um ID_ITEM_PEDIDO específico."""
    return lookup_rules_for_id_item_pedido(id_item_pedido)


RULES_PROMPT = """
Você é Rules Agent. Recebe ID_ITEM_PEDIDO, data, visão do estado do produto e resultado do OCR.
Use tool rules_lookup e avalie rule-by-rule se o caso passa. Retorne JSON:
{
  "id_item_pedido": "...",
  "checks": [ { "rule_id": "...", "pass": true/false, "evidence": "..." } ],
  "eligible": true|false,
  "confidence": 0.0-1.0,
  "citations": [...]
}
Retorne SOMENTE JSON.
"""

def build_rules_agent(model: str = "gpt-4o-mini", mock: bool = True):
    
    """
    Se o Mock estiver true, deve retornar os dados apenas para iteração do fluxo.
    """

    if(mock):
        class MockRulesAgent:
            def invoke(self, inputs):
                id_item_pedido = inputs.get("input", "ID_ITEM_PEDIDO-MOCK")
                return {
                    "id_item_pedido": id_item_pedido,
                    "checks": [
                        {"rule_id": "R1", "pass": True, "evidence": "Produto em bom estado"},
                        {"rule_id": "R2", "pass": False, "evidence": "Prazo de garantia expirado"}
                    ],
                    "eligible": random.choice([True, False]),
                    "confidence": round(random.uniform(0.7, 0.99), 2),
                    "citations": ["Manual interno v2", "Política de Garantia 2025"]
                }
        return MockRulesAgent()
    
    # criando o agente
    llm = ChatOpenAI(model=model, temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", RULES_PROMPT),
        ("user", "{input}")
    ])

    agent = create_openai_functions_agent(
        llm=llm,
        tools=[rules_lookup],
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=[rules_lookup],
        verbose=True
    )

    return agent_executor