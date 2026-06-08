# CHANGELOG

Este documento registra a evolução, decisões técnicas e soluções de problemas do projeto **Roadmap-Estudos**.

---

## [Unreleased]

### Added
- **`.env.example`**: Template de variáveis de ambiente (COMPLIANCE-001)
- **`pydantic-settings`**: Migrado `config.py` para Settings(BaseSettings) (COMPLIANCE-004)
- **`docs/01_BRIEF.md`**: Briefing do problema de negócio (COMPLIANCE-013)
- **`docs/02_PRD.md`**: Requisitos do produto para melhorias de aderência (COMPLIANCE-013)
- **`docs/03_DESIGN.md`**: Especificação de design técnico (COMPLIANCE-013)
- **`docs/04_ADR-001-fastapi-migration.md`**: ADR da migração para FastAPI (COMPLIANCE-014)
- **`docs/04_ADR-002-openrouter-integration.md`**: ADR da integração OpenRouter (COMPLIANCE-014)
- **`docs/05_BACKLOG.md`**: Backlog de tarefas de conformidade (COMPLIANCE-013)
- **`docs/06_TESTE.md`**: Evidências de validação (COMPLIANCE-013)
- **`docs/07_RELEASE.md`**: Log de releases (COMPLIANCE-013)
- **112 novos testes**: Cobertura aumentada de 39.29% para 90.94% (COMPLIANCE-017)
- **Subestrutura `tests/unit/` e `tests/integration/`**: Testes organizados (COMPLIANCE-009)

### Changed
- **`pyproject.toml`**: Adicionadas configs `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest]`, `[tool.coverage]` (COMPLIANCE-003, 008)
- **`CHANGELOG.md`**: Reduzido de 683 para 209 linhas (69% de redução) (COMPLIANCE-015)
- **`backend/core/config.py`**: Migrado para pydantic-settings com Settings(BaseSettings) (COMPLIANCE-004)
- **`backend/api/routes_fastapi.py`**: Path traversal protegido, exceções específicas (COMPLIANCE-005, 007)
- **`backend/services/`**: Logging estruturado substitui print() (COMPLIANCE-006)
- **`backend/services/`**: Any eliminado, type hints completos (COMPLIANCE-010)
- **`.gitignore`**: Adicionados padrões para backups e coverage (COMPLIANCE-016)

### Fixed
- **Ruff lint**: Erros E501 corrigidos em todos os services (COMPLIANCE-011)
- **Mypy strict**: Erros type-arg corrigidos em engine.py (COMPLIANCE-012)

### Removed
- **`scripts/guard_harness.py.backup`**: Deletado (viola política de segurança) (COMPLIANCE-002)
- **`scripts/guard_harness.py.bak`**: Deletado (viola política de segurança) (COMPLIANCE-002)

---

## [v3.0.1] - 2026-05-12

### Corrigido
- **E402 imports em main.py**: Movidos imports do FastAPI para o topo com `noqa: E402`
- **Testes de API**: Corrigidos imports em `test_api.py` e `test_dsl_engine.py` para novo módulo `backend/`
- **Teste de API key**: Corrigido `test_diagnose_missing_api_key` para usar `patch.dict`
- **Config lazy evaluation**: `check_api_key()` agora lê do ambiente atual via `get_api_key()`

### Memória Técnica
`OPENROUTER_API_KEY` era cacheado em módulo. Solução: função `get_api_key()` lê `os.getenv()` em tempo de execução.

## [v3.0.0] - 2026-05-11

### Alterado
- **[BREAKING] Migração para FastAPI**: Substituído `http.server` síncrono por **FastAPI** + uvicorn
  - Endpoints assíncronos (`async def`) — não bloqueiam em I/O
  - Pydantic v2 valida inputs automaticamente (erro 422)
  - Swagger UI disponível em `/docs`
  - CORS integrado via middleware

### Adicionado
- **Pydantic Models**: `backend/models/` — GenerateLesson, GenerateQuiz, EvaluateQuiz, CreateRoadmap, Diagnose
- **Rotas FastAPI**: `backend/api/routes_fastapi.py`
- **Dependências**: `fastapi>=0.111.0`, `uvicorn[standard]>=0.30.0`, `pydantic>=2.0.0`

