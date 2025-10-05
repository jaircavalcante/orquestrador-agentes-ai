# app/agents/ocr_vision_agent.py
from typing import Dict
from app.tools.ocr_extract_text import ocr_extract_text
from app.tools.vision_service import classify_damage
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

@tool
def run_ocr(image_path: str) -> Dict:
    """Extrai texto de uma imagem (OCR)."""
    return ocr_extract_text(image_path)


@tool
def run_vision(image_path: str) -> Dict:
    """Classifica danos em uma imagem."""
    return classify_damage(image_path)


OCR_VISION_PROMPT = """
Você é OCR/Vision Agent. Recebe caminhos das imagens (invoice, product).
Utilize tools run_ocr e run_vision e retorne JSON com:
{
  "ocr": {...},
  "vision": {...},
  "confidence": 0.0-1.0
}
Retorne SOMENTE JSON.
"""

def build_ocr_vision_agent(model: str = "gpt-4o-mini", mock: bool = True):
    
    """
    Se o Mock estiver true, deve retornar os dados apenas para iteração do fluxo.
    """

    if(mock):
        class MockOCRVisionAgent:
            def invoke(self, inputs):
                image_info = inputs.get("input", "mock_image.png")
                return {
                    "ocr": {"text": "Fatura #12345 - Valor: R$ 500,00"},
                    "vision": {"damage": "arranhão leve", "location": "lateral direita"},
                    "confidence": 0.92,
                    "source": image_info
                }
            
        return MockOCRVisionAgent()

    llm = ChatOpenAI(model=model, temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", OCR_VISION_PROMPT),
        ("user", "{input}")
    ])

    agent = create_openai_functions_agent(
        llm=llm,
        tools=[run_ocr, run_vision],
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=[run_ocr, run_vision],
        verbose=True
    )

    return agent_executor