# Design Document: Roadmap-Estudos

## Overview
Plataforma de estudos personalizada que gera roadmaps e lições via IA (OpenRouter), com quizzes interativos, diagnóstico de conhecimento e visualização em fluxograma expansível.

## Princípios de Engenharia

| Princípio | Aplicação neste projeto |
|-----------|------------------------|
| **KISS** | Persistência em arquivos JSON/Markdown (sem banco de dados). Frontend single-page sem frameworks. |
| **DRY** | Serviços compartilham cliente OpenAI via funções `get_client()` em cada módulo. Config centralizada em `backend/core/config.py`. |
| **SRP** | Cada serviço tem responsabilidade única: `lesson_generator` → lições, `quiz_service` → quizzes, `diagnosis_service` → diagnóstico, `roadmap_generator` → roadmaps. |
| **Immutable Artifacts** | `harness.py`, `guard_harness.py` e `.harness.hash` são protegidos por SHA256 + chattr +i. Nenhum agente pode modificá-los. |

## Architecture

### Estrutura de Diretórios
```
roadmap-estudos/
├── backend/                       # Servidor FastAPI
│   ├── main.py                    # Entry point uvicorn
│   ├── core/config.py             # Config centralizada (dirs, API key)
│   ├── models/                    # Pydantic v2 models
│   │   ├── lesson.py, quiz.py, roadmap.py, diagnosis.py
│   ├── api/
│   │   ├── routes.py              # Rotas legado (http.server)
│   │   └── routes_fastapi.py      # Rotas ativas (FastAPI APIRouter)
│   └── services/
│       ├── ai_content/            # Geração de roadmaps e lições
│       │   ├── roadmap_generator.py
│       │   └── lesson_generator.py
│       ├── diagnosis/             # Diagnóstico de conhecimento
│       ├── quiz/                  # Geração e avaliação de quizzes
│       └── dsl/                   # Motor DSL (stub)
├── frontend/public/               # SPA (HTML, CSS, JS puros)
├── data/                          # Roadmaps JSON
├── licoes/                        # Lições Markdown + quizzes embutidos
├── scripts/                       # Utilitários (validação, migração, guard)
├── tests/                         # Testes pytest
├── harness.py                     # Orquestrador de validação
└── .harness.hash                  # Hashes de arquivos protegidos
```

### Camadas de Validação
1. **Entrada da API**: Pydantic v2 models validam tipos e formatos automaticamente.
2. **Serviço**: Funções validam estado antes de chamar a OpenRouter (ex: API key presente, arquivos existem).
3. **Persistência**: Script `validate_content_format.py` valida naming, estrutura JSON e formato de quiz.
4. **Pipeline**: `harness.py` agrega lint, type check, testes, segurança, estrutura e conteúdo.

### Arquivos Protegidos
| Arquivo | Proteção | Quem pode alterar |
|---------|----------|-------------------|
| `harness.py` | SHA256 + chattr +i + git status | Mantenedor humano |
| `scripts/guard_harness.py` | SHA256 + chattr +i + git status | Mantenedor humano |
| `.harness.hash` | git status | Mantenedor humano (via --seal) |

### Gestão de Credenciais
- OpenRouter API key em `.env` (ignorado pelo git).
- Carregada via `os.environ.setdefault()` no módulo `config.py`.
- Exportada como `OPENROUTER_API_KEY` para uso nos serviços.
- `check_api_key()` valida presença antes de chamadas à API.

## Components and Interfaces

### Component 1: FastAPI Router
**Responsabilidade**: Expor endpoints REST para frontend e testes.
**Interface pública**: `APIRouter` com 9 endpoints (`/api/roadmaps`, `/api/roadmap/{id}`, `/api/dep-map`, `/api/generate-lesson`, `/api/generate-roadmap`, `/api/quiz/generate`, `/api/quiz/evaluate`, `/api/diagnose`, `/licoes/{file}`).
**Erros tratados**: HTTP 404 (arquivo não encontrado), 422 (validação Pydantic), 500 (erro interno/API).

### Component 2: Roadmap Generator
**Responsabilidade**: Gerar roadmaps de estudo via OpenRouter API e persistir em JSON.
**Interface pública**: `gerar_roadmap_ia(tema: str) -> dict`, `salvar_roadmap(roadmap: dict) -> str`.
**Erros tratados**: API key ausente, timeout da API, JSON inválido retornado pela IA.

### Component 3: Lesson Generator
**Responsabilidade**: Gerar lições Markdown com quizzes embutidos via OpenRouter API.
**Interface pública**: `gerar_conteudo_ia(topico: str, node_data: dict) -> str`, `processar_node(roadmap_id: str, node_id: str) -> str`.
**Erros tratados**: API key ausente, node não encontrado no roadmap, falha na API.

### Component 4: Quiz Service
**Responsabilidade**: Gerar e avaliar quizzes de múltipla escolha sobre lições.
**Interface pública**: `generate_quiz(lesson_content: str) -> dict`, `evaluate_quiz(quiz_data: dict, answers: list) -> dict`.
**Erros tratados**: Lição não encontrada, quiz mal formatado, API key ausente.

### Component 5: Diagnosis Service
**Responsabilidade**: Analisar gaps de conhecimento usando o mapa de dependências.
**Interface pública**: `diagnose(area: str, knowledge: str) -> dict`.
**Erros tratados**: API key ausente, dep_map.json vazio.

### Component 6: DSL Engine (stub)
**Responsabilidade**: Executar scripts DSL para fluxos de aprendizado customizados.
**Interface pública**: `execute(dsl: str) -> dict`, `validate(dsl: str) -> dict`.
**Erros tratados**: Sintaxe inválida, comandos desconhecidos.

### Component 7: Validation Harness
**Responsabilidade**: Agregar e executar todas as validações do projeto.
**Interface pública**: `python harness.py` (modos: json, lint, type, test, audit, security, structure, content).
**Erros tratados**: Exit 0 (healthy), Exit 1 (falha de validação), Exit 2 (violação de integridade).

## Error Handling Strategy

| Cenário | Componente | Resposta |
|---------|------------|----------|
| API key ausente | Todos os serviços IA | `PermissionError("API key não configurada")` |
| Arquivo não encontrado | Routers, serviços | HTTP 404 + mensagem descritiva |
| Falha OpenRouter API | Serviços IA | HTTP 500 + mensagem original do erro |
| Validação Pydantic | FastAPI Router | HTTP 422 + detalhes dos campos inválidos |
| Path traversal | Lesson endpoint | Sanitização de caminho, HTTP 400 |
| Violação de integridade | Guard Harness | Exit 2 + relatório de violações |

## Testing Strategy

### Pirâmide de Testes

| Tipo | Cobertura Alvo | Ferramentas |
|------|---------------|-------------|
| Unitário | Serviços de diagnóstico, quiz, DSL | pytest, pytest-asyncio |
| Integração | Fluxos de API (mocks OpenAI) | pytest, httpx, pytest-asyncio |

### Critérios de Aceitação
- [ ] `python harness.py` retorna status "healthy" (0 erros)
- [ ] Nenhuma credencial hardcodada
- [ ] Todos os arquivos protegidos com hash válido
- [ ] Docstrings em todas as funções/classes públicas
- [ ] Lições com quizzes embutidos (mínimo 3 perguntas)
