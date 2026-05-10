# Spec: Plano de Cobertura de Testes (~85-90%)

## Objetivo

Implementar testes para atingir cobertura de 85-90% em cada módulo do projeto roadmap-estudos.

## Módulos e Gaps de Teste

### 1. `server.py` — Cobertura atual: 27% | Alvo: 85%

#### Endpoints não testados (GET)
| Endpoint | Função | Prioridade | Testes necessários |
|----------|--------|------------|-------------------|
| `GET /api/roadmaps` | `list_roadmaps()` | Alta | Lista vazia, com arquivos, excluindo dep_map.json |
| `GET /api/roadmap/<file>` | `load_roadmap()` | Alta | Arquivo existe, arquivo não existe |
| `GET /api/dep-map` | `get_dep_map()` | Alta | Arquivo existe, arquivo não existe |
| CORS headers | `end_headers()` | Baixa | Verificar headers de CORS |

#### Endpoints não testados (POST)
| Endpoint | Função | Prioridade | Testes necessários |
|----------|--------|------------|-------------------|
| `POST /api/generate-lesson` | `handle_generate_lesson()` | Alta | Sucesso, dados inválidos, erro IA |
| `POST /api/generate-roadmap` | `handle_generate_roadmap()` | Alta | Sucesso, tema vazio, erro IA |
| `POST /api/save-roadmap` | `handle_save_roadmap()` | Alta | Sucesso, arquivo não existe, erro permissão |
| `POST /api/diagnose` | `handle_diagnosis()` | ✅ Já testado | - |
| `POST /api/regenerate-dep-map` | `handle_regenerate_dep_map()` | Alta | Sucesso, erro glob, erro escrita |

#### Endpoints não testados (DELETE)
| Endpoint | Função | Prioridade | Testes necessários |
|----------|--------|------------|-------------------|
| `DELETE /` | `do_DELETE()` | Baixa | Retorna 200 |

#### Casos de erro não testados
| Cenário | Prioridade | Descrição |
|---------|------------|-----------|
| 400 para diagnose sem params | Alta | Testar topic vazio, user_answer vazio |
| 404 para rota inexistente | Alta | Testar POST/GET para rota não existente |
| 502 para falha LLM | Alta | Mockar erro OpenAI |
| 500 para erro interno | Alta | Mockar exceções genéricas |

#### Detalhamento de Testes

```
tests/test_endpoints.py
├── TestListRoadmaps
│   ├── test_list_roadmaps_empty_dir
│   ├── test_list_roadmaps_with_files
│   └── test_list_roadmaps_excludes_dep_map
├── TestLoadRoadmap
│   ├── test_load_roadmap_success
│   └── test_load_roadmap_not_found
├── TestDepMap
│   ├── test_get_dep_map_success
│   └── test_get_dep_map_not_found
├── TestGenerateLesson
│   ├── test_generate_lesson_success
│   ├── test_generate_lesson_missing_id
│   └── test_generate_lesson_error
├── TestGenerateRoadmap
│   ├── test_generate_roadmap_success
│   ├── test_generate_roadmap_empty_theme
│   └── test_generate_roadmap_error
├── TestSaveRoadmap
│   ├── test_save_roadmap_success
│   └── test_save_roadmap_permission_error
├── TestRegenerateDepMap
│   ├── test_regenerate_dep_map_success
│   ├── test_regenerate_dep_map_no_files
│   └── test_regenerate_dep_map_write_error
├── TestDiagnosisErrorHandling
│   ├── test_diagnose_missing_topic
│   ├── test_diagnose_missing_answer
│   ├── test_diagnose_llm_failure_502
│   └── test_diagnose_internal_error_500
└── TestCORs
    └── test_cors_headers_present
```

---

### 2. `generate_roadmap.py` — Cobertura atual: 32% | Alvo: 85%

#### Funções não testadas
| Função | Prioridade | Testes necessários |
|--------|------------|-------------------|
| `gerar_roadmap_ia()` | Alta | Mock OpenAI, JSON válido, JSON inválido, regex fallbacks |
| `salvar_roadmap()` | Alta | Arquivo criado, diretório criado, permissões |
| `BASE_DIR` | Baixa | Verificar que usa diretório correto |

#### Detalhamento de Testes

```
tests/test_generate_roadmap.py
├── TestGerarRoadmapIA
│   ├── test_gerar_roadmap_success
│   ├── test_gerar_roadmap_invalid_json
│   ├── test_gerar_roadmap_no_json_in_response
│   └── test_gerar_roadmap_empty_response
├── TestSalvarRoadmap
│   ├── test_salvar_roadmap_new_file
│   ├── test_salvar_roadmap_existing_file
│   ├── test_salvar_roadmap_creates_dir
│   └── test_salvar_roadmap_permission_error
└── TestBaseDir
    └── test_base_dir_resolution
```

