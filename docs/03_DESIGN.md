# 03_DESIGN.md — Especificação de Design Técnico

**Projeto**: Roadmap-Estudos
**Data**: 2026-06-08

---

## 1. Arquitetura Geral

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Browser)                │
│  HTML5 + Vanilla CSS + JavaScript (ES6+ global)     │
│  Marked.js (Markdown rendering)                     │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (fetch API)
                       ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Server (uvicorn)                │
│  backend/main.py                                    │
│  ├── Middleware: CORS, Static Files                 │
│  ├── Lifespan: criar dirs data/ e licoes/          │
│  └── Router: backend/api/routes_fastapi.py         │
└──────┬──────────────┬──────────────┬───────────────┘
       │              │              │
       ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────────┐
│  Pydantic  │ │  Services  │ │  OpenRouter    │
│  Models    │ │  (lógica)  │ │  API (IA)      │
│  /models/  │ │ /services/ │ │  openai SDK    │
└────────────┘ └────────────┘ └────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
┌────────────┐ ┌────────────┐ ┌────────────────┐
│  data/     │ │  licoes/   │ │  frontend/     │
│  JSON      │ │  Markdown  │ │  public/       │
│  roadmaps  │ │  lições    │ │  estáticos     │
└────────────┘ └────────────┘ └────────────────┘
```

### 1.1 Stack Técnica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend | FastAPI | ≥0.111.0 |
| ASGI Server | uvicorn | ≥0.30.0 |
| Validação | Pydantic v2 | ≥2.0.0 |
| IA Client | openai SDK | via OpenRouter |
| Frontend | HTML5, CSS3, JS ES6+ | — |
| Markdown | Marked.js | via CDN |

### 1.2 Padrões de Arquitetura
- **Async/Await**: Todos os endpoints FastAPI são `async def` para não bloquear I/O.
- **Dependency Injection**: FastAPI `Depends()` para services quando necessário.
- **Separation of Concerns**: Models → Services → Routes (camadas bem definidas).
- **File-based Persistence**: JSON e Markdown; sem banco de dados.

---

## 2. Estrutura de Diretórios — backend/

```
backend/
├── __init__.py
├── main.py                    # Entry point FastAPI + uvicorn
├── core/
│   ├── __init__.py
│   └── config.py              # Configurações, paths, API key
├── api/
│   ├── __init__.py
│   ├── routes.py              # Rotas legado (http.server) — deprecated
│   └── routes_fastapi.py      # Rotas FastAPI (ativas)
├── models/
│   ├── __init__.py
│   ├── lesson.py              # GenerateLessonRequest/Response
│   ├── quiz.py                # Generate/EvaluateQuizRequest/Response
│   ├── roadmap.py             # CreateRoadmapRequest/Response
│   └── diagnosis.py           # DiagnoseRequest/Response
└── services/
    ├── __init__.py
    ├── ai_content/
    │   ├── lesson_generator.py    # Geração de lições via IA
    │   └── roadmap_generator.py   # Geração de roadmaps via IA
    ├── quiz/
    │   └── quiz_service.py        # Geração e avaliação de quizzes
    ├── diagnosis/
    │   └── diagnosis_service.py   # Diagnóstico de gaps
    └── dsl/
        └── dsl_engine.py          # Motor DSL (análise de estrutura)
```

### 2.1 Módulos Principais

#### `main.py`
- Cria instância `FastAPI` com lifespan para inicializar diretórios.
- Configura CORS middleware (`allow_origins=["*"]`).
- Inclui router de API e monta arquivos estáticos do frontend.

#### `core/config.py`
- Define `BASE_DIR`, `DATA_DIR`, `LICOES_DIR`, `FRONTEND_DIR`.
- Lê variáveis do `.env` manualmente (sem pydantic-settings ainda).
- Expõe `OPENROUTER_BASE_URL`, `OPENROUTER_API_KEY`, `get_api_key()`, `check_api_key()`.

#### `api/routes_fastapi.py`
- APIRouter com todos os endpoints REST.
- Delega lógica para services (`QuizService`, `DiagnosisService`, etc.).
- Validação automática via Pydantic models nos request bodies.

---

## 3. Modelos Pydantic

### 3.1 Lição (`models/lesson.py`)

```python
class GenerateLessonRequest(BaseModel):
    node_id: str          # ID único do nó (min_length=1)
    title: str            # Título do tópico (min_length=1)
    type: Literal["topic", "subtopic", "central"]  # Tipo do nó

class GenerateLessonResponse(BaseModel):
    status: str           # "success" | "error"
    node_id: str          # ID do nó processado
```

### 3.2 Quiz (`models/quiz.py`)

```python
class GenerateQuizRequest(BaseModel):
    node_id: str          # ID do nó
    title: str            # Título da lição

class GenerateQuizResponse(BaseModel):
    status: str
    quiz: list[dict] | None    # Lista de perguntas
    message: str | None        # Mensagem de erro

class EvaluateQuizRequest(BaseModel):
    node_id: str
    title: str
    quiz_data: list[dict]      # Perguntas geradas
    user_answers: dict[str, int]  # {índice_pergunta: opção_escolhida}

class EvaluateQuizResponse(BaseModel):
    status: str
    evaluation: dict | None    # Score, feedback, details
    message: str | None
```

### 3.3 Roadmap (`models/roadmap.py`)

```python
class CreateRoadmapRequest(BaseModel):
    tema: str                  # Tema do roadmap (min_length=1)

