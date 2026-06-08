# 05_BACKLOG.md

**Baseado em**: 02_PRD.md + Análise de Aderência
**Data**: 2026-06-08
**Autor**: Agente de IA

---

## Definition of Done

- [ ] Código commitado
- [ ] Teste unitário passou
- [ ] Teste manual passou
- [ ] Sem erros no console
- [ ] Documentado se necessário
- [ ] `python harness.py` retorna status healthy

---

## Fase 1 — CRÍTICO (Segurança & Config)

### [ ] TASK-001: Criar arquivo `.env.example`
**Descrição**: Criar template de variáveis de ambiente sem valores reais
**Arquivos**:
- `.env.example` (novo)

**Critério de Pronto**:
- Arquivo contém `OPENROUTER_API_KEY=your-key-here`
- Comentário explicativo sobre cada variável
- Commitado no repositório

**Dependência**: Nenhuma
**Estimativa**: 10min

---

### [ ] TASK-002: Remover backups proibidos
**Descrição**: Deletar arquivos `.bak` e `.backup` que violam política de segurança
**Arquivos**:
- `scripts/guard_harness.py.backup` (deletar)
- `scripts/guard_harness.py.bak` (deletar)

**Critério de Pronto**:
- `ls scripts/` não lista nenhum arquivo `.bak` ou `.backup`
- Deleções commitadas

**Dependência**: Nenhuma
**Estimativa**: 5min

---

### [ ] TASK-003: Configurar tools no pyproject.toml
**Descrição**: Adicionar seções `[tool.ruff]`, `[tool.mypy]` e `[tool.pytest.ini_options]` conforme standards/stack-defaults.md
**Arquivos**:
- `pyproject.toml`

**Critério de Pronto**:
- `[tool.ruff]` com `line-length = 100`, `target-version = "py311"` e selects
- `[tool.mypy]` com `strict = true`, `python_version = "3.11"`
- `[tool.pytest.ini_options]` com `asyncio_mode = "auto"` e `testpaths = ["tests"]`
- `ruff check .` roda com configuração definida

**Dependência**: Nenhuma
**Estimativa**: 30min

---

### [ ] TASK-004: Adicionar pydantic-settings
**Descrição**: Migrar `backend/core/config.py` para usar `pydantic-settings` em vez de parsing manual de `.env`
**Arquivos**:
- `pyproject.toml` (adicionar dependência)
- `backend/core/config.py` (criar classe Settings)

**Critério de Pronto**:
- `pydantic-settings>=2.0.0` em `dependencies` no pyproject.toml
- Classe `Settings(BaseSettings)` com campos tipados
- Variáveis obrigárias validadas na inicialização
- `get_api_key()` mantido para compatibilidade

**Dependência**: TASK-003
**Estimativa**: 1.5h

---

### [ ] TASK-005: Adicionar timeout em subprocessos
**Descrição**: Adicionar `timeout=5` em todas as chamadas `subprocess.run()` do guard_harness.py
**Arquivos**:
- `scripts/guard_harness.py`

**Critério de Pronto**:
- Todas as chamadas `subprocess.run()` possuem `timeout=5`
- `subprocess.TimeoutExpired` é capturada
- Mensagem de timeout clara é registrada

**Dependência**: Nenhuma
**Estimativa**: 45min

---

### [ ] TASK-006: Proteger rota de lições contra path traversal
**Descrição**: Validar que `lesson_file` não acessa diretórios fora de `LICOES_DIR`
**Arquivos**:
- `backend/api/routes_fastapi.py` (função `get_lesson`)

**Critério de Pronto**:
- `Path(LICOES_DIR / lesson_file).resolve()` está dentro de `LICOES_DIR.resolve()`
- Requisição com `../` retorna 403 ou 404
- Requisição válida retorna arquivo corretamente

**Dependência**: Nenhuma
**Estimativa**: 45min

---

### [ ] TASK-007: Proteger rotas de roadmap contra path traversal
**Descrição**: Sanitizar `roadmap_id` para conter apenas caracteres seguros
**Arquivos**:
- `backend/api/routes_fastapi.py` (função `load_roadmap`)

**Critério de Pronto**:
- `roadmap_id` validado com regex `^[a-z0-9_-]+$`
- ID com caracteres inválidos retorna 400
- ID válido carrega roadmap corretamente

**Dependência**: Nenhuma
**Estimativa**: 30min

---

### [ ] TASK-008: Substituir print() por logging
**Descrição**: Substituir `print()` por `logging` estruturado em todos os services
**Arquivos**:
- `backend/services/ai_content/lesson_generator.py`
- `backend/services/ai_content/roadmap_generator.py`
- `backend/services/quiz/quiz_service.py`
- `backend/services/diagnosis/diagnosis_service.py`

