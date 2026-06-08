# 02_PRD.md

**Baseado em**: Análise de Aderência às Diretrizes Herdadas
**Data**: 2026-06-08
**Autor**: Agente de IA

---

## Contexto

O projeto **roadmap-estudos** atinge atualmente **68% de aderência** às diretrizes e padrões definidos em `/home/lucinei/Projetos/.agents/`. Esta análise identificou lacunas críticas em segurança, configuração de ferramentas, estrutura de diretórios e documentação que precisam ser endereçadas para atingir a meta de **≥85%**.

---

## 1. User Stories

### US-001: Criar template de variáveis de ambiente
**História**: Como desenvolvedor quero um arquivo `.env.example` para saber quais variáveis de ambiente são necessárias sem expor valores reais

**Critérios de Aceite**:
1. Given o repositório clonado When o desenvolvedor consulta `.env.example` Then visualiza todas as variáveis necessárias com descrições
2. Given `.env.example` existe When executado `git status` Then o arquivo não aparece como não rastreado (deve ser commitado)

---

### US-002: Remover backups proibidos
**História**: Como mantenedor quero remover arquivos `.bak/.backup` que violam a política de data-protection.md

**Critérios de Aceite**:
1. Given os arquivos `guard_harness.py.backup` e `.bak` existem When executado `ls scripts/` Then nenhum arquivo `.bak` ou `.backup` é listado
2. Given os arquivos removidos When executado `git status` Then as deleções estão staged para commit

---

### US-003: Configurar ferramentas de qualidade no pyproject.toml
**História**: Como desenvolvedor quero `[tool.ruff]`, `[tool.mypy]` e `[tool.pytest]` configurados para ter validação automática

**Critérios de Aceite**:
1. Given `pyproject.toml` atualizado When executado `ruff check .` Then o comando roda com a configuração definida
2. Given `pyproject.toml` atualizado When executado `mypy --strict backend/` Then o comando usa as configs do projeto
3. Given `pyproject.toml` atualizado When executado `pytest` Then `asyncio_mode = "auto"` está ativo

---

### US-004: Implementar pydantic-settings
**História**: Como desenvolvedor quero que as configurações usem `pydantic-settings` para validação estruturada de variáveis de ambiente

**Critérios de Aceite**:
1. Given `config.py` migrado When o servidor inicia Then as variáveis são validadas pelo Pydantic
2. Given variável obrigatória ausente When o servidor inicia Then erro claro é exibido com variável faltante
3. Given `pyproject.toml` Then `pydantic-settings>=2.0.0` está em `dependencies`

---

### US-005: Adicionar timeout em subprocessos
**História**: Como operador quero que subprocessos tenham timeout de 5s para evitar processos zumbis

**Critérios de Aceite**:
1. Given `guard_harness.py` When subprocesso excede 5s Then é terminado automaticamente
2. Given timeout atingido When tratamento de exceção Then mensagem de erro clara é registrada

---

### US-006: Proteger contra path traversal
**História**: Como operador de segurança quero que rotas de API validem caminhos para evitar acesso a diretórios pai

**Critérios de Aceite**:
1. Given requisição com `../` no `lesson_file` When rota `/licoes/{lesson_file}` Then retorna 403 ou 404
2. Given `roadmap_id` com caracteres inválidos When rota `/api/roadmap/{roadmap_id}` Then retorna 400
3. Given caminho válido When `Path.resolve()` está dentro do diretório permitido Then arquivo é retornado

---

### US-007: Substituir prints por logging estruturado
**História**: Como desenvolvedor quero logs estruturados em vez de `print()` para observabilidade

**Critérios de Aceite**:
1. Given services revisados When executado `grep -r "print(" backend/services/` Then nenhum `print()` é encontrado
2. Given logging configurado When evento registrado Then inclui timestamp, nível e mensagem

---

### US-008: Eliminar exceções genéricas
**História**: Como desenvolvedor quero exceções específicas em vez de `except Exception` para tratamento adequado

