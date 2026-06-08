# AGENTS.md

Este documento é a **fonte da verdade** para qualquer agente que colabore neste projeto. Leia-o integralmente antes de iniciar qualquer alteração.

---

## 🔗 Diretrizes & Padrões Globais

Este projeto integra o diretório centralizado de diretrizes do workspace: **`/home/lucinei/Projetos/.agents/`**

### Precedência de Regras
```
policies/ (Global - non-negotiable) > rules/ (Projeto) > standards/ (Fallback)
```

### Recursos Disponíveis

| Categoria | Caminho | Descrição |
|-----------|---------|-----------|
| **Políticas** | [`/.agents/policies/`](file:///home/lucinei/Projetos/.agents/policies/) | Regras de segurança, proteção de dados e controle de acesso (obrigatórias) |
| **Regras** | [`/.agents/rules/`](file:///home/lucinei/Projetos/.agents/rules/) | Padrões de codificação e workflow DSL |
| **Padrões** | [`/.agents/standards/`](file:///home/lucinei/Projetos/.agents/standards/) | Stack, qualidade, documentação e estrutura |
| **ADRs** | [`/.agents/adr/`](file:///home/lucinei/Projetos/.agents/adr/) | Decisões arquiteturais (core + domain) |
| **Templates** | [`/.agents/templates/`](file:///home/lucinei/Projetos/.agents/templates/) | Templates para briefings, PRDs, ADRs e CHANGELOGs |

### Políticas Mandatórias (Non-Negotiable)
- **[Segurança](file:///home/lucinei/Projetos/.agents/policies/security.md):** Deny list de comandos, anti-patterns proibidos e guardrails
- **[Proteção de Dados](file:///home/lucinei/Projetos/.agents/policies/data-protection.md):** Diretrizes PII e dados em logs
- **[Controle de Acesso](file:///home/lucinei/Projetos/.agents/policies/access-control.md):** Credenciais e secrets

### Padrões de Qualidade (Quality Gates)
Após qualquer alteração, o código deve passar nas 4 validações:
1. `python harness.py` — Validação do harness
2. `pytest --cov-fail-under=85` — Cobertura ≥ 85%
3. `ruff check && ruff format --check` — Lint e formatação
4. `mypy --strict` — Checagem de tipos

### ADRs Core (Obrigatórios)
- **[ADR-001](file:///home/lucinei/Projetos/.agents/adr/core/ADR-001-harness-validation.md):** Harness de Validação Unificado
- **[ADR-002](file:///home/lucinei/Projetos/.agents/adr/core/ADR-002-pydantic-settings.md):** Configurações via pydantic-settings
- **[ADR-003](file:///home/lucinei/Projetos/.agents/adr/core/ADR-003-fastapi-di.md):** FastAPI com DI via Depends
- **[ADR-004](file:///home/lucinei/Projetos/.agents/adr/core/ADR-004-process-standards.md):** Padrões de Processos (DoR, DoD, WIP Limits)

### ADRs de Domínio (Opcionais - aplicáveis a este projeto)
- **[ADR-005](file:///home/lucinei/Projetos/.agents/adr/domain/ADR-005-artifact-provenance.md):** Metadados de Proveniência em Artefatos de IA/ML
- **[ADR-007](file:///home/lucinei/Projetos/.agents/adr/domain/ADR-007-multi-provider-ia.md):** Arquitetura Multi-Provider para Modelos de IA

## 🛠️ Stack Técnica & Arquitetura
- **Backend**: Python 3.11+ com **FastAPI** (servidor assíncrono em `backend/main.py`)
- **Frontend**: HTML5, Vanilla CSS, JavaScript (ES6+ com **escopo global** para compatibilidade)
- **Validação**: Pydantic v2 para todos os endpoints
- **IA**: Integração via OpenRouter API
- **Persistência**: Arquivos JSON em `/data` e Markdown em `/licoes`

## 📁 Estrutura de Diretórios
```
roadmap-estudos/
├── backend/
│   ├── api/
│   │   ├── routes.py          # Rotas legado (http.server)
│   │   └── routes_fastapi.py  # Rotas FastAPI (novas)
│   ├── core/config.py         # Configurações
│   ├── models/                # Pydantic models (validação)
│   │   ├── lesson.py
│   │   ├── quiz.py
│   │   ├── roadmap.py
│   │   └── diagnosis.py
│   └── services/              # Lógica de negócio
│       ├── ai_content/        # Geração de roadmaps e lições
│       ├── diagnosis/         # Diagnóstico
│       ├── quiz/              # Quizzes
│       └── dsl/               # Motor DSL
frontend/public/assets/        # CSS, JS, assets
data/                         # Roadmaps JSON
licoes/                       # Lições Markdown
```

## 🔄 Workflow de Orquestração
Sempre que detectar uma nova funcionalidade, alteração estrutural ou bug, acione o protocolo de orquestração para garantir a sincronia entre Dados, IA e Interface:
👉 **[@skill/workflown-agents.md](./skill/workflown-agents.md)**

## 🚦 Verificação de Ambiente
- Servidor local: `http://localhost:8000`
- Start: `cd backend && python main.py` (ou `uvicorn backend.main:app --reload`)
- Testes: `pytest tests/`
- Lint: `ruff check . && ruff format .`
- Harness: `python harness.py`
- Teste rápido de API: `curl http://localhost:8000/api/roadmaps`
- API Docs: `http://localhost:8000/docs` (Swagger UI)

## 🐍 Boas Práticas Python
- **Tipagem**: Use *type hints* em todas as funções.
- **Validação**: Use Pydantic models em `backend/models/` para validar entradas de API.
- **Async**: Endpoints de IA devem ser `async def` para não bloquear.
- **Caminhos**: Utilize `os.path.join` e `BASE_DIR` para portabilidade.
- **Tratamento de Erros**: Try-except específicos com `HTTPException` no FastAPI.

## 📝 Fluxo de Evolução & Commits
Siga: **Modificação -> Registro no Changelog -> Commit**.

### Conventional Commits (PT-BR)
`[tipo]([escopo]): [descrição detalhada]`

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `chore`

Exemplo: `feat(api): migra endpoint de quiz para FastAPI com validação Pydantic`

## ⚠️ Notas de Atenção
- **Escopo JS**: Não converta o frontend para ES6 Modules (`import/export`).
- **Parser de Quiz**: O quiz é extraído via Regex de blocos ` ```json ` no final dos `.md`.
- **Porta 8000**: Se `Address already in use`, use `fuser -k 8000/tcp`.