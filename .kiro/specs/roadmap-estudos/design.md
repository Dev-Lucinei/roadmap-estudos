# Design Document: Roadmap-Estudos

## Overview
Plataforma de estudos personalizada que gera roadmaps e lições via IA (OpenRouter), com quizzes interativos, diagnóstico de conhecimento e visualização em fluxograma expansível.

## Princípios de Engenharia

| Princípio | Aplicação neste projeto |
|-----------|------------------------|
| **KISS** | Persistência em arquivos JSON/Markdown (sem banco de dados). Frontend single-page sem frameworks. |
| **DRY** | Serviços compartilham cliente OpenAI via funções `get_client()` em cada módulo. Config centralizada em `backend/core/config.py`. |
| **SRP** | Cada serviço tem responsabilidade única: `lesson_generator` → lições, `quiz_service` → quizzes, `diagnosis_service` → diagnóstico, `roadmap_generator` → roadmaps. |
| **Immutable Artifacts** | `harness.py`, `guard_harness.py` e `.harness.hash` são protegidos por SHA256 + chattr +i. Nenhum agente pode modificá-los. |

## Architecture

### Estrutura de Diretórios
```
roadmap-estudos/
├── backend/                       # Servidor FastAPI
│   ├── main.py                    # Entry point uvicorn
│   ├── core/config.py             # Config centralizada (dirs, API key)
│   ├── models/                    # Pydantic v2 models
│   │   ├── lesson.py, quiz.py, roadmap.py, diagnosis.py
│   ├── api/
│   │   ├── routes.py              # Rotas legado (http.server)
│   │   └── routes_fastapi.py      # Rotas ativas (FastAPI APIRouter)
│   └── services/
│       ├── ai_content/            # Geração de roadmaps e lições
│       │   ├── roadmap_generator.py
│       │   └── lesson_generator.py
│       ├── diagnosis/             # Diagnóstico de conhecimento
│       ├── quiz/                  # Geração e avaliação de quizzes
│       └── dsl/                   # Motor DSL (stub)
├── frontend/public/               # SPA (HTML, CSS, JS puros)
├── data/                          # Roadmaps JSON
├── licoes/                        # Lições Markdown + quizzes embutidos
├── scripts/                       # Utilitários (validação, migração, guard)
├── tests/                         # Testes pytest
├── harness.py                     # Orquestrador de validação
└── .harness.hash                  # Hashes de arquivos protegidos
```

### Camadas de Validação
1. **Entrada da API**: Pydantic v2 models validam tipos e formatos automaticamente.
2. **Serviço**: Funções validam estado antes de chamar a OpenRouter (ex: API key presente, arquivos existem).
3. **Persistência**: Script `validate_content_format.py` valida naming, estrutura JSON e formato de quiz.
4. **Pipeline**: `harness.py` agrega lint, type check, testes, segurança, estrutura e conteúdo.

### Arquivos Protegidos
| Arquivo | Proteção | Quem pode alterar |
|---------|----------|-------------------|
| `harness.py` | SHA256 + chattr +i + git status | Mantenedor humano |
| `scripts/guard_harness.py` | SHA256 + chattr +i + git status | Mantenedor humano |
| `.harness.hash` | git status | Mantenedor humano (via --seal) |

### Gestão de Credenciais
- OpenRouter API key em `.env` (ignorado pelo git).
- Carregada via `os.environ.setdefault()` no módulo `config.py`.
- Exportada como `OPENROUTER_API_KEY` para uso nos serviços.
- `check_api_key()` valida presença antes de chamadas à API.

## Components and Interfaces

### Component 1: FastAPI Router
**Responsabilidade**: Expor endpoints REST para frontend e testes.
**Interface pública**: `APIRouter` com 9 endpoints (`/api/roadmaps`, `/api/roadmap/{id}`, `/api/dep-map`, `/api/generate-lesson`, `/api/generate-roadmap`, `/api/quiz/generate`, `/api/quiz/evaluate`, `/api/diagnose`, `/licoes/{file}`).
**Erros tratados**: HTTP 404 (arquivo não encontrado), 422 (validação Pydantic), 500 (erro interno/API).