class CreateRoadmapResponse(BaseModel):
    status: str
    tema: str | None
    data: dict | None          # Dados do roadmap gerado
```

### 3.4 Diagnóstico (`models/diagnosis.py`)

```python
class DiagnoseRequest(BaseModel):
    topic: str                 # Tópico a diagnosticar
    user_answer: str           # Resposta do usuário

class DiagnoseResponse(BaseModel):
    status: str
    result: dict | None        # {status, message, tags, has_gap}
```

---

## 4. Endpoints da API

| Método | Rota | Modelo Request | Modelo Response | Descrição |
|--------|------|----------------|-----------------|-----------|
| `GET` | `/api/roadmaps` | — | `list[str]` | Lista roadmaps disponíveis |
| `GET` | `/api/roadmap/{id}` | — | `dict` | Carrega roadmap por ID |
| `GET` | `/api/dep-map` | — | `dict` | Mapa de dependências |
| `POST` | `/api/generate-lesson` | `GenerateLessonRequest` | `GenerateLessonResponse` | Gera lição via IA |
| `POST` | `/api/generate-roadmap` | `CreateRoadmapRequest` | `CreateRoadmapResponse` | Cria roadmap via IA |
| `POST` | `/api/quiz/generate` | `GenerateQuizRequest` | `GenerateQuizResponse` | Gera quiz via IA |
| `POST` | `/api/quiz/evaluate` | `EvaluateQuizRequest` | `EvaluateQuizResponse` | Avalia respostas do quiz |
| `POST` | `/api/diagnose` | `DiagnoseRequest` | `DiagnoseResponse` | Diagnostica gaps |
| `GET` | `/licoes/{file}` | — | `FileResponse` | Retorna lição Markdown |

### 4.1 Validação Automática
- FastAPI retorna **422 Unprocessable Entity** automaticamente para bodies inválidos.
- Pydantic valida `min_length`, tipos e literais sem código manual.

---

## 5. Fluxos Principais

### 5.1 Geração de Lições

```
Frontend → POST /api/generate-lesson {node_id, title, type}
    ↓
routes_fastapi.py → processar_node(node_id, title, type)
    ↓
lesson_generator.py → OpenRouter API (prompt com template)
    ↓
Salva em /licoes/{node_id}.md
    ↓
Retorna {status: "success", node_id}
```

### 5.2 Geração e Avaliação de Quizzes

```
Geração:
Frontend → POST /api/quiz/generate {node_id, title}
    ↓
QuizService.generate_quiz()
    → Lê lição de /licoes/{node_id}.md
    → Envia prompt para OpenRouter (4 perguntas múltipla escolha)
    → Parseia JSON da resposta
    ↓
Retorna {status, quiz: [perguntas]}

Avaliação:
Frontend → POST /api/quiz/evaluate {node_id, title, quiz_data, user_answers}
    ↓
QuizService.evaluate_quiz()
    → Compara respostas com gabarito
    → Envia para IA gerar feedback detalhado
    ↓
Retorna {status, evaluation: {score, passed, feedback, details}}
```

### 5.3 Diagnóstico de Conhecimento

```
Frontend → POST /api/diagnose {topic, user_answer}
    ↓
DiagnosisService.diagnose()
    → Lê dep_map.json para pré-requisitos
    → Envia resposta + pré-requisitos para IA
    → Analisa indicadores de gap ("falta", "não sabe", etc.)
    ↓
Retorna {status, result: {status: "hit"|"miss", message, tags, has_gap}}
```

### 5.4 Geração de Roadmap

```
Frontend → POST /api/generate-roadmap {tema}
    ↓
gerar_roadmap_ia(tema) → OpenRouter API
    → Prompt com estrutura v2.0 (subtopics aninhados)
    → Parseia JSON da resposta
    ↓
salvar_roadmap(tema, data)
    → Salva em /data/roadmap_{tema_normalizado}.json
    ↓
Retorna {status, tema, data}
```

---

## 6. Integração com OpenRouter API

### 6.1 Configuração
- **Base URL**: `https://openrouter.ai/api/v1`
- **Autenticação**: Bearer token via `OPENROUTER_API_KEY`
- **SDK**: Biblioteca `openai` (compatível com OpenRouter)
- **Modelo padrão**: `openrouter/auto` (roteamento automático)

### 6.2 Padrão de Uso

```python
from openai import OpenAI

client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

completion = client.chat.completions.create(
    model="openrouter/auto",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=800,
    temperature=0.7,
)
```

### 6.3 Otimizações de Custo
| Endpoint | max_tokens | temperatura | Justificativa |
|----------|-----------|-------------|---------------|
| Geração de lição | 1500 | 0.7 | Conteúdo focado e conciso |
| Geração de quiz | 800 | 0.7 | 4 perguntas objetivas |
| Avaliação de quiz | 400 | 0.5 | Feedback preciso |
| Diagnóstico | 150 | 0.7 | Resposta curta (max 100 palavras) |
| Geração de roadmap | 2000 | 0.7 | Estrutura JSON complexa |

### 6.4 Segurança
- **Prompt injection**: Prompts restritivos que bloqueiam manipulação.
- **Validação de resposta**: Parse de JSON com regex; fallback para erro.
- **API key**: Nunca em código; lida de `.env` ou variável de ambiente.