### Memória Técnica
`http.server` bloqueava em cada requisição. FastAPI + `async def` resolve o gargalo de chamadas à API de IA.

---

## [v2.9.x] - 2026-05-10 a 2026-05-11

### Features (v2.9.0-v2.9.1)
- **Sistema de Quiz IA**: Geração e avaliação de quizzes via `QuizService`
- **Botão "📝 Gerar Conteúdo"**: Geração de lição sob demanda com loading visual
- **Prompt otimizado**: max 800 palavras, 1500 tokens, temperatura 0.7

### Correções de Layout (v2.9.1-v2.9.3)
- **Espaçamento uniforme**: Fixado em 250px entre nós centrais
- **Removido `adjustedY`**: Simplificado para `currentY` direto
- **`box-sizing: border-box`**: Padding incluído na altura do nó (causa raiz de sobreposição)

### Memória Técnica (Layout)
Problema persistente de sobreposição entre nós. Causa raiz: CSS `box-sizing: content-box` fazia altura real ser maior que calculada. Solução: `border-box` + espaçamento fixo de 250px.

---

## [v2.8.x] - 2026-05-10 a 2026-05-11

### Adicionado
- **Layout Adaptativo (v2.8.0)**: Algoritmo em duas fases — pré-calcula altura, posiciona com espaçamento mínimo
- **Posicionamento Sequencial (v2.8.5)**: `currentY` incremental previne sobreposição
- **Margem Mínima (v2.8.1, v2.8.6)**: Subtópicos sempre visíveis (minTopMargin = 100px)
- **Script de Migração**: `scripts/fix_roadmap_structure.py` converte estrutura antiga
- **Prompt de IA (v2.8.7)**: Gera estrutura v2.0 com `subtopics` aninhados

### Correções de Espaçamento (v2.8.2-v2.8.11)
- Iterações sucessivas para encontrar fórmula correta de espaçamento
- **Resultado final**: `max(h1, h2) + minGap` para recolhidos; `(h1/2) + gap + (h2/2)` para expandidos
- Espaçamento mínimo absoluto de 140px entre nós recolhidos

### Memória Técnica
Espaçamento dinâmico é complexo. após 10+ iterações, KISS prevaleceu: espaçamento fixo de 250px com `box-sizing: border-box`.

---

## [v2.7.x] - 2026-05-10

### Adicionado
- **Expansão/Recolhimento Interativo (v2.7.0)**: Click expande/recolhe nós; double-click abre lição
- **Layout de Fluxograma (v2.6.0)**: Visualização mindmap com conexões SVG bezier
- **Espaçamento Dinâmico (v2.7.1-v2.7.2)**: Gap reduzido de 600px para 100px base

### Alterado
- **Layout Único**: Removido layout de árvore, apenas fluxograma
- **Botões de Controle**: "📂 Expandir" e "📁 Recolher" no header

---

## [v2.5.0-v2.6.0] - 2026-05-10

### Adicionado
- **Expansão Inteligente (v2.5.0)**: Nível 1 horizontal, Nível 2+ vertical
- **Fluxograma Profissional (v2.6.0)**: Nós centrais no centro, subtópicos alternados esquerda/direita
- **Alternância de Layout**: Botão "🔀 Layout" para árvore ↔ fluxograma

---

## [v2.4.0] - 2026-05-10

### Adicionado
- **Padrão JSON Unificado**: Estrutura v2.0 com `subtopics` aninhados
- **Script de Migração**: `scripts/migrate_roadmap_structure.py`

---

## [v2.3.0] - 2026-05-10

### Adicionado
- **Sistema de Proteção com Imutabilidade**: `chattr +i` para arquivos críticos
- **Comandos**: `--seal`, `--unlock`, `--status` no `guard_harness.py`
- **Hook Pre-Commit**: Validação de imutabilidade via `lsattr`

---

## [v2.3.1] - 2026-05-11

