# Tasks: Implementação de Testes (~85-90% Coverage)

## Fase 0: Preparação

- [ ] 0.1 Remover `tests/test_diagnosis_logic.py` (duplicado)
- [ ] 0.2 Criar `tests/conftest.py` com fixtures compartilhadas
- [ ] 0.3 Verificar que `pytest` e `pytest-cov` estão instalados
- [ ] 0.4 Executar baseline de coverage atual

## Fase 1: DSL Engine (90% target)

- [ ] 1.1 Criar `tests/test_dsl_engine.py`
- [ ] 1.2 Testar `DSLExecutionEngine.__init__()` — context vazio
- [ ] 1.3 Testar `execute()` — DSL executado corretamente
- [ ] 1.4 Testar `execute()` — DSL vazio
- [ ] 1.5 Testar `validate()` — dict válido
- [ ] 1.6 Testar `validate()` — string (inválido)
- [ ] 1.7 Testar `validate()` — list (inválido)
- [ ] 1.8 Testar `validate()` — None (inválido)
- [ ] 1.9 Executar testes e verificar coverage ≥ 90%
- [ ] 1.10 Commit: `test(engine): adiciona testes para DSL engine`

## Fase 2: Endpoints HTTP (85% target)

- [ ] 2.1 Criar `tests/test_endpoints.py`
- [ ] 2.2 Implementar `TestListRoadmaps`
  - [ ] 2.2.1 test_list_roadmaps_empty_dir
  - [ ] 2.2.2 test_list_roadmaps_with_files
  - [ ] 2.2.3 test_list_roadmaps_excludes_dep_map
- [ ] 2.3 Implementar `TestLoadRoadmap`
  - [ ] 2.3.1 test_load_roadmap_success
  - [ ] 2.3.2 test_load_roadmap_not_found (404)
- [ ] 2.4 Implementar `TestDepMap`
  - [ ] 2.4.1 test_get_dep_map_success
  - [ ] 2.4.2 test_get_dep_map_not_found (404)
- [ ] 2.5 Implementar `TestGenerateLesson`
  - [ ] 2.5.1 test_generate_lesson_success
  - [ ] 2.5.2 test_generate_lesson_missing_id (400)
  - [ ] 2.5.3 test_generate_lesson_error (500)
- [ ] 2.6 Implementar `TestGenerateRoadmap`
  - [ ] 2.6.1 test_generate_roadmap_success
  - [ ] 2.6.2 test_generate_roadmap_empty_theme
  - [ ] 2.6.3 test_generate_roadmap_error (500)
- [ ] 2.7 Implementar `TestSaveRoadmap`
  - [ ] 2.7.1 test_save_roadmap_success
  - [ ] 2.7.2 test_save_roadmap_permission_error (500)
- [ ] 2.8 Implementar `TestRegenerateDepMap`
  - [ ] 2.8.1 test_regenerate_dep_map_success
  - [ ] 2.8.2 test_regenerate_dep_map_no_files
  - [ ] 2.8.3 test_regenerate_dep_map_write_error (500)
- [ ] 2.9 Implementar `TestDiagnosisErrorHandling`
  - [ ] 2.9.1 test_diagnose_missing_topic (400)
  - [ ] 2.9.2 test_diagnose_missing_answer (400)
  - [ ] 2.9.3 test_diagnose_llm_failure (502)
  - [ ] 2.9.4 test_diagnose_internal_error (500)
- [ ] 2.10 Implementar `TestCORs`
  - [ ] 2.10.1 test_cors_headers_present
- [ ] 2.11 Executar testes e verificar coverage ≥ 85%
- [ ] 2.12 Commit: `test(endpoints): adiciona testes para endpoints HTTP`

## Fase 3: Generate Roadmap (85% target)

- [ ] 3.1 Criar `tests/test_generate_roadmap.py`
- [ ] 3.2 Implementar `TestGerarRoadmapIA`
  - [ ] 3.2.1 test_gerar_roadmap_success (mock OpenAI)
  - [ ] 3.2.2 test_gerar_roadmap_invalid_json
  - [ ] 3.2.3 test_gerar_roadmap_no_json_in_response
  - [ ] 3.2.4 test_gerar_roadmap_empty_response
- [ ] 3.3 Implementar `TestSalvarRoadmap`
  - [ ] 3.3.1 test_salvar_roadmap_new_file
  - [ ] 3.3.2 test_salvar_roadmap_existing_file
  - [ ] 3.3.3 test_salvar_roadmap_creates_dir
  - [ ] 3.3.4 test_salvar_roadmap_permission_error (mock)
- [ ] 3.4 Implementar `TestBaseDir`
  - [ ] 3.4.1 test_base_dir_resolution
- [ ] 3.5 Executar testes e verificar coverage ≥ 85%
- [ ] 3.6 Commit: `test(roadmap): adiciona testes para generate_roadmap`

## Fase 4: Generate Lessons (85% target)

- [ ] 4.1 Criar `tests/test_generate_lessons.py`
- [ ] 4.2 Implementar `TestGerarConteudoIA`
  - [ ] 4.2.1 test_gerar_conteudo_success (mock OpenAI)
  - [ ] 4.2.2 test_gerar_conteudo_empty_response
  - [ ] 4.2.3 test_gerar_conteudo_long_content
- [ ] 4.3 Implementar `TestProcessarNode`
  - [ ] 4.3.1 test_processar_node_new_file
  - [ ] 4.3.2 test_processar_node_creates_dir
  - [ ] 4.3.3 test_processar_node_encoding_utf8
  - [ ] 4.3.4 test_processar_node_permission_error (mock)
- [ ] 4.4 Implementar `TestBaseDir`
  - [ ] 4.4.1 test_base_dir_resolution
- [ ] 4.5 Executar testes e verificar coverage ≥ 85%
- [ ] 4.6 Commit: `test(lessons): adiciona testes para generate_lessons`

## Fase 5: Validação Final

- [ ] 5.1 Executar todos os testes: `pytest tests/ -v`
- [ ] 5.2 Executar coverage: `pytest --cov=. --cov-report=term-missing`
- [ ] 5.3 Verificar cada módulo:
  - [ ] server.py ≥ 85%
  - [ ] generate_roadmap.py ≥ 85%
  - [ ] generate_lessons.py ≥ 85%
  - [ ] src/services/dsl/engine.py ≥ 90%
- [ ] 5.4 Executar harness: `uv run python3 harness.py`
- [ ] 5.5 Commit final: `test(coverage): completa suite de testes ~85-90% coverage`

---

## Resumo de Tarefas

| Fase | Arquivos | Testes | Coverage Target |
|------|----------|--------|-----------------|
| 0 | conftest.py | - | - |
| 1 | test_dsl_engine.py | 8 | 90% |
| 2 | test_endpoints.py | 22 | 85% |
| 3 | test_generate_roadmap.py | 9 | 85% |
| 4 | test_generate_lessons.py | 9 | 85% |
| 5 | Validação | - | - |
| **Total** | **5 novos** | **~48** | **~85-90%** |

## Dependências

- pytest (já instalado)
- pytest-cov (já instalado)
- unittest.mock (stdlib)
- tempfile (stdlib)
- shutil (stdlib)