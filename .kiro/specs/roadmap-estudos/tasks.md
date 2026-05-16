# Implementation Plan: Roadmap-Estudos

## Fase 1: Estrutura Base e Governança (COMPLETA)

- [x] 1.1 Configurar estrutura de diretórios
  - Criar backend/, frontend/, data/, licoes/, scripts/, tests/
  - _Requirements: R.8_

- [x] 1.2 Configurar harness de validação
  - Copiar harness.py e scripts/guard_harness.py
  - Executar: python scripts/guard_harness.py --seal
  - _Requirements: R.8, R.9_

- [x] 1.3 Configurar dependências
  - FastAPI, Pydantic v2, OpenAI SDK, pytest, ruff, mypy
  - _Requirements: R.9_

## Fase 2: Backend Core (COMPLETA)

- [x] 2.1 Implementar modelos Pydantic
  - Criar models para lesson, quiz, roadmap, diagnosis
  - _Requirements: R.1, R.2, R.3, R.4_

- [x] 2.2 Migrar rotas para FastAPI
  - Implementar APIRouter com 9 endpoints
  - Migrar de http.server para uvicorn
  - _Requirements: R.1, R.2, R.3, R.4_

- [x] 2.3 Implementar geração de roadmaps
  - Criar roadmap_generator.py com chamadas OpenRouter
  - _Requirements: R.1_

- [x] 2.4 Implementar geração de lições
  - Criar lesson_generator.py com suporte a quizzes embutidos
  - _Requirements: R.2_

- [x] 2.5 Implementar sistema de quiz
  - Gerar 4 perguntas, avaliar respostas via IA
  - _Requirements: R.3_

- [x] 2.6 Implementar serviço de diagnóstico
  - Analisar gaps com dep_map.json
  - _Requirements: R.4_

## Fase 3: Frontend (COMPLETA)

- [x] 3.1 Desenvolver SPA com tema escuro glassmorphism
  - index.html + main.css + app.js
  - _Requirements: R.5_

- [x] 3.2 Implementar renderização de fluxograma
  - flowchart_layout.js com SVG bezier e alternância de lados
  - _Requirements: R.5_

- [x] 3.3 Implementar expansão/recolhimento de nós
  - Animação suave, toggle por nó individual
  - _Requirements: R.5_

- [x] 3.4 Implementar posicionamento dinâmico
  - Algoritmo de espacamento para evitar sobreposição
  - _Requirements: R.5_

## Fase 4: Validação e Segurança (COMPLETA)

- [x] 4.1 Implementar script de validação de conteúdo
  - validate_content_format.py: naming, estrutura JSON, quiz
  - _Requirements: R.6_

- [x] 4.2 Implementar guard_harness
  - SHA256, chattr +i, git dirty detection
  - _Requirements: R.8_

- [x] 4.3 Migrar validação para harness.py unificado
  - Agregar lint, type, test, audit, security, structure, content
  - _Requirements: R.8, R.9_

- [x] 4.4 Prevenir path traversal e XSS
  - Sanitização em rotas de arquivos
  - _Requirements: R.8_

## Fase 5: Testes (PARCIAL)

- [x] 5.1 Testes de diagnóstico
  - test_diagnosis.py, test_api.py
  - _Requirements: R.9_

- [x] 5.2 Testes do motor DSL
  - test_dsl_engine.py (engine é stub, testes limitados)
  - _Requirements: R.9_

- [x] 5.3 Corrigir erro de importação em tests/test_api.py
  - Teste falha ao coletar (provavelmente dependência ou mock faltando)
  - _Requirements: R.9_

- [x] 5.4 Adicionar docstrings e return types em todo backend
  - ~93 avisos de audit: módulos, classes e funções sem docstring/return type
  - _Requirements: R.9_

## Fase 6: Expansão de Conteúdo (PENDENTE)

- [x] 6.1 Expandir dep_map.json
  - Atualmente apenas 2 entradas com listas vazias
  - Mapear dependências reais entre tópicos de programação
  - _Requirements: R.4_

- [ ] 6.2 Gerar lições faltantes (~57)
  - 21 de ~78 lições existentes (27%)
  - Usar lesson_generator.py para preencher lacunas
  - _Requirements: R.2_

- [ ] 6.3 Adicionar quizzes em lições sem quiz
  - algos-ds.md, arch.md, paradigmas.md, sintaxe-estruturas.md, sw-eng-basics.md
  - Corrigir docker-dockerfiles.md (quiz com < 3 perguntas)
  - _Requirements: R.3_

## Fase 7: Motor DSL (PENDENTE)

- [ ] 7.1 Implementar validação de sintaxe DSL
  - engine.py: validar comandos, parâmetros e estrutura
  - _Requirements: R.7_

- [ ] 7.2 Implementar execução de comandos DSL
  - engine.py: executar fluxos de aprendizado programáticos
  - _Requirements: R.7_

- [ ] 7.3 Testes completos para motor DSL
  - engine.py: cobrir sintaxe inválida, comandos, edge cases
  - _Requirements: R.7, R.9_

## Fase Final: Qualidade e Auditoria

- [ ] F.1 Auditoria de segurança via harness
  - Executar: python harness.py security
  - _Requirements: R.8_

- [ ] F.2 Verificar integridade dos artefatos protegidos
  - Executar: python scripts/guard_harness.py
  - Confirmar STATUS: INTACT
  - _Requirements: R.8_

- [ ] F.3 Gate final de qualidade
  - Executar: python harness.py
  - Confirmar: 0 erros críticos
  - _Requirements: R.8, R.9_
