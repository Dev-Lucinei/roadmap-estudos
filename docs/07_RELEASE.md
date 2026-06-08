# 07_RELEASE.md — Log de Releases

**Projeto**: Roadmap-Estudos
**Data**: 2026-06-08

---

## Versão Atual

| Campo | Valor |
|-------|-------|
| **Versão** | v3.0.1 |
| **Data de lançamento** | 2026-05-12 |
| **Status** | Estável |
| **Python** | ≥3.11 |

---

## Histórico de Releases

### v3.0.1 — 2026-05-12
**Tipo**: Correção de bugs
- Corrigido E402 imports em `main.py` com `noqa: E402`
- Corrigido testes de API para novo módulo `backend/`
- Corrigido teste `test_diagnose_missing_api_key` para usar `patch.dict`
- Config lazy evaluation: `check_api_key()` lê do ambiente atual via `get_api_key()`

### v3.0.0 — 2026-05-11
**Tipo**: Breaking change — Migração para FastAPI
- Substituído `http.server` síncrono por **FastAPI** + uvicorn
- Endpoints assíncronos (`async def`) — não bloqueiam em I/O
- Pydantic v2 para validação automática de inputs
- Swagger UI disponível em `/docs`
- CORS integrado via middleware
- Novos modelos em `backend/models/`: Lesson, Quiz, Roadmap, Diagnosis
- Rotas em `backend/api/routes_fastapi.py`

### v2.3.1 — 2026-05-11
**Tipo**: Correção de bugs + features
- [CRÍTICO] Endpoints de quiz corrigidos (padronização REST)
- [CRÍTICO] Payload de geração de lição corrigido (`id` → `node_id`)
- Normalização de nomes de arquivo com `unicodedata.normalize()`
- Script de validação de formato: `scripts/validate_content_format.py`
- Documentação de padrões: `docs/PADROES_FORMATO_CONTEUDO.md`

### v2.3.0 — 2026-05-11
**Tipo**: Correção de bugs
- [CRÍTICO] Roadmaps não carregando — renomeação para seguir padrão `roadmap_`
- [CRÍTICO] Lições existentes não carregando — tratamento para rota `/licoes/`
- Método `_send_file()` para servir arquivos Markdown com encoding correto

### v2.9.3 — 2026-05-11
**Tipo**: Correção de bug
- Corrigido `box-sizing: border-box` em `.flowchart-node` — padding incluído na altura

### v2.9.2 — 2026-05-11
**Tipo**: Refactor
- Removido ajuste complexo de `adjustedY` — simplificado para `currentY`

### v2.9.1 — 2026-05-11
**Tipo**: Melhoria
- Botão "📝 Gerar Conteúdo" para geração de lição sob demanda
- Prompt otimizado: focado, conciso, max 800 palavras, 1500 tokens

### v2.9.0 — 2026-05-11
**Tipo**: Feature
- Sistema de Avaliação de Conhecimento via Quiz IA
- Botão "🧠 Gerar Quiz" no painel de lições
- Backend: `QuizService` com `generate_quiz()` e `evaluate_quiz()`
- Interface com radio buttons e validação de respostas
- Avaliação assertiva via IA com feedback detalhado
- Sistema de pontuação (0-100%) e status aprovado/reprovado

### v2.8.0 — 2026-05-10
**Tipo**: Feature
- Algoritmo de Layout Adaptativo — cálculo dinâmico de espaçamento
- Fase 1: pré-calcula altura necessária
- Fase 2: posiciona com espaçamento mínimo necessário
- Centralização vertical de subtópicos

### v2.7.0 — 2026-05-10
**Tipo**: Feature
- Expansão/Recolhimento interativo de nós
- Botões "📂 Expandir" e "📁 Recolher" no header
- Layout único (fluxograma como padrão)

### v2.6.0 — 2026-05-10
**Tipo**: Feature
- Layout de Fluxograma Profissional (mindmap/fluxograma)
- Conexões SVG com curvas bezier
- Alternância de Layout (árvore ↔ fluxograma)

### v2.5.0 — 2026-05-10
**Tipo**: Feature
- Sistema de Expansão Inteligente (horizontal nível 1, vertical nível 2+)
- Responsividade para telas < 1200px

### v2.4.0 — 2026-05-10
**Tipo**: Feature
- Padrão JSON Unificado (estrutura v2.0 com `subtopics`)
- Script de migração: `scripts/migrate_roadmap_structure.py`

### v2.3.0 — 2026-05-10
**Tipo**: Feature + Security
- Sistema de Proteção com Imutabilidade (`chattr +i`)
- Hook Pre-Commit com validação de imutabilidade
- Documentação: `GUIA_RAPIDO_SEAL.md`

### v2.2.0 — 2026-05-10
**Tipo**: Security fix
- [P0] Path traversal em `load_roadmap` e `handle_save_roadmap`
- [P0] XSS via `innerHTML` com dados do LLM
- [P0] Validação de `Content-Length` em `do_POST`
- [P1] Falha silenciosa de API key
- [P1] CORS aberto → restrito a `localhost:8000`
- [P1] Contagem cruzada de progresso

### v2.1.0 — 2026-05-09
**Tipo**: Feature
- Ecossistema Multi-Tema
- Servidor de Ponte (`server.py`) em Python
- Modo Edição (CRUD UI)
- Geração de IA Integrada

### v1.5.0 — 2026-05-08
**Tipo**: Feature
- Gamificação (Streaks, Quizzes)
- Modo Zen
- Persistência Local (localStorage)

### v1.0.0 — Inicial
**Tipo**: Feature
- Estrutura base com HTML/CSS
- Renderização de conexões dinâmicas via SVG
- Suporte inicial para Markdown e Mermaid.js

---

## Próximas Versões Planejadas

### v3.1.0 — Planejado
- [ ] Migrar config para `pydantic-settings` (US-004)
- [ ] Adicionar timeout em subprocessos (US-005)
- [ ] Proteger contra path traversal em todas as rotas (US-006)

### v3.2.0 — Planejado
- [ ] Substituir prints por logging estruturado (US-007)
- [ ] Eliminar exceções genéricas `except Exception` (US-008)
- [ ] Configurar cobertura mínima ≥85% (US-010)

### v4.0.0 — Futuro
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Autenticação JWT (multi-tenant)
- [ ] Rate limiting em endpoints públicos
- [ ] Dashboard de progresso com métricas

---

## Notas de Versão

- **v3.x**: Fase de maturação técnica (FastAPI, testes, qualidade)
- **v2.x**: Fase de features (layout, quiz, IA, segurança)
- **v1.x**: Fase de prototipação (HTML/CSS básico)
