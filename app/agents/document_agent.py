import json
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

from app.tools.portal_api import dados_protocolo


# Tool no formato novo
@tool
def fetch_protocol(protocol_id: str) -> Dict:
    """Busca informações do protocolo no portal"""
    return dados_protocolo(protocol_id)


# Prompt / instruções do agent
DOCUMENT_PROMPT = """
Você é o Document Analyzer. Receberá dados do portal (via tool fetch_protocol).
Compare dados do pedido com os dados da solicitação e retorne um JSON com:
- customer_match: bool
- order_match: bool
- extracted_order: {...}
- issues: []
- confidence: float
Retorne SOMENTE JSON.
"""

def build_document_agent(model: str = "gpt-4o-mini", mock: bool = True):
    
    """
    Se o Mock estiver true, deve retornar os dados apenas para iteração do fluxo.
    """

    if(mock):
        class MockAgent:

            """Mock simplificado para testes e desenvolvimento local."""

            def invoke(self, inputs):
                protocol_id = inputs.get("input", "")
                return {
                    "output": json.dumps({
                        "customer_match": True,
                        "order_match": True,
                        "extracted_order": {"protocol_id": protocol_id},
                        "issues": [],
                        "confidence": 0.95
                    })
                }
        
        return MockAgent()

    # Modelo
    llm = ChatOpenAI(model=model, temperature=0)

    # # Monta o prompt no formato novo
    prompt = ChatPromptTemplate.from_messages([
        ("system", DOCUMENT_PROMPT),
        ("user", "{input}")  # entrada dinâmica
    ])

    # criando o agente
    agent = create_openai_functions_agent(
        llm=llm,
        tools=[
            fetch_protocol
        ],
        prompt=prompt
    )

    #Executor que roda o agente
    agent_executor = AgentExecutor(
        agent=agent,
        tools=[
            fetch_protocol
        ], 
        verbose=True,
    )

    return agent_executor