**Critério de Pronto**:
- `import logging` e `logger = logging.getLogger(__name__)` em cada módulo
- `print()` substituído por `logger.info()`, `logger.warning()` ou `logger.error()`
- Nenhum `print()` restante em `backend/services/`

**Dependência**: TASK-003
**Estimativa**: 1h

---

### [ ] TASK-009: Substituir except Exception genérico
**Descrição**: Capturar exceções específicas em vez de `except Exception` nos endpoints
**Arquivos**:
- `backend/api/routes_fastapi.py` (funções `generate_quiz`, `evaluate_quiz`)

**Critério de Pronto**:
- `FileNotFoundError` capturado para arquivo não encontrado
- `ValueError` capturado para dados inválidos
- `Exception` genérico removido ou substituído por tipos específicos

**Dependência**: Nenhuma
**Estimativa**: 45min

---

## Fase 2 — ALTO (Quality Gates)

### [ ] TASK-010: Configurar cobertura mínima
**Descrição**: Adicionar configuração de cobertura no pyproject.toml
**Arquivos**:
- `pyproject.toml`

**Critério de Pronto**:
- `[tool.coverage.run]` com `source = ["backend"]`
- `[tool.coverage.report]` com `fail_under = 85`
- `pytest --cov` falha se cobertura < 85%

**Dependência**: TASK-003
**Estimativa**: 15min

---

### [ ] TASK-011: Criar subestrutura de testes
**Descrição**: Criar diretórios `tests/unit/` e `tests/integration/` e mover testes
**Arquivos**:
- `tests/unit/` (novo)
- `tests/integration/` (novo)
- `tests/unit/test_diagnosis.py` (mover)
- `tests/unit/test_dsl_engine.py` (mover)
- `tests/integration/test_api.py` (mover)
- `tests/conftest.py` (manter na raiz)

**Critério de Pronto**:
- Diretórios criados com `__init__.py`
- Testes movidos e imports atualizados
- `pytest` encontra todos os testes
- `pytest --cov` calcula cobertura corretamente

**Dependência**: Nenhuma
**Estimativa**: 1h

---

### [ ] TASK-012: Eliminar uso de Any
**Descrição**: Tipar corretamente funções que usam `Any` nos services
**Arquivos**:
- `backend/services/ai_content/lesson_generator.py`
- `backend/services/ai_content/roadmap_generator.py`

**Critério de Pronto**:
- `Any` substituído por tipos específicos (`OpenAI`, `ChatCompletion`, etc.)
- Funções com type hints completos
- `mypy --strict` passa sem erros de tipo

**Dependência**: TASK-004
**Estimativa**: 1.5h

---

### [ ] TASK-013: Validar ruff check e format
**Descrição**: Rodar linting e corrigir todos os issues encontrados
**Arquivos**:
- Todos os `.py` do projeto

**Critério de Pronto**:
- `ruff check .` retorna 0 erros
- `ruff format --check .` retorna 0 divergências
- Código formatado conforme configuração

**Dependência**: TASK-003
**Estimativa**: 1h

---

### [ ] TASK-014: Validar mypy strict
**Descrição**: Rodar mypy e corrigir todos os erros de tipagem
**Arquivos**:
- Todos os `.py` do projeto

**Critério de Pronto**:
- `mypy --strict backend/` retorna 0 erros
- Todas as funções com type hints completos
- Sem uso de `Any`

**Dependência**: TASK-012
**Estimativa**: 30min

---

## Fase 3 — MÉDIO (Estrutura & Documentação)

### [ ] TASK-015: Criar 01_BRIEF.md
**Descrição**: Criar briefing do problema de negócio
**Arquivos**:
- `docs/01_BRIEF.md` (novo)

**Critério de Pronto**:
- Documento descreve o problema que o projeto resolve
- Contexto e restrições documentadas
- Stakeholders identificados

**Dependência**: Nenhuma
**Estimativa**: 1h

---

### [ ] TASK-016: Criar 03_DESIGN.md
**Descrição**: Criar especificação de design técnico
**Arquivos**:
- `docs/03_DESIGN.md` (novo)

**Critério de Pronto**:
- Diagrama de arquitetura
- Especificação de endpoints
- Modelos de dados
- Fluxos principais

**Dependência**: Nenhuma
**Estimativa**: 1.5h

---

### [ ] TASK-017: Criar ADRs locais
**Descrição**: Documentar decisões arquiteturais do projeto
**Arquivos**:
- `docs/04_ADR-001-fastapi-migration.md` (novo)
- `docs/04_ADR-002-openrouter-integration.md` (novo)

