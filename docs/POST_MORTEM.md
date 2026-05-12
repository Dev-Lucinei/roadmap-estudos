# 🧠 Relatório de Lições Aprendidas: Roadmap-Estudos

## 1. Contexto da Falha
Tentativa de evolução do portal para um sistema gamificado com módulos ES6 e automação de quizzes. O sistema enfrentou falhas críticas de carregamento de dados e conteúdo, resultando em regressões de interface.

## 2. Análise de Causa Raiz
- **Infraestrutura**: `http.server` (Python) incompatível com Módulos ES6 em ambiente local (MIME type errors).
- **Escopo**: Variáveis `const` isoladas entre scripts não modulares.
- **Race Conditions**: Tentativa de renderização antes da carga de dados síncronos.

## 3. Protocolo de Evitação (NÃO FAZER)
- ❌ Não usar `import/export` no JS.
- ❌ Não declarar dados globais apenas com `const`; usar `window.roadmapData`.
- ❌ Não fragmentar o carregamento de scripts essenciais com `async` se houver dependência de ordem.

## 4. Caminho de Sucesso Validado
- ✅ Carregamento sequencial: `roadmap_data.js` -> `app.js`.
- ✅ Injeção de dados via objeto `window`.
- ✅ Fallback de conteúdo: embutir lições críticas no `app.js` para evitar falhas de `fetch`.

## 5. Snapshot do Estado Atual
- **Git HEAD**: `0dc35b5` (Estável).
- **Estrutura**: Roadmap visual funcional, conexões SVG operacionais.
- **Ponto de Retomada**: Implementar Quizzes e Zen Mode via escopo global.

---
*Documentação gerada pelo Agente Antigravity para continuidade de estado.*
