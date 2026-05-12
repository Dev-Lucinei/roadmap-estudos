# Matriz de Impacto Especificação-Componente

## Visão Geral

Esta matriz mapeia como cada componente do sistema impacta e é impactado por outros componentes, funcionalidades e requisitos.

---

## Matriz de Impacto Componente × Funcionalidade

| Componente | Geração de Roadmap | Geração de Lição | Quiz | Diagnóstico | Persistência | API REST |
|------------|-------------------|------------------|------|-------------|--------------|----------|
| **RoadmapHandler** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **QuizService** | - | - | ⭐⭐⭐ | - | ⭐ | - |
| **DiagnosisService** | - | - | - | ⭐⭐⭐ | ⭐ | - |
| **generate_roadmap** | ⭐⭐⭐ | - | - | - | ⭐⭐ | - |
| **generate_lessons** | - | ⭐⭐⭐ | - | - | ⭐⭐ | - |
| **Sistema de Arquivos** | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | - |
| **OpenRouter API** | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | - | - |

**Legenda**: ⭐⭐⭐ = Alto impacto | ⭐⭐ = Médio impacto | ⭐ = Baixo impacto | - = Sem impacto direto

---

## Matriz de Impacto Componente × Componente

### Fluxo de Impacto

```
OpenRouter API
     │
     ├─── impacta ───> QuizService
     │                    │
     │                    └─── impacta ───> RoadmapHandler
     │
     ├─── impacta ───> DiagnosisService
     │                    │
     │                    └─── impacta ───> RoadmapHandler
     │
     ├─── impacta ───> generate_roadmap
     │                    │
     │                    └─── impacta ───> RoadmapHandler
     │
     └─── impacta ───> generate_lessons
                          │
                          └─── impacta ───> RoadmapHandler

Sistema de Arquivos
     │
     ├─── impacta ───> RoadmapHandler (leitura/escrita)
     ├─── impacta ───> QuizService (leitura de lições)
     ├─── impacta ───> generate_roadmap (leitura/escrita)
     └─── impacta ───> generate_lessons (leitura/escrita)

Frontend Web
     │
     └─── impacta ───> RoadmapHandler (chamadas API)
```

---

## Especificação de Impacto por Funcionalidade

### 1. Geração de Roadmap

| Componente | Impacto | Tipo de Impacto |
|------------|---------|-----------------|
| RoadmapHandler | Exposed | Consome serviço via `/api/generate-roadmap` |
| generate_roadmap | Provider | Gera estrutura JSON do roadmap |
| OpenRouter API | Dependência | Fornece conteúdo para geração |
| Sistema de Arquivos | Dependência | Salva roadmap em `/data/` |

**Fluxo**: Usuário → RoadmapHandler → generate_roadmap → OpenRouter API → RoadmapHandler → Sistema de Arquivos

---

### 2. Geração de Lição

| Componente | Impacto | Tipo de Impacto |
|------------|---------|-----------------|
| RoadmapHandler | Exposed | Consome serviço via `/api/generate-lesson` |
| generate_lessons | Provider | Gera conteúdo Markdown da lição |
| OpenRouter API | Dependência | Fornece conteúdo educacional |
| Sistema de Arquivos | Dependência | Salva lição em `/licoes/` |

**Fluxo**: Usuário → RoadmapHandler → generate_lessons → OpenRouter API → generate_lessons → Sistema de Arquivos

---

### 3. Sistema de Quiz

| Componente | Impacto | Tipo de Impacto |
|------------|---------|-----------------|
| RoadmapHandler | Exposed | Endpoints `/api/generate-quiz` e `/api/evaluate-quiz` |
| QuizService | Provider | Gera e avalia quizzes |
| generate_lessons | Dependência | Lição contém quiz EMBUTIDO |
| Sistema de Arquivos | Leitura | Lê conteúdo da lição para contexto |
| OpenRouter API | Dependência | Gera e avalia quiz |

**Fluxo Quiz**: Usuário → RoadmapHandler → QuizService.generate_quiz() → OpenRouter API → QuizService → Usuário

**Fluxo Avaliação**: Usuário → RoadmapHandler → QuizService.evaluate_quiz() → OpenRouter API → QuizService → Usuário

---

### 4. Diagnóstico de Lacunas