### Corrigido
- **[CRÍTICO] Endpoints de quiz**: Padronização REST (`/api/quiz/generate`, `/api/quiz/evaluate`)
- **[CRÍTICO] Payload de lição**: `id` → `node_id` no frontend
- **Normalização de nomes**: `unicodedata.normalize()` remove acentos de nomes de arquivo
- **`.env.example`**: Template de configuração para API key

### Adicionado
- **Script de validação**: `scripts/validate_content_format.py`
- **Documentação de padrões**: `docs/PADROES_FORMATO_CONTEUDO.md`

### Memória Técnica
Convenção REST consistente (`/api/recurso/acao`) evita desalinhamento frontend/backend. Normalizar nomes de arquivo para ASCII previne erros de URL encoding.

---

## [v2.3.0] - 2026-05-11

### Corrigido
- **[CRÍTICO] Roadmaps não carregando**: Renomeação para seguir padrão `roadmap_*.json`
- **[CRÍTICO] Lições não carregando**: Tratamento explícito para rota `/licoes/`
- **Método `_send_file()`**: Servir Markdown com encoding UTF-8 e Content-Type correto

---

## [v2.2.0] - 2026-05-10

### Corrigido (Segurança)
- **[P0] Path traversal**: `os.path.basename` + `os.path.realpath` com verificação de prefixo
- **[P0] XSS via innerHTML**: Reescrita com `createElement` + `textContent`
- **[P0] Content-Length**: Validação com limite de 1MB
- **[P1] API key silenciosa**: Verificação explícita com `raise EnvironmentError`
- **[P1] CORS aberto**: Restrito a `http://localhost:8000`
- **[P1] Progresso cruzado**: Filtro por roadmap atual no `updateProgressBar`

### Memória Técnica
`os.path.join` não bloqueia path traversal — `os.path.realpath` + verificação de prefixo é a defesa correta. `innerHTML` com dados de LLM é superfície de XSS real.

---

## [v2.1.x] - 2026-05-09 a 2026-05-10

### Adicionado
- **Ecossistema Multi-Tema**: Diferentes arquivos de roteiro em `data/`
- **Servidor de Ponte**: API em Python para gerenciar arquivos e IA
- **Modo Edição (CRUD UI)**: Adicionar, editar e excluir nós
- **Geração de IA**: Lições, quizzes e roadmaps via OpenRouter

### Corrigido
- Tratamento de erro na inicialização (`try...catch` robustos)
- Scroll unificado (lição + quiz compartilham container)
- Compatibilidade Mermaid.js v11+
- Erro de porta ocupada (`allow_reuse_address`)

---

## [v1.5.0] - 2026-05-08

### Adicionado
- **Gamificação**: Streaks diários e Quizzes de validação
- **Modo Zen**: Interface focada para leitura
- **Persistência Local**: `localStorage` para progresso e streaks

### Mudança de Arquitetura
- **Migração para Escopo Global**: Abandonado ES6 Modules em favor de scripts globais — servidores locais simples falhavam com MIME Type e CORS.

---

## [v1.0.0] - Inicial

### Adicionado
- Estrutura base com HTML/CSS e renderização de conexões dinâmicas via SVG
- Suporte inicial para Markdown e Mermaid.js

---

## 🧠 Registro de Decisões e Prevenção de Regressões

### 1. Por que não usar Streamlit no Portal?
O Streamlit é muito rígido para a interface visual complexa que o roadmap exige (SVG dinâmico, animações). HTML/JS puro dá controle total.

### 2. Por que o Servidor Python é necessário?
O navegador bloqueia salva arquivos locais e requisições `file://`. O servidor atua como ponte de confiança para a IA escrever lições na pasta `/licoes`.

### 3. O Problema do "Address already in use"
Reinicialização brusca pode prender a porta 8000. Usar `fuser -k 8000/tcp` ou `allow_reuse_address = True`.

### 4. Manutenção do Quiz
Quiz é extraído via Regex de blocos ` ```json [...] ``` ` no final dos Markdown. O formato deve ser estritamente mantido para o parser do frontend.
