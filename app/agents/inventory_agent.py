# app/agents/inventory_agent.py
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from app.tools.inventory_api import check_and_reserve


@tool
def check_reserve(id_item_pedido: str, qty: int, idempotency_key: str) -> Dict:
    """Verifica e reserva estoque do ID_ITEM_PEDIDO solicitado."""
    return check_and_reserve(id_item_pedido, qty, idempotency_key)


INVENTORY_PROMPT = """
Você é Inventory Agent. Receba ID_ITEM_PEDIDO e quantidade, chame check_reserve e retorne JSON com:
{ "id_item_pedido":..., "available": bool, "reservation_id": "...", "confidence": 0.0-1.0 }
Retorne SOMENTE JSON.
"""


def build_inventory_agent(model: str = "gpt-4o-mini", mock: bool = True):
    
    """
    Se o Mock estiver true, deve retornar os dados apenas para iteração do fluxo.
    """

    if(mock):
        class MockInventoryAgent:
            def invoke(self, inputs):
                data = inputs.get("input", {})
                id_item_pedido = data.get("id_item_pedido", "ID_ITEM_PEDIDO-MOCK")
                qty = data.get("qty", 1)
                return {
                    "id_item_pedido": id_item_pedido,
                    "available": True,  # simula que sempre tem estoque
                    "reservation_id": f"RES-{id_item_pedido}-MOCK",
                    "qty": qty,
                    "confidence": 0.95
                }
            
        return MockInventoryAgent()

    # Executando processo sem Mock 
    llm = ChatOpenAI(model=model, temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", INVENTORY_PROMPT),
        ("user", "{input}")
    ])

    agent = create_openai_functions_agent(
        llm=llm,
        tools=[check_reserve],
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=[check_reserve],
        verbose=True
    )

    return agent_executor