---

### 3. `generate_lessons.py` — Cobertura atual: 32% | Alvo: 85%

#### Funções não testadas
| Função | Prioridade | Testes necessários |
|--------|------------|-------------------|
| `gerar_conteudo_ia()` | Alta | Mock OpenAI, resposta vazia, conteúdo longo |
| `processar_node()` | Alta | Arquivo criado, diretório criado, encoding UTF-8 |

#### Detalhamento de Testes

```
tests/test_generate_lessons.py
├── TestGerarConteudoIA
│   ├── test_gerar_conteudo_success
│   ├── test_gerar_conteudo_empty_response
│   └── test_gerar_conteudo_long_content
├── TestProcessarNode
│   ├── test_processar_node_new_file
│   ├── test_processar_node_creates_dir
│   ├── test_processar_node_encoding_utf8
│   └── test_processar_node_permission_error
└── TestBaseDir
    └── test_base_dir_resolution
```

---

### 4. `src/services/dsl/engine.py` — Cobertura atual: 0% | Alvo: 90%

#### Funções não testadas
| Função | Prioridade | Testes necessários |
|--------|------------|-------------------|
| `__init__()` | Alta | Engine inicializa com context vazio |
| `execute()` | Alta | DSL executado, retorna status |
| `validate()` | Alta | DSL válido, DSL inválido (não-dict) |

#### Detalhamento de Testes

```
tests/test_dsl_engine.py
├── TestDSLExecutionEngine
│   ├── test_init_empty_context
│   ├── test_execute_returns_executed_status
│   ├── test_execute_preserves_dsl
│   ├── test_execute_empty_dsl
│   ├── test_validate_valid_dict
│   ├── test_validate_invalid_type_string
│   ├── test_validate_invalid_type_list
│   └── test_validate_invalid_type_none
```

---

### 5. Limpeza: Remover teste duplicado

| Arquivo | Ação | Prioridade |
|---------|------|------------|
| `tests/test_diagnosis_logic.py` | **REMOVER** — duplicado de `test_diagnosis.py` | Alta |

---

## Plano de Execução

### Fase 1: Testes de Endpoints (server.py)
1. Criar `tests/test_endpoints.py`
2. Implementar todos os 20+ testes
3. Meta: server.py 85%+

### Fase 2: Testes de Geração (generate_*.py)
4. Criar `tests/test_generate_roadmap.py`
5. Criar `tests/test_generate_lessons.py`
6. Meta: cada módulo 85%+

### Fase 3: Testes DSL Engine
7. Criar `tests/test_dsl_engine.py`
8. Meta: engine 90%+

### Fase 4: Limpeza
9. Remover `test_diagnosis_logic.py` duplicado
10. Executar coverage final

---

## Critérios de Aceitação

| Métrica | Alvo |
|---------|------|
| Cobertura server.py | ≥ 85% |
| Cobertura generate_roadmap.py | ≥ 85% |
| Cobertura generate_lessons.py | ≥ 85% |
| Cobertura src/services/dsl/engine.py | ≥ 90% |
| Cobertura tests/ | ≥ 90% (já está) |
| Testes totais | ~50+ |
| Status do harness | ✅ HEALTHY |
| Testes passando | 100% |

---

## Estrutura Final de Testes

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartilhadas
├── test_api.py              # DiagnosisService (existente)
├── test_diagnosis.py        # Lógica de diagnóstico (existente)
├── test_diagnosis_logic.py  # [REMOVER - duplicado]
├── test_endpoints.py        # [NOVO] Endpoints HTTP
├── test_generate_roadmap.py # [NOVO] Geração de roadmap
├── test_generate_lessons.py# [NOVO] Geração de lições
└── test_dsl_engine.py       # [NOVO] DSL Engine
```

---

## Dependências de Teste

```python
# tests/conftest.py
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Fixtures:
# - mock_openai_client: Mock do cliente OpenAI
# - temp_data_dir: Diretório temporário para testes
# - sample_roadmap: Roadmap de exemplo para testes
# - sample_dep_map: dep_map de exemplo
```

---

## Notas

- Todos os mocks devem usar `unittest.mock` para consistência
- Testar casos de erro com `assertRaises`
- Verificar headers HTTP em endpoints
- Coverage deve ser executado com `pytest --cov=. --cov-report=term-missing`
- Manter testes independentes (clean teardown)