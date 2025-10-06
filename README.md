# 🤖 Orquestrador de Agentes AI

Este projeto implementa um **orquestrador de agentes inteligentes** que integra diversos módulos para análise e decisão automática de solicitações de troca/exchange, utilizando:

- **LLMs** (Large Language Models)  
- **OCR e visão computacional**  
- **Regras de negócio**  
- **Mock de agentes** para testes offline

O fluxo principal envolve os seguintes agentes:

| Agente | Função |
|--------|--------|
| **DocumentAgent** | Analisa dados do pedido e do portal. |
| **OCRVisionAgent** | Processa imagens de invoice e produto para extrair informações e classificar danos. |
| **RulesAgent** | Aplica regras de negócio por Item do pedido. |
| **InventoryAgent** | Verifica disponibilidade de estoque e realiza reservas. |
| **DecisionAgent** | Consolida saídas dos agentes e aplica políticas de decisão (aprovação automática, proposta de crédito, escalonamento ou revisão humana). |

---

## ⚙️ Pré-requisitos

- Python >= 3.10  
- pip  
- Virtualenv (recomendado)

---

## 🛠️ Instalação

1. **Clone o repositório:**

```bash
git clone <URL_DO_REPOSITORIO>
cd <PASTA_DO_PROJETO>
```

2. **Crie um ambiente virtual (opcional, mas recomendado):**

```bash
python -m venv venv
```

3. **Ative o ambiente virtual:**

- **Linux / macOS:**
```bash
source venv/bin/activate
```
- **Windows:**
```bash
venv\Scripts\activate
```

4. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

5. **Verifique a instalação:**

```bash
pip list
```

---

## 🚀 Uso

Exemplo de execução do orquestrador com um `protocol_id`:

```python
from app.orchestrator import orchestrate

protocol_id = "PROTO-20251003-0001"
resultado = orchestrate(protocol_id)

print("DECISÃO FINAL:", resultado["decision"])
```

**Fluxo completo:**

1. Fetch de dados do portal (DocumentAgent).  
2. Extração de informações via OCR e visão computacional (OCRVisionAgent).  
3. Aplicação de regras do negócio (RulesAgent).  
4. Checagem e reserva de estoque (InventoryAgent).  
5. Consolidação da decisão e possível ação (DecisionAgent).  
6. Revisão humana caso necessário.  

---

## 📂 Estrutura do Projeto

```
app/
├── agents/             # Agentes de AI (Document, OCR/Vision, Rules, Inventory, Decision)
├── tools/              # Ferramentas de suporte (APIs, OCR, Inventário, Portal)
├── orchestrator.py     # Fluxo principal de orquestração
├── main.py             # Script de execução
requirements.txt        # Dependências do projeto
README.md               # Este arquivo
```

---

## Fluxograma Sequencial

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant DocumentAgent
    participant OCRVisionAgent
    participant RulesAgent
    participant InventoryAgent
    participant DecisionAgent
    participant HumanReviewer

    User->>Orchestrator: solicita análise do protocol_id
    Orchestrator->>DocumentAgent: invoke(protocol_id)
    DocumentAgent-->>Orchestrator: dados do portal

    Orchestrator->>OCRVisionAgent: invoke(caminhos das imagens)
    OCRVisionAgent-->>Orchestrator: OCR + visão do produto

    Orchestrator->>RulesAgent: invoke(identificador + OCR)
    RulesAgent-->>Orchestrator: checagem de regras, elegibilidade

    Orchestrator->>InventoryAgent: invoke(identificador + idempotency_key)
    InventoryAgent-->>Orchestrator: disponibilidade/reserva do estoque

    Orchestrator->>DecisionAgent: invoke(todos outputs + idempotency_key)
    DecisionAgent-->>Orchestrator: decisão preliminar + action_payload

    alt Decision requires human review
        Orchestrator->>HumanReviewer: enviar dados + recomendação
        HumanReviewer-->>Orchestrator: decisão final
    end

    Orchestrator-->>User: resultado final + auditoria
```

## Fluxograma Completo

```mermaid
flowchart TD

%% Camada de Entrada
A[Cliente solicita troca via portal/app] --> B[Orquestrador ReAct - LangGraph]

%% Camada de Agentes Inteligentes
B --> C[DocumentAgent 📄 Extrai dados e fotos do pedido]
C --> D[RulesAgent ⚖️ Valida elegibilidade nas políticas internas]
D --> E[InventoryAgent 📦 Verifica estoque e disponibilidade]
E --> F[DecisionAgent 🧠 Integra resultados e define ação]

%% Caminhos de Decisão
F -->|✅ Cenário OK: elegível e estoque disponível| G[Auto-aprovação - approved]
F -->|♻️ Elegível, mas sem estoque| H[Propor crédito ao cliente - propose_credit]
F -->|⚠️ Baixa confiança ou regra ambígua| I[Escalonar para humano - human_review]
F -->|❌ Não elegível ou inconsistências graves| J[Recusar troca - escalate]

%% Camada de Ação
G --> K[Criação de protocolo no ERP]
H --> L[Emissão de vale-compra via API de crédito]
I --> M[Analista humano revisa caso e confirma ou recusa]
J --> N[Comunica recusa ao cliente]

%% Camada de Persistência e Auditoria
F --> O[(Base de auditoria 🗃️ Registra decisão, confiança e evidências)]
M --> O

%% Camada de Integração e Dados
subgraph APIs e Bases
    P1[API Catálogo de Produtos]
    P2[API de Estoque]
    P3[API de Crédito]
    DB1[(Banco ERP)]
    DB2[(Base de Logs e Auditoria)]
end

%% Relações com APIs e Banco
InventoryAgent -.-> P1
InventoryAgent -.-> P2
H -.-> P3
K -.-> DB1
O -.-> DB2

%% Camada de Suporte Humano
subgraph Revisão Humana
    M
end

%% Estilo visual
classDef entrada fill:#FFFDE7,stroke:#FDD835,stroke-width:1px;
classDef agent fill:#E3F2FD,stroke:#1E88E5,stroke-width:1px;
classDef decision fill:#FFF3E0,stroke:#FB8C00,stroke-width:1px;
classDef action fill:#E8F5E9,stroke:#43A047,stroke-width:1px;
classDef human fill:#FFEBEE,stroke:#C62828,stroke-width:1px;
classDef infra fill:#E0F7FA,stroke:#00838F,stroke-width:1px;

class A entrada;
class B,C,D,E,F agent;
class F decision;
class G,H,J,K,L,O action;
class I,M human;
class P1,P2,P3,DB1,DB2 infra;

```

## Detalhe do Agente Decisor

```mermaid
flowchart TD
    A[Início: Recebe outputs dos agentes] --> B{Elegível?}
    
    B -- Não --> C[Escalado: produto inelegível ou confiança baixa]
    B -- Sim --> D{Confiança >= 0.9?}
    
    D -- Sim --> E{Estoque disponível?}
    E -- Sim --> F[Aprovado automaticamente<br>action_payload gerado]
    E -- Não --> G[Proposta de crédito<br>action_payload gerado]
    
    D -- Não --> H[Aprovado com condições<br>action_payload gerado]
    
    %% Revisão humana
    I[Pequena chance aleatória] --> J[Revisão humana necessária]
    
    %% Conecta revisão humana ao fluxo principal
    J --> K[Fim: decisão retornada]
    C --> K
    F --> K
    G --> K
    H --> K

```

-----

## 💡 Notas

- É possível ativar **mocks** para todos os agentes, permitindo testes sem LLM ou APIs externas.  
- As decisões seguem **políticas configuráveis**, incluindo thresholds de confiança e elegibilidade.  
- O projeto suporta **escalonamento e revisão humana** para casos incertos.  

--