### Component 2: Roadmap Generator
**Responsabilidade**: Gerar roadmaps de estudo via OpenRouter API e persistir em JSON.
**Interface pública**: `gerar_roadmap_ia(tema: str) -> dict`, `salvar_roadmap(roadmap: dict) -> str`.
**Erros tratados**: API key ausente, timeout da API, JSON inválido retornado pela IA.

### Component 3: Lesson Generator
**Responsabilidade**: Gerar lições Markdown com quizzes embutidos via OpenRouter API.
**Interface pública**: `gerar_conteudo_ia(topico: str, node_data: dict) -> str`, `processar_node(roadmap_id: str, node_id: str) -> str`.
**Erros tratados**: API key ausente, node não encontrado no roadmap, falha na API.

### Component 4: Quiz Service
**Responsabilidade**: Gerar e avaliar quizzes de múltipla escolha sobre lições.
**Interface pública**: `generate_quiz(lesson_content: str) -> dict`, `evaluate_quiz(quiz_data: dict, answers: list) -> dict`.
**Erros tratados**: Lição não encontrada, quiz mal formatado, API key ausente.

### Component 5: Diagnosis Service
**Responsabilidade**: Analisar gaps de conhecimento usando o mapa de dependências.
**Interface pública**: `diagnose(area: str, knowledge: str) -> dict`.
**Erros tratados**: API key ausente, dep_map.json vazio.

### Component 6: DSL Engine (stub)
**Responsabilidade**: Executar scripts DSL para fluxos de aprendizado customizados.
**Interface pública**: `execute(dsl: str) -> dict`, `validate(dsl: str) -> dict`.
**Erros tratados**: Sintaxe inválida, comandos desconhecidos.

### Component 7: Validation Harness
**Responsabilidade**: Agregar e executar todas as validações do projeto.
**Interface pública**: `python harness.py` (modos: json, lint, type, test, audit, security, structure, content).
**Erros tratados**: Exit 0 (healthy), Exit 1 (falha de validação), Exit 2 (violação de integridade).

### Component 8: UI/UX Design System — Cartographic Theme
**Responsabilidade**: Definir e aplicar o sistema de design visual "Cartographic Learning Atlas" em todo o frontend.

**Tokens de Cor (CSS `:root`)**:
```css
--bg-deep: #0f172a;
--bg-surface: #1e293b;
--bg-card: #1e293b;
--accent-primary: #f59e0b;
--accent-secondary: #d97706;
--accent-glow: rgba(245, 158, 11, 0.15);
--success: #10b981;
--text-primary: #f8fafc;
--text-secondary: #94a3b8;
--glass-bg: rgba(30, 41, 59, 0.8);
--glass-border: rgba(245, 158, 11, 0.2);
--glass-blur: blur(16px);
```

**Sistema Tipográfico**:
| Uso | Fonte | Peso | Fallback |
|-----|-------|------|----------|
| Títulos (h1-h3) | Playfair Display | 600, 700 | serifa |
| Corpo | DM Sans | 400, 500 | sans-serif |
| Código | JetBrains Mono | 400 | monospace |

**Tokens de Motion**:
```css
--motion-default: cubic-bezier(0.4, 0, 0.2, 1);
--motion-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
--duration-fast: 200ms;
--duration-normal: 300ms;
--duration-slow: 400ms;
--stagger-delay: 50ms;
```

**Matriz de Estados de Componente**:
| Componente | Loading | Empty | Error | Success |
|------------|---------|-------|-------|---------|
| Lista de Roadmaps | Shimmer skeleton (3 cards) | Ilustração + "Crie seu primeiro roadmap" | Card erro + retry | N/A (navegação) |
| Fluxograma | Skeleton dos nós + SVG tracejado | "Nenhum tópico neste roadmap" | Toast erro + "Tentar novamente" | Confete ao completar nó |
| Painel de Lição | Shimmer de texto (5 linhas) | "Selecione um tópico" | Toast erro + fallback para conteúdo local | Animação de checkmark |
| Quiz | Skeleton das perguntas | "Nenhum quiz disponível" | Toast erro + "Gerar novamente" | Score animation + confete |
| Diagnóstico | Shimmer de análise | "Informe sua área" | Toast erro + retry | Resultado com gradiente |
| Barra de Progresso | Skeleton bar | 0% — "Comece sua jornada" | N/A | Animação de preenchimento |

