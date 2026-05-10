# Requirements: Test Coverage Plan

## Introduction

Este documento especifica os requisitos para implementar cobertura de testes de 85-90% em todos os módulos do projeto roadmap-estudos.

## Requirements

### 1. Cobertura por Módulo

| Módulo | Cobertura Atual | Cobertura Alvo | Gap |
|--------|-----------------|----------------|-----|
| `server.py` | 27% | 85% | +58% |
| `generate_roadmap.py` | 32% | 85% | +53% |
| `generate_lessons.py` | 32% | 85% | +53% |
| `src/services/dsl/engine.py` | 0% | 90% | +90% |
| **Total** | **27%** | **~85%** | **+58%** |

### 2. Estrutura de Testes

**Obrigatório:**
- Arquivo `tests/conftest.py` com fixtures compartilhadas
- Arquivo `tests/test_endpoints.py` para endpoints HTTP
- Arquivo `tests/test_generate_roadmap.py` para generate_roadmap.py
- Arquivo `tests/test_generate_lessons.py` para generate_lessons.py
- Arquivo `tests/test_dsl_engine.py` para DSL engine

**Remover:**
- `tests/test_diagnosis_logic.py` (duplicado)

### 3. Tipos de Teste

| Tipo | Quantidade | Descrição |
|------|------------|-----------|
| Unitários | ~35 | Testes de funções isoladas |
| Integração | ~15 | Testes de endpoints HTTP |
| Mock | ~25 | Testes com OpenAI mockado |
| Erro | ~10 | Testes de casos de erro (404, 500, 502) |

### 4. Critérios de Qualidade

1. **100% dos testes passando** — nenhum teste quebrado
2. **Cobertura ≥ 85%** em cada módulo principal
3. **Tempo de execução < 5s** — testes rápidos
4. **Fixtures reutilizáveis** — DRY nos testes
5. **Mocks consistentes** — usar unittest.mock

### 5. Mocking de APIs Externas

| API | Módulo | Estratégia |
|-----|--------|------------|
| OpenAI | generate_roadmap.py | Mock `client.chat.completions.create` |
| OpenAI | generate_lessons.py | Mock `client.chat.completions.create` |
| OpenAI | server.py (DiagnosisService) | Mock `OpenAI` class |

### 6. Casos de Teste Obrigatórios

#### Endpoints HTTP (server.py)
- [ ] `GET /api/roadmaps` — lista vazia, lista com arquivos, exclusão de dep_map
- [ ] `GET /api/roadmap/<file>` — arquivo existe, não existe
- [ ] `GET /api/dep-map` — arquivo existe, não existe (404)
- [ ] `POST /api/generate-lesson` — sucesso, missing id, erro
- [ ] `POST /api/generate-roadmap` — sucesso, tema vazio, erro IA
- [ ] `POST /api/save-roadmap` — sucesso, erro permissão
- [ ] `POST /api/diagnose` — 400 params inválidos, 502 falha LLM, 500 erro interno
- [ ] `POST /api/regenerate-dep-map` — sucesso, erro escrita

#### Geração (generate_*.py)
- [ ] `gerar_roadmap_ia()` — JSON válido, JSON inválio, regex fallback
- [ ] `salvar_roadmap()` — arquivo criado, diretório criado
- [ ] `gerar_conteudo_ia()` — resposta vazia, conteúdo longo
- [ ] `processar_node()` — arquivo criado, encoding UTF-8

#### DSL Engine
- [ ] `execute()` — DSL executado, retorna status
- [ ] `validate()` — dict válido, tipos inválidos

### 7. Evitar False Positives

- Cada teste deve ter assertion específica
- Não usar `pass` em testes
- Verificar corpo da resposta (não só status code)
- Verificar encoding UTF-8 em arquivos

## Glossary

- **Coverage**: Percentual de linhas executadas pelos testes
- **Mock**: Objeto simulado para substituir dependências externas
- **Fixture**: Função que fornece dados/comportamento reutilizável para testes
- **Unit Test**: Teste de uma unidade isolada de código
- **Integration Test**: Teste de múltiplas unidades trabalhando juntas