**Critérios de Aceite**:
1. Given `routes_fastapi.py` revisado When endpoints de quiz/evaluate rodam Then exceções específicas são capturadas
2. Given exceção específica When tratada Then mensagem de erro é útil para debug

---

### US-009: Criar subestrutura de testes
**História**: Como desenvolvedor quero `tests/unit/` e `tests/integration/` para organizar testes

**Critérios de Aceite**:
1. Given diretórios criados When executado `pytest` Then todos os testes são encontrados
2. Given testes movidos When executado `pytest --cov` Then cobertura é calculada corretamente

---

### US-010: Configurar cobertura mínima
**História**: Como mantenedor quero `--cov-fail-under=85` para garantir qualidade

**Critérios de Aceite**:
1. Given `pyproject.toml` atualizado When executado `pytest --cov` Then falha se cobertura < 85%
2. Given cobertura ≥ 85% When executado `pytest --cov` Then teste passa

---

### US-011: Criar documentação de fases
**História**: Como stakeholder quero documentos `01_BRIEF.md` a `07_RELEASE.md` para rastreabilidade

**Critérios de Aceite**:
1. Given `docs/` revisado When listado Then contém pelo menos `01_BRIEF.md`, `02_PRD.md`, `03_DESIGN.md`
2. Given documentos criados When consultados Then descrevem contexto, decisões e evidências do projeto

---

### US-012: Criar ADRs locais
**História**: Como arquiteto quero ADRs documentando decisões técnicas do projeto

**Critérios de Aceite**:
1. Given ADRs criados When consultados Then contêm Contexto, Decisão e Consequências
2. Given pelo menos 2 ADRs When listados Then cobrem migração FastAPI e integração OpenRouter

---

### US-013: Podar CHANGELOG.md
**História**: Como desenvolvedor quero `CHANGELOG.md` com ≤500 linhas para legibilidade

**Critérios de Aceite**:
1. Given `CHANGELOG.md` revisado When executado `wc -l` Then resultado ≤ 500
2. Given entradas antigas When resumidas Then informações críticas são preservadas

---

## 2. Requisitos Não Funcionais

### Segurança
- [x] Deny list de comandos bloqueados (política security.md)
- [x] Sem hardcode de segredos em código
- [ ] `.env.example` commitado sem valores reais
- [ ] Sem arquivos `.bak/.backup` no repositório
- [ ] Path traversal protegido em todas as rotas de arquivo
- [ ] Subprocessos com timeout máximo de 5 segundos

### Qualidade de Código
- [ ] `ruff check` e `ruff format --check` passam sem erros
- [ ] `mypy --strict` passa sem erros
- [ ] `pytest --cov-fail-under=85` passa
- [ ] Sem uso de `Any` em type hints
- [ ] Sem `print()` em código de produção
- [ ] Exceções específicas capturadas (não `except Exception`)

### Estrutura
- [ ] Subpastas `tests/unit/` e `tests/integration/`
- [ ] Documentação de fases em `docs/`
- [ ] ADRs locais documentados
- [ ] `CHANGELOG.md` com ≤500 linhas

### Observabilidade
- [ ] Logging estruturado com timestamps
- [ ] Mensagens de erro claras e acionáveis
- [ ] Tratamento de exceções com contexto

---

## 3. Métricas v1

| Métrica | Alvo | Ferramenta de Medição |
|---------|------|----------------------|
| Aderência às diretrizes | ≥85% | Análise manual/automatizada |
| Cobertura de código | ≥85% | `pytest --cov` |
| Qualidade de lint | 0 erros | `ruff check` |
| Formatação | 0 divergências | `ruff format --check` |
| Tipagem estrita | 0 erros | `mypy --strict` |
| Tamanho do CHANGELOG | ≤500 linhas | `wc -l CHANGELOG.md` |
| Segurança | 0 violações | `python harness.py` |

---

## 4. Fora de Escopo (v1)

- Migrar `backend/` para `src/` (decisão opcional, alto custo)
- Implementar CI/CD pipeline
- Adicionar testes de integração com banco de dados
- Configurar rate limiting em endpoints públicos
- Implementar autenticação JWT
