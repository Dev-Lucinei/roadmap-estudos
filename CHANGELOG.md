# CHANGELOG - Roadmap-Estudos

Este documento registra a evolução, decisões técnicas e soluções de problemas do projeto **Roadmap-Estudos**.

## [v2.1.1] - 2026-05-09
### Corrigido
- **Tratamento de Erro na Inicialização**: Adicionado blocos `try...catch` robustos em `init()`, `listRoadmaps()` e `loadRoadmap()` para capturar falhas de rede, erros HTTP e arrays vazios. Mensagens de erro claras agora são exibidas no `roadmap-selector` e no container de nós quando o backend não responde ou retorna dados inválidos.

## [v2.1.0] - 2026-05-09
### Adicionado
- **Ecossistema Multi-Tema**: Suporte para carregar diferentes arquivos de roteiro a partir da pasta `data/`.
- **Servidor de Ponte (`server.py`)**: API minimalista em Python para gerenciar arquivos e integrações de IA, contornando limitações de segurança do navegador.
- **Modo Edição (CRUD UI)**: Interface para adicionar, editar e excluir nós diretamente no roadmap visual.
- **Geração de IA Integrada**: Botões na interface para disparar a criação de lições, quizzes e roadmaps completos via OpenRouter/OpenAI.

### Corrigido
- **Scroll Unificado**: Conteúdo da lição e Quiz agora compartilham o mesmo container de scroll, evitando que o quiz fique inacessível em textos longos.
- **Compatibilidade Mermaid**: Ajuste no renderer do `marked.js` para suportar a API v11+, corrigindo o erro onde diagramas apareciam como `[object Object]`.
- **Erro de Porta Ocupada**: Adicionado `allow_reuse_address = True` no servidor socket para permitir reinicializações rápidas.

## [v1.5.0] - 2026-05-08
### Adicionado
- **Gamificação**: Sistema de Streaks diários e Quizzes de validação.
- **Modo Zen**: Interface focada para leitura de lições.
- **Persistência Local**: Uso de `localStorage` para salvar progresso e streaks.

### Mudanças de Arquitetura (Decisões Críticas)
- **Migração para Escopo Global**: Abandonamos ES6 Modules (`import/export`) em favor de scripts globais (`window.roadmapData`).
    - **Motivo**: Servidores locais simples (`http.server`) e abertura direta de arquivos falhavam com erros de MIME Type e CORS. O escopo global garante que o projeto funcione em qualquer ambiente de desenvolvimento sem configuração complexa.

## [v1.0.0] - Inicial
### Adicionado
- Estrutura base com HTML/CSS e renderização de conexões dinâmicas via SVG.
- Suporte inicial para Markdown e Mermaid.js.

---

## 🧠 Registro de Decisões e Prevenção de Regressões

### 1. Por que não usar Streamlit no Portal?
Embora o Streamlit seja usado em outros módulos do projeto (como o Chatbot), decidimos manter o Roadmap em **HTML/JS puro** para ter controle total sobre o **SVG dinâmico** e as animações de conexões. O Streamlit é muito rígido para a interface visual complexa que o roadmap exige.

### 2. Por que o Servidor Python (`server.py`) é necessário?
O navegador bloqueia (por segurança) que um site salve arquivos diretamente no seu computador ou faça requisições para arquivos locais (`file://`). O `server.py` atua como uma ponte de confiança, permitindo que a interface peça à IA para "escrever" uma nova lição na pasta `/licoes`.

### 3. O Problema do "Address already in use"
Sempre que o servidor for reiniciado bruscamente, a porta 8000 pode ficar presa. O uso do comando `fuser -k 8000/tcp` ou a flag `allow_reuse_address` no Python é vital para evitar travamentos no fluxo de desenvolvimento.

### 4. Manutenção do Quiz
O Quiz é extraído via Regex do final dos arquivos Markdown. Ao editar o script de geração de IA, o formato do bloco de código JSON ` ```json [...] ``` ` deve ser estritamente mantido para não quebrar o parser do frontend.
