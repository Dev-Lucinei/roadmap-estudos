# CHANGELOG - Roadmap-Estudos

Este documento registra a evolução, decisões técnicas e soluções de problemas do projeto **Roadmap-Estudos**.

## [v2.3.0] - 2026-05-10
### Adicionado
- **Sistema de Proteção com Imutabilidade**: Implementado sistema consolidado de bloqueio de arquivos críticos usando `chattr +i` (imutabilidade no nível do kernel Linux) integrado ao `guard_harness.py`.
- **Comandos de Gerenciamento no guard_harness.py**:
  - `--seal` - Gera/atualiza hashes e sela arquivos com imutabilidade (requer sudo)
  - `--unlock` - Remove imutabilidade para edição (requer sudo)
  - `--status` - Verifica status de bloqueio dos arquivos
- **Hook Pre-Commit Atualizado**: Validação baseada em status de imutabilidade dos arquivos via `lsattr`, permitindo commits apenas quando arquivos foram explicitamente desbloqueados com senha.
- **Documentação Simplificada**: `GUIA_RAPIDO_SEAL.md` com workflow consolidado usando apenas o `guard_harness.py`.

### Alterado
- **Arquivos Protegidos**: `harness.py`, `scripts/guard_harness.py`, `.harness.hash` agora são protegidos por imutabilidade do sistema operacional.
- **Workflow de Modificação**: Requer desbloqueio explícito com senha antes de editar (`--unlock`), e selagem após commit (`--seal`).
- **Consolidação**: Removidos scripts bash redundantes (`seal_protected.sh`, `unseal_protected.sh`, `check_seal_status.sh`) - toda funcionalidade agora está no `guard_harness.py`.

### Memória Técnica
- O atributo `chattr +i` é uma proteção no nível do kernel que impede qualquer modificação (escrita, remoção, renomeação) mesmo para o dono do arquivo. Apenas `sudo chattr -i` pode remover a proteção, garantindo que agentes IA não possam modificar arquivos críticos sem intervenção humana com senha.
- A solução anterior com `touch .git/COMMIT_AUTHORIZED` era vulnerável pois agentes poderiam criar o arquivo de bypass. A nova abordagem requer privilégios de root para qualquer modificação.
- Consolidar tudo no `guard_harness.py` simplifica o workflow e reduz a superfície de ataque (menos arquivos para gerenciar).

## [v2.2.0] - 2026-05-10
### Corrigido
- **[P0] Path Traversal em `load_roadmap` e `handle_save_roadmap`** (`server.py`): Adicionado `os.path.basename` + `os.path.realpath` com verificação de prefixo para garantir que nenhum filename vindo da URL ou do body POST possa escapar de `DATA_DIR`. Requisições fora do diretório retornam 403.
- **[P0] XSS via `innerHTML` com dados do LLM** (`app.js`): `showReviewModal` reescrita usando criação de elementos DOM (`createElement` + `textContent`). Removidas as funções globais `handleReviewClose` e `handleReviewRetry` que dependiam de `innerHTML` com interpolação de strings não sanitizadas.
- **[P0] Validação de `Content-Length` em `do_POST`** (`server.py`): Adicionado bloco `try-except` com verificação de header ausente, valor não-numérico e limite de 1MB. Servidor retorna 411, 413 ou 400 em vez de lançar exceção não tratada.
- **[P1] Falha silenciosa de API key** (`generate_lessons.py`, `generate_roadmap.py`): Substituído `os.getenv("OPENROUTER_API_KEY", "")` por verificação explícita com `raise EnvironmentError` — o servidor falha na inicialização com mensagem clara em vez de na primeira chamada de API.
- **[P1] CORS aberto** (`server.py`): `Access-Control-Allow-Origin` alterado de `*` para `http://localhost:8000`.
- **[P1] `Content-Type` ausente em respostas de erro 500** (`server.py`): `handle_generate_lesson` e `handle_generate_roadmap` agora enviam `Content-Type: application/json` antes do body em todos os caminhos de erro.
- **[P1] Contagem cruzada de progresso em `updateProgressBar`** (`app.js`): `completedNodes.length` substituído por filtro que considera apenas nós do roadmap atual, evitando barra acima de 100%.
- **[P1] `checkQuizCompletion` com escopo global** (`app.js`): Seletor `document.querySelectorAll` substituído por `quizContainer.querySelectorAll` para isolar a contagem ao quiz da sessão atual.
- **[P1] `setInterval(drawConnections, 5000)` removido** (`app.js`): Eliminado polling periódico que forçava layout thrashing a cada 5 segundos sem nenhuma mudança no DOM.
- **[P2] `editNode` não implementado** (`app.js`): Função implementada com `prompt` para edição de título, seguida de `renderRoadmap` + `saveRoadmap`.
- **[P2] `do_DELETE` retornando 200 sem lógica** (`server.py`): Alterado para retornar 405 com body JSON.
- **[P2] Classe `.glass` ausente** (`style.css`): Definida com `backdrop-filter`, `background` e `border` consistentes com o design system.
- **[P2] `.review-modal-overlay` sem backdrop** (`style.css`): Adicionado `background: rgba(0,0,0,0.8)` para consistência com `.modal-overlay`.

### Memória Técnica
- O path traversal em `os.path.join(DATA_DIR, filename)` não é bloqueado automaticamente pelo Python — `os.path.join("/data", "../../.env")` resolve para `../../.env`. A defesa correta é `os.path.realpath` + verificação de prefixo com `os.sep` no final para evitar falsos positivos em nomes como `/data-extra`.
- `innerHTML` com dados de LLM é uma superfície de XSS real: modelos podem retornar HTML válido como parte do diagnóstico. A única defesa confiável é `textContent`.

## [v2.1.1] - 2026-05-09
### Corrigido
- **Tratamento de Erro na Inicialização**: Adicionado blocos `try...catch` robustos em `init()`, `listRoadmaps()` e `loadRoadmap()` para capturar falhas de rede, erros HTTP e arrays vazios. Mensagens de erro claras agora são exibidas no `roadmap-selector` e no container de nós quando o backend não responde ou retorna dados inválidos.

## [v2.1.0] - 2026-05-09
### Adicionado
- **Ecossistema Multi-Tema**: Suporte para carregar diferentes arquivos de roteiro a partir da pasta `data/`.
- **Servidor de Ponte (`server.py`)**: API minimalista em Python para gerenciar arquivos e integrações de IA, contornando limitações de segurança do navegador.
- **Modo Edição (CRUD UI)**: Interface para adicionar, editar e excluir nós diretamente no roadmap visual.
- **Geração de IA Integrada**: Botões na interface para disparar a criação de lições, quizzes e roadmaps completos via OpenRouter/OpenAI.

## [v2.1.1] - 2026-05-10
### Corrigido
- **Tratamento de erro na inicialização**: Adicionada função `loadDepMap()` para pré-carregar o mapa de dependências, blocos `try...catch` em `init()`, `listRoadmaps()` e `loadRoadmap()` para capturar falhas de rede, erros HTTP e arrays vazios, exibindo mensagens de erro claras na UI e evitando que o aplicativo trave silenciosamente.

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
