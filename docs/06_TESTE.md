# 06_TESTE.md — Evidências de Validação

**Projeto**: Roadmap-Estudos
**Data**: 2026-06-08
**Ambiente**: Python 3.11+, pytest, Linux

---

## 1. Resultados dos Testes

### 1.1 Resumo Executivo

| Métrica | Valor | Status |
|---------|-------|--------|
| Total de testes | 68 | — |
| Testes passando | 67 | ✅ |
| Testes falhando | 1 | ⚠️ |
| Taxa de sucesso | 98.5% | — |

### 1.2 Detalhamento por Suite

| Suite | Testes | Passaram | Falharam |
|-------|--------|----------|----------|
| `tests/unit/test_dsl_engine.py` | 57 | 57 | 0 |
| `tests/unit/test_diagnosis.py` | 5 | 5 | 0 |
| `tests/integration/test_api.py` | 6 | 5 | 1 |

### 1.3 Teste com Falha

**`test_diagnose_missing_api_key`** (`tests/integration/test_api.py:77`)

```
ImportError: openai package not installed
```

**Causa**: O pacote `openai` não está instalado no ambiente de teste. O `DiagnosisService.get_client()` verifica `if OpenAI is None` e lança `ImportError` antes de checar a API key.

**Impacto**: Baixo — teste de integração depende de pacote externo. O teste unitário `test_diagnosis.py` valida a mesma lógica via mock.

**Correção recomendada**: Mockar `openai.OpenAI` no teste ou instalar `openai` como dependência de dev.

---

## 2. Cobertura de Código

### 2.1 Cobertura Geral

| Métrica | Valor | Meta |
|---------|-------|------|
| **Cobertura total** | **38.45%** | ≥85% |
| Statements | 658 total, 253 executados | — |
| Status | **ABAIXO DA META** | ⚠️ |

### 2.2 Cobertura por Módulo

| Módulo | Stmts | Miss | Cobertura | Status |
|--------|-------|------|-----------|--------|
| `backend/core/config.py` | 18 | 1 | **94%** | ✅ |
| `backend/services/diagnosis/diagnosis_service.py` | 35 | 0 | **100%** | ✅ |
| `backend/services/dsl/engine.py` | 227 | 26 | **89%** | ✅ |
| `backend/models/__init__.py` | 5 | 5 | 0% | ❌ |
| `backend/models/diagnosis.py` | 8 | 8 | 0% | ❌ |
| `backend/models/lesson.py` | 9 | 9 | 0% | ❌ |
| `backend/models/quiz.py` | 18 | 18 | 0% | ❌ |
| `backend/models/roadmap.py` | 8 | 8 | 0% | ❌ |
| `backend/api/routes.py` | 83 | 83 | 0% | ❌ (deprecated) |
| `backend/api/routes_fastapi.py` | 85 | 85 | 0% | ❌ |
| `backend/main.py` | 25 | 25 | 0% | ❌ |
| `backend/services/ai_content/lesson_generator.py` | 25 | 25 | 0% | ❌ |
| `backend/services/ai_content/roadmap_generator.py` | 53 | 53 | 0% | ❌ |
| `backend/services/quiz/quiz_service.py` | 59 | 59 | 0% | ❌ |

### 2.3 Análise de Lacunas

**Módulos sem cobertura (0%)**: Todos os módulos que dependem de `openai` ou FastAPI não são testados diretamente. A estratégia atual é:
- **Services com IA**: Testados via mock em `test_diagnosis.py` e `test_api.py` (parcial).
- **Pydantic models**: Não requerem testes unitários (validação automática do Pydantic).
- **Rotas FastAPI**: Não testadas com `TestClient` (falta `httpx` ou `pytest-httpx`).

**Ações para atingir 85%**:
1. Adicionar testes de rotas FastAPI com `TestClient`.
2. Mockar services de IA nos testes de integração.
3. Cobrir `lesson_generator.py` e `roadmap_generator.py` via mocks.

---

## 3. Issues Encontrados e Resolvidos

### 3.1 Issues Ativos

| ID | Severidade | Descrição | Status |
|----|-----------|-----------|--------|
| ISSUE-001 | Baixa | `openai` não instalado em ambiente de teste | Aberto |
| ISSUE-002 | Média | Cobertura abaixo de 85% (38.45%) | Aberto |

### 3.2 Issues Resolvidos (Histórico)

| ID | Descrição | Versão | Solução |
|----|-----------|--------|---------|
| v3.0.0 | Migração http.server → FastAPI | v3.0.0 | Reescrita completa de rotas |
| v3.0.1 | E402 imports em main.py | v3.0.1 | `noqa: E402` + imports no topo |
| v2.3.1 | Endpoints de quiz incorretos | v2.3.1 | Padronização REST no frontend |
| v2.3.1 | Nomes de arquivo com acentos | v2.3.1 | `unicodedata.normalize()` |
| v2.2.0 | Path traversal em load_roadmap | v2.2.0 | `os.path.basename` + `realpath` |
| v2.2.0 | XSS via innerHTML | v2.2.0 | Reescrita com `createElement` |
| v2.2.0 | CORS aberto | v2.2.0 | Restrito a `localhost:8000` |

### 3.3 Lições Aprendidas

1. **Convenções de rotas**: Manter REST consistente (`/api/recurso/acao`) evita desalinhamento frontend/backend.
2. **Normalização de arquivos**: Sempre normalizar para ASCII ao salvar — evita problemas de URL encoding.
3. **Validação automática**: Script `validate_content_format.py` previne bugs silenciosos.
4. **API key lazy**: Ler `os.getenv()` em tempo de execução, não cachear em módulo.

---

## 4. Comandos de Validação

```bash
# Rodar todos os testes
python3 -m pytest tests/ -v

# Rodar com cobertura
python3 -m pytest tests/ --cov=backend --cov-report=term-missing

# Rodar apenas unitários
python3 -m pytest tests/unit/ -v

# Rodar apenas integração
python3 -m pytest tests/integration/ -v

# Harness de validação
python3 harness.py
```
