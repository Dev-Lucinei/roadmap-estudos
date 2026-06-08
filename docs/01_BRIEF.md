# 01_BRIEF.md — Briefing do Problema de Negócio

**Projeto**: Roadmap-Estudos
**Data**: 2026-06-08

---

## 1. O que o projeto resolve

O **Roadmap-Estudos** é um **Sistema de Gestão de Aprendizado (LMS) Pessoal** que transforma roteiros técnicos estáticos — inspirados no [roadmap.sh](https://roadmap.sh) — em uma plataforma de estudo interativa e automatizada.

O sistema resolve os seguintes problemas:

- **Falta de estrutura**: Estudantes possuem roadmaps em texto/JSON mas não conseguem visualizar relações de dependência entre tópicos de forma intuitiva.
- **Conteúdo estático**: Roadmaps são listas passivas; não há geração automática de lições, quizzes ou diagnósticos.
- **Falta de feedback**: Não há mecanismo para avaliar conhecimento ou identificar gaps de aprendizado.
- **Experiência fragmentada**: O estudante precisa alternar entre múltiplas ferramentas (roadmap + editor + quiz + anotações).

## 2. Por que existe

O projeto nasceu da necessidade de **transformar o roadmap.sh em uma plataforma interativa** que:

1. **Visualiza** a hierarquia de tópicos com conexões dinâmicas (SVG, fluxograma).
2. **Gera conteúdo automaticamente** via IA (lições em Markdown) a partir de metas de estudo.
3. **Avalia conhecimento** via quizzes gerados dinamicamente pela IA.
4. **Diagnostica gaps** de conhecimento cruzando respostas do usuário com o mapa de dependências.
5. **Persiste progresso** localmente, mantendo o estudante engajado com streaks e gamificação.

A motivação central é **democratizar o acesso a um plano de estudo estruturado**, eliminando a barreira de criar e manter conteúdo manualmente.

## 3. Stakeholders

| Stakeholder | Papel | Responsabilidades |
|-------------|-------|-------------------|
| **Desenvolvedor pessoal** (Lucinei) | Product Owner + Developer | Definir requisitos, desenvolver, testar e manter o sistema |
| **IA (OpenRouter API)** | Gerador de conteúdo | Gerar lições, quizzes e diagnósticos sob demanda |
| **Usuário final** (mesmo desenvolvedor) | Estudante | Utilizar a plataforma para aprendizado |

> Nota: Este é um projeto pessoal com stakeholder único. Não há equipe multidisciplinar.

## 4. Contexto

### 4.1 Ambiente
- **Plataforma**: Aplicação web fullstack (FastAPI + HTML/CSS/JS vanilla)
- **Linguagem**: Python 3.11+ (backend), JavaScript ES6+ (frontend)
- **Hospedagem**: Servidor local (`localhost:8000`)
- **Dependência externa**: OpenRouter API (para geração de conteúdo via IA)

### 4.2 Restrições técnicas
- **Frontend em escopo global**: Não usar ES6 Modules (`import/export`) devido a limitações de servidores locais e CORS.
- **Persistência em arquivos**: JSON para roadmaps, Markdown para lições — sem banco de dados relacional.
- **Custo de API**: Cada chamada à OpenRouter gera custo; prompts devem ser otimizados (max_tokens, temperatura).
- **Porta 8000 fixa**: Servidor local; conflitos devem ser resolvidos com `fuser -k 8000/tcp`.

### 4.3 Restrições de negócio
- **Projeto pessoal**: Sem orçamento para infraestrutura externa.
- **Conteúdo gerado por IA**: Qualidade variável; exigir validação humana para conteúdo crítico.
- **Single-tenant**: Apenas um usuário; não há necessidade de autenticação ou multi-tenancy.

### 4.4 Concorrência / Alternativas
| Alternativa | Limitação |
|-------------|-----------|
| roadmap.sh (original) | Estático, sem geração de conteúdo, sem quizzes |
| Notion / Obsidian | Manual, sem IA integrada, sem gamificação |
| Coursera / Udemy | Pago, conteúdo pré-definido, sem personalização |

O Roadmap-Estudos se diferencia por ser **gratuito, personalizado e com IA integrada**.