**Breakpoints Responsivos**:
| Nome | Largura | Comportamento |
|------|---------|---------------|
| Mobile | < 768px | Layout vertical, bottom sheet, fonte reduzida |
| Tablet | 768-1023px | Layout híbrido, painel sobreposto |
| Desktop | 1024-1919px | Layout completo, painel lateral |
| Wide | ≥ 1920px | Layout completo expandido, glow decorativo |

**Conformidade de Acessibilidade**:
- Contraste mínimo: 4.5:1 (texto normal), 3:1 (texto grande) — WCAG AA
- Focus indicator: `outline: 2px solid var(--accent-primary); outline-offset: 2px`
- `prefers-reduced-motion`: desativa animações não essenciais
- ARIA labels em todos os componentes interativos
- Ordem de tabulação natural (sem tabindex positivo)
- Landmarks: `role="navigation"`, `role="main"`, `role="complementary"`

## Error Handling Strategy

| Cenário | Componente | Resposta |
|---------|------------|----------|
| API key ausente | Todos os serviços IA | `PermissionError("API key não configurada")` |
| Arquivo não encontrado | Routers, serviços | HTTP 404 + mensagem descritiva |
| Falha OpenRouter API | Serviços IA | HTTP 500 + mensagem original do erro |
| Validação Pydantic | FastAPI Router | HTTP 422 + detalhes dos campos inválidos |
| Path traversal | Lesson endpoint | Sanitização de caminho, HTTP 400 |
| Violação de integridade | Guard Harness | Exit 2 + relatório de violações |
| Timeout de API (frontend) | UI (todos componentes) | Toast "Servidor demorou para responder" + retry |
| Falha de renderização JS | UI (fluxograma/lição) | Error boundary + "Erro ao renderizar componente" + recarregar |
| Imagem/ilustração não carrega | UI (empty states) | Fallback para placeholder SVG inline |
| Fonte não carrega (CDN down) | UI (global) | Fallback para font stack do sistema |
| Animation frame drop | UI (animações) | `requestAnimationFrame` throttling + desativar animações decorativas |
| Mobile touch event não dispara | UI (mobile) | Fallback para evento de clique |

## Testing Strategy

### Pirâmide de Testes

| Tipo | Cobertura Alvo | Ferramentas |
|------|---------------|-------------|
| Unitário | Serviços de diagnóstico, quiz, DSL | pytest, pytest-asyncio |
| Integração | Fluxos de API (mocks OpenAI) | pytest, httpx, pytest-asyncio |

### Critérios de Aceitação
- [ ] `python harness.py` retorna status "healthy" (0 erros)
- [ ] Nenhuma credencial hardcodada
- [ ] Todos os arquivos protegidos com hash válido
- [ ] Docstrings em todas as funções/classes públicas
- [ ] Lições com quizzes embutidos (mínimo 3 perguntas)

### Testes Visuais (Frontend)

| Tipo | Cobertura Alvo | Ferramentas |
|------|---------------|-------------|
| Visual/Regressão | Comparar snapshots dos componentes antes/depois | Teste manual com Lighthouse CI |
| Responsivo | 3 breakpoints: 375px, 768px, 1440px | DevTools Chrome, Teste manual |
| Acessibilidade | Contraste WCAG AA, ARIA labels, foco visível | Lighthouse, axe DevTools |
| Animações | 60fps consistentes, sem layout thrashing | Chrome DevTools Performance tab |
| Touch | Interações mobile (tap, swipe, long press) | Teste manual em dispositivo real ou emulador |

### Critérios de Aceitação (Adicionais)
- [ ] Contraste WCAG AA verificado em todas as combinações de cor
- [ ] Shimmer skeleton presente em todo carregamento assíncrono
- [ ] Navegação por teclado completa (Tab, Enter, Esc)
- [ ] `prefers-reduced-motion` desativa animações não essenciais
- [ ] Background topográfico não causa sobrecarga de renderização
- [ ] Painel de lição funciona em mobile (bottom sheet) e desktop (slide lateral)
- [ ] Busca/filtro sanitiza entrada contra XSS