| Componente | Impacto | Tipo de Impacto |
|------------|---------|-----------------|
| RoadmapHandler | Exposed | Endpoint `/api/diagnose` |
| DiagnosisService | Provider | Realiza diagnóstico |
| DependencyMap | Leitura | Mapa de pré-requisitos |
| Sistema de Arquivos | Leitura | Lê `/data/dep_map.json` |
| OpenRouter API | Dependência | Gera diagnóstico |

**Fluxo**: Usuário → RoadmapHandler → DiagnosisService → Sistema de Arquivos (dep_map) → OpenRouter API → DiagnosisService → Usuário

---

## Cadeia de Impacto em Cascata

### Cascata de Falha: OpenRouter API Indisponível

```
OpenRouter API (falha)
     │
     ├──× QuizService.generate_quiz() ──× falha
     ├──× QuizService.evaluate_quiz() ──× falha
     ├──× DiagnosisService.diagnose() ──× falha
     ├──× generate_roadmap() ──× falha
     └──× generate_lessons() ──× falha

Impacto Final:
- /api/generate-quiz → ERRO 502
- /api/evaluate-quiz → ERRO 502
- /api/diagnose → ERRO 502
- /api/generate-roadmap → ERRO 500
- /api/generate-lesson → ERRO 500
```

### Cascata de Falha: Sistema de Arquivos Indisponível

```
Sistema de Arquivos (falha)
     │
     ├──× Leitura de lições ──× falha
     ├──× Escrita de roadmaps ──× falha
     └──× Leitura de dep_map ──× falha

Impacto Final:
- /api/generate-quiz → ERRO 500 (não consegue ler lição)
- /api/diagnose → ERRO 500 (não consegue ler dep_map)
- /api/generate-roadmap → ERRO 500 (não consegue salvar)
- /api/save-roadmap → ERRO 500
```

---

## Matriz de Dependência de Dados

### Fluxo de Dados entre Componentes

| Dados | Origem | Destino | Formato |
|-------|--------|---------|---------|
| Roadmap JSON | generate_roadmap | Sistema de Arquivos | JSON |
| Lições Markdown | generate_lessons | Sistema de Arquivos | Markdown |
| Quiz JSON | OpenRouter API | QuizService | JSON |
| Avaliação | OpenRouter API | QuizService | JSON |
| Diagnóstico | OpenRouter API | DiagnosisService | JSON |
| dep_map | Sistema de Arquivos | DiagnosisService | JSON |

---

## Pontos Críticos de Impacto

### 1. OpenRouter API (Single Point of Failure)

**Impacto**: Se indisponível, todas as funcionalidades de geração falham.

**Mitigação Recomendada**:
- Implementar cache de requisições frequentes
- Adicionar retry com backoff exponencial
- Permitir fallback para modelo alternativo
- Considerar rate limiting para evitar consumo excessivo

---

### 2. Sistema de Arquivos (I/O Bloqueante)

**Impacto**: Operações de I/O bloqueiam o servidor HTTP síncrono.

**Mitigação Recomendada**:
- Para escala maior, migrar para banco de dados assíncrono
- Implementar pooling de threads para operações de I/O
- Considerar cache em memória para dados frequentes

---

### 3. RoadmapHandler (Acoplamento Alto)

**Impacto**: Centraliza muita lógica, difícil de testar e manter isolado.

**Mitigação Recomendada**:
- Extrair validações para classes/serviços dedicados
- Implementar testes unitários para cada service
- Considerar padrão de arquitetura em camadas

---

## Spec Impact Summary

| Requisito | Componentes Impactados | Complexidade |
|-----------|----------------------|--------------|
| FR01: Visualizar roadmaps | RoadmapHandler, Frontend | Baixa |
| FR02: Gerar roadmap por tema | RoadmapHandler, generate_roadmap, OpenRouter | Alta |
| FR03: Gerar lições | RoadmapHandler, generate_lessons, OpenRouter | Alta |
| FR04: Resolver quiz | RoadmapHandler, QuizService, OpenRouter | Alta |
| FR05: Diagnosticar lacunas | RoadmapHandler, DiagnosisService, OpenRouter | Alta |
| FR06: Salvar roadmaps | RoadmapHandler, Sistema de Arquivos | Média |
| FR07: Regenerar dep_map | RoadmapHandler, Sistema de Arquivos | Baixa |

**Legenda**:
- FR = Requisito Funcional
- Alta = Múltiplas dependências externas, lógica complexa
- Média = Algumas dependências, lógica moderada
- Baixa = Poucas dependências, lógica simples