**Critério de Pronto**:
- Cada ADR contém: Contexto, Decisão, Consequências
- Pelo menos 2 ADRs documentados
- Formato compatível com template `.agents/templates/04_ADR.md.template`

**Dependência**: Nenhuma
**Estimativa**: 1.5h

---

### [ ] TASK-018: Criar 06_TESTE.md
**Descrição**: Documentar evidências e resultados de validação
**Arquivos**:
- `docs/06_TESTE.md` (novo)

**Critério de Pronto**:
- Resultados de testes documentados
- Cobertura de código reportada
- Issues encontrados e resolvidos

**Dependência**: TASK-011, TASK-013, TASK-014
**Estimativa**: 30min

---

### [ ] TASK-019: Criar 07_RELEASE.md
**Descrição**: Documentar log de releases e deploys
**Arquivos**:
- `docs/07_RELEASE.md` (novo)

**Critério de Pronto**:
- Versão atual documentada
- Histórico de releases
- Próximas versões planejadas

**Dependência**: Nenhuma
**Estimativa**: 30min

---

### [ ] TASK-020: Podar CHANGELOG.md
**Descrição**: Reduzir CHANGELOG.md de 683 para ≤500 linhas
**Arquivos**:
- `CHANGELOG.md`

**Critério de Pronto**:
- `wc -l CHANGELOG.md` ≤ 500
- Entradas dos últimos 6 meses mantidas detalhadamente
- Entradas antigas resumidas em 1-2 linhas
- Informações críticas preservadas

**Dependência**: Nenhuma
**Estimativa**: 1h

---

## Fase 4 — BAIXO (Limpeza & Validação)

### [ ] TASK-021: Atualizar .gitignore
**Descrição**: Adicionar padrões para backups e arquivos temporários
**Arquivos**:
- `.gitignore`

**Critério de Pronto**:
- `*.bak` adicionado
- `*.backup` adicionado
- `.coverage` adicionado
- Padrões testados com `git status`

**Dependência**: Nenhuma
**Estimativa**: 5min

---

### [ ] TASK-022: Validar cobertura ≥85%
**Descrição**: Rodar testes e garantir cobertura mínima
**Arquivos**:
- `tests/` (adicionar testes se necessário)

**Critério de Pronto**:
- `pytest --cov --cov-fail-under=85` passa
- Cobertura ≥ 85% reportada
- Testes adicionais criados se necessário

**Dependência**: TASK-010, TASK-011
**Estimativa**: 2h

---

### [ ] TASK-023: Rodar harness completo
**Descrição**: Executar `python harness.py` e garantir status healthy
**Arquivos**:
- Nenhum (validação)

**Critério de Pronto**:
- `python harness.py` retorna status "healthy"
- Todos os passos passam sem erros
- `python harness.py json` mostra status "healthy"

**Dependência**: Todas as fases anteriores
**Estimativa**: 30min

---

## Bugs / Melhorias

### [ ] BUG-001: CHANGELOG.md excede limite de 500 linhas
**Severidade**: Média
**Passos para reproduzir**:
1. Executar `wc -l CHANGELOG.md`
2. Verificar resultado: 683 linhas

**Comportamento esperado**: ≤500 linhas conforme documentation.md
**Comportamento atual**: 683 linhas

---

### [ ] BUG-002: Backups .bak/.backup no repositório
**Severidade**: Alta
**Passos para reproduzir**:
1. Executar `ls scripts/*.bak scripts/*.backup`

**Comportamento esperado**: Nenhum arquivo listado
**Comportamento atual**: `guard_harness.py.backup` e `guard_harness.py.bak` existem

---

### [ ] BUG-003: Ausência de .env.example
**Severidade**: Alta
**Passos para reproduzir**:
1. Verificar se `.env.example` existe

**Comportamento esperado**: Arquivo existe com variáveis documentadas
**Comportamento atual**: Arquivo não existe

---

### [ ] BUG-004: pydantic-settings ausente
**Severidade**: Média
**Passos para reproduzir**:
1. Executar `grep pydantic-settings pyproject.toml`

**Comportamento esperado**: Dependência listada
**Comportamento atual**: Não encontrada

---

## Notas

- **Prioridade**: Tasks são executadas na ordem das fases (1 → 2 → 3 → 4)
- **Dependências**: Devem ser respeitadas antes de iniciar task dependente
- **Uma task por commit**: Cada task deve resultar em um commit atômico
- **Validação obrigatória**: Rodar `python harness.py` antes de marcar como [x]
- **Escopo**: Tasks 015-020 (docs) e 021-023 (limpeza) podem ser paralelizadas com fases anteriores
