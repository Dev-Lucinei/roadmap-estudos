# CHANGELOG - Roadmap-Estudos

Este documento registra a evolução, decisões técnicas e soluções de problemas do projeto **Roadmap-Estudos**.

## [v2.9.0] - 2026-05-10
### Adicionado
- **Sistema de Avaliação de Conhecimento via Quiz IA**: Implementado fluxo completo de geração e avaliação de quizzes.
  - Botão "🧠 Gerar Quiz" no painel de lições
  - Backend: `QuizService` com métodos `generate_quiz()` e `evaluate_quiz()`
  - Endpoints API: `/api/generate-quiz` e `/api/evaluate-quiz`
  - Frontend: Interface de quiz com radio buttons e validação de respostas
  - Avaliação assertiva via IA com feedback detalhado por questão
  - Sistema de pontuação (0-100%) e status aprovado/reprovado
  - Proteção contra prompt injection e desvio de contexto

### Alterado
- **Geração de Perguntas**: Quiz gerado exclusivamente com base no conteúdo da lição atual (máx 2000 chars)
- **Formato de Resposta**: Múltipla escolha com 4 alternativas por questão
- **Feedback Otimizado**: Limitado a 150 palavras para economia de tokens
- **Interface de Avaliação**: Exibe score, feedback geral e detalhes por questão com respostas corretas

### Memória Técnica
- Problema: Necessidade de avaliar conhecimento do usuário antes de avançar no roadmap
- Solução: Sistema de quiz gerado dinamicamente pela IA baseado no conteúdo específico da lição
- Segurança: Prompts restritivos que bloqueiam tentativas de manipulação ou desvio de contexto
- Validação: Backend valida estrutura JSON e frontend valida preenchimento completo
- UX: Botões de "Tentar Novamente" e "Marcar como Concluído" (apenas se aprovado)
- Resultado: Experiência fluida de teste de conhecimento com feedback construtivo e seguro

## [v2.8.6] - 2026-05-10
### Corrigido
- **Subtópicos Cortados no Topo**: Adicionada verificação de margem mínima para `subtopicStartY`.
  - Se `subtopicStartY < minTopMargin (100px)`, ajusta para `minTopMargin`
  - Previne que subtópicos sejam empurrados para cima e fiquem ocultos
  - Mesma lógica aplicada ao nó central agora também protege subtópicos

### Memória Técnica
- Problema: `subtopicStartY = adjustedY - (maxHeight / 2)` podia resultar em Y negativo ou muito pequeno
- Quando nó tem muitos subtópicos com sub-subtópicos, `maxHeight` é grande, empurrando início para cima
- Solução: `if (subtopicStartY < 100) { subtopicStartY = 100 }`
- Resultado: Todos os elementos sempre visíveis, respeitando margem superior

## [v2.8.5] - 2026-05-10
### Corrigido
- **Sistema de Posicionamento Sequencial**: Implementado cálculo incremental que previne sobreposição de containers.
  - Cada subtópico é posicionado **após** o anterior (não mais centralizado fixo)
  - `currentY` incrementa com altura real ocupada (60px + sub-subtópicos + gaps)
  - Calcula altura total de cada lado (esquerda/direita) para centralização correta
  - Sub-subtópicos posicionados sequencialmente abaixo do pai

### Alterado
- **Lógica de Posicionamento**: De "centralizado com gap fixo" para "sequencial com altura dinâmica"
- **Cálculo de Espaço**: 
  - Subtópico: 60px altura + 40px gap
  - Sub-subtópicos: 20px offset + (n * 80px)
  - Altura total calculada antes do posicionamento

### Memória Técnica
- Problema: Centralização com gap fixo (`idx * 100`) não considerava altura real dos sub-subtópicos
- Solução: Sistema incremental onde `currentY += alturaReal` após cada elemento
- Função `calculateSideHeight()` pré-calcula espaço total necessário para centralização
- Resultado: Cada container ocupa seu espaço exclusivo, sem sobreposição

## [v2.8.4] - 2026-05-10
### Corrigido
- **Sobreposição de Sub-subtópicos**: Corrigido cálculo de altura na Fase 1 para considerar corretamente sub-subtópicos expandidos.
  - Altura de subtópico com filhos expandidos: `80 + (quantidade * 80)` (antes era `60 + (quantidade * 60)`)
  - Alinhado com o cálculo real de posicionamento na Fase 2
  - Previne sobreposição quando múltiplos subtópicos têm filhos expandidos

### Memória Técnica
- Problema: Fase 1 calculava `subtopicHeight = 60 + (n * 60)` mas Fase 2 posicionava com `80 + (n * 80)`
- Desalinhamento causava cálculo de altura insuficiente, resultando em sobreposição
- Solução: Sincronizar cálculos usando mesmos valores (80px offset + 80px gap)
- Resultado: Espaço correto reservado para sub-subtópicos, sem sobreposição

## [v2.8.3] - 2026-05-10
### Corrigido
- **Espaçamento Uniforme de Subtópicos**: Ajustado cálculo de posicionamento para garantir distância consistente entre containers.
  - Gap uniforme de 100px entre subtópicos (antes variava)
  - Gap uniforme de 80px entre sub-subtópicos
  - Centralização corrigida: `subtopicStartY = adjustedY - ((total - 1) * gap / 2)`
  - Offset inicial de sub-subtópicos ajustado para 80px

### Memória Técnica
- Problema: Centralização usava `* 40` mas espaçamento usava `* 90`, causando irregularidade
- Solução: Variável `subtopicGap = 100` usada tanto para centralização quanto para espaçamento
- Fórmula de centralização: divide o espaço total por 2 para centralizar em relação ao nó pai
- Resultado: Distância visual uniforme entre todos os containers de subtópicos

## [v2.8.2] - 2026-05-10
### Corrigido
- **Espaçamento Equilibrado entre Nós**: Implementado cálculo de espaçamento baseado na média das alturas de nós adjacentes.
  - Quando nó expandido é seguido por nó recolhido: espaço reduzido (não mais sobreposição)
  - Quando nó recolhido é seguido por nó expandido: espaço aumentado (não mais gap excessivo)
  - Fórmula: `avgHeight = (alturaAtual + alturaProxima) / 2`

### Memória Técnica
- Problema: `currentY += requiredHeight + minGap` usava apenas a altura do nó atual, causando:
  - Gap excessivo quando nó expandido era seguido por recolhido
  - Sobreposição quando nó recolhido era seguido por expandido
- Solução: Calcular média das alturas de nós adjacentes para espaçamento equilibrado
- Resultado: Transições suaves entre nós expandidos e recolhidos

## [v2.8.1] - 2026-05-10
### Corrigido
- **Corte de Subtópicos no Topo**: Implementado ajuste automático de posição do nó central quando subtópicos ficariam acima da margem segura.
  - Margem mínima de 100px do topo garantida
  - Nó central é deslocado para baixo automaticamente se necessário
  - Subtópicos sempre visíveis, mesmo ao expandir o primeiro nó

### Memória Técnica
- Problema: Quando o primeiro nó central estava em Y=150 e tinha muitos subtópicos, eles ficavam centralizados acima dele (Y < 100) e eram cortados pelo header.
- Solução: Antes de posicionar, calcula onde os subtópicos ficariam. Se `subtopicStartY < minTopMargin`, ajusta o Y do nó central para baixo.
- Fórmula: `adjustedY = currentY + (minTopMargin - subtopicStartY)`

## [v2.8.0] - 2026-05-10
### Adicionado
- **Algoritmo de Layout Adaptativo**: Sistema robusto que calcula espaçamento dinamicamente baseado no conteúdo real.
  - **Fase 1**: Pré-calcula altura necessária para cada nó central
  - **Fase 2**: Posiciona nós com espaçamento mínimo necessário (60px quando recolhido)
  - **Centralização Vertical**: Subtópicos são centralizados em relação ao nó pai
  - **Escalabilidade**: Funciona automaticamente para qualquer roadmap futuro

### Alterado
- **calculateLayout()**: Reescrito completamente com algoritmo em duas fases
- **Espaçamento Dinâmico**: 
  - Nós recolhidos: 60px de gap (antes era 100-180px fixo)
  - Nós expandidos: Espaço calculado baseado no número real de subtópicos
  - Subtópicos: 90px de gap vertical
  - Sub-subtópicos: 60px de gap vertical

### Memória Técnica
- **Problema Anterior**: Espaçamento fixo desperdiçava espaço e não se adaptava a diferentes roadmaps.
- **Solução Nova**: 
  1. Primeira passada calcula altura necessária para cada nó (considerando expansão)
  2. Segunda passada posiciona nós usando apenas o espaço necessário
  3. Subtópicos são centralizados verticalmente em relação ao pai
- **Benefícios**:
  - Roadmaps recolhidos são extremamente compactos (60px gap)
  - Roadmaps expandidos usam exatamente o espaço necessário
  - Funciona para 3 nós ou 30 nós sem ajustes manuais
  - Centralização vertical melhora estética e legibilidade

## [v2.7.2] - 2026-05-10
### Corrigido
- **Espaçamento Compacto**: Reduzido drasticamente o espaçamento entre nós principais.
  - `baseVerticalGap` reduzido de 180px para 100px
  - Espaçamento de subtópicos reduzido de 120px para 100px
  - Espaçamento de sub-subtópicos reduzido de 80px para 70px
- **Corte no Topo**: Padding superior aumentado de 60px para 100px e `startY` de 150px para 200px.
- **Layout Mais Compacto**: Todos os espaçamentos ajustados para melhor aproveitamento da tela.

### Memória Técnica
- O espaçamento anterior (180px base) era excessivo, forçando zoom out extremo para visualizar roadmaps completos.
- Novo espaçamento (100px base) mantém legibilidade enquanto permite visualização de mais conteúdo.
- Padding superior de 100px garante que o primeiro nó não seja cortado pelo header fixo mesmo em zoom reduzido.

## [v2.7.1] - 2026-05-10
### Corrigido
- **Erro Crítico de Sintaxe**: Arquivo `flowchart_layout.js` estava corrompido com código duplicado, impedindo o carregamento.
  - Arquivo recriado do zero com estrutura limpa
  - Sintaxe validada com Node.js
- **Espaçamento Dinâmico**: Nós recolhidos agora ficam próximos uns dos outros, expandindo suavemente quando abertos.
  - Gap vertical reduzido de 600px para 180px base
  - Espaçamento calculado dinamicamente baseado no estado de expansão
  - Nós expandidos recebem espaço adicional proporcional ao número de subtópicos
- **Corte no Topo**: Aumentado padding superior do container de 40px para 60px e `startY` de 100px para 150px.
- **Altura do SVG**: Cálculo ajustado para considerar altura dos nós (`maxY + height`) e garantir margem inferior adequada.
- **Transições Suaves**: 
  - Animação de entrada melhorada com `cubic-bezier(0.4, 0, 0.2, 1)`
  - Scroll suave habilitado com `scroll-behavior: smooth`
  - Duração de animação ajustada para 0.5s nos nós

### Memória Técnica
- O espaçamento fixo anterior (`verticalGap * 3 = 600px`) desperdiçava espaço quando nós estavam recolhidos.
- Nova abordagem usa `currentY` incremental que soma apenas o espaço necessário: `nodeHeight + baseGap + additionalSpace`.
- `additionalSpace` é calculado dinamicamente: `Math.max(subtopicCount * 120, 200)` quando expandido, 0 quando recolhido.
- Padding superior aumentado evita que o primeiro nó fique cortado pelo header fixo.

## [v2.7.0] - 2026-05-10
### Adicionado
- **Expansão/Recolhimento Interativo**: Sistema completo de expandir/recolher nós no layout de fluxograma.
  - Click em nós com subtópicos expande/recolhe seus filhos
  - Ícone visual (▶) que rotaciona ao expandir
  - Botões "📂 Expandir" e "📁 Recolher" no header para controle global
  - Double-click sempre abre a lição, independente de ter subtópicos
- **Layout Único**: Removido layout de árvore, mantendo apenas o fluxograma como padrão.
- **Indicadores Visuais**: Barra inferior nos nós recolhidos indicando que há conteúdo oculto.

### Alterado
- **flowchart_layout.js**: 
  - Adicionado `expandedNodes` Set para rastrear estado de expansão
  - Método `toggleNode()` para expandir/recolher
  - Renderização condicional baseada em estado de expansão
- **flowchart_layout.css**: Estilos para ícone de expansão e indicadores visuais
- **app.js**: 
  - `renderRoadmap()` usa apenas fluxograma
  - Funções `expandAllNodes()` e `collapseAllNodes()`
  - Removida lógica de alternância de layout
- **index.html**: Botões de expandir/recolher substituem botão de alternância

### Memória Técnica
- O estado de expansão é mantido em um `Set` para lookup O(1)
- Re-renderização completa ao expandir/recolher garante posicionamento correto
- Nós sem subtópicos abrem lição diretamente no click
- Nós com subtópicos requerem double-click para abrir lição (single click expande)
- O sistema preserva nós completos após re-renderização via timeout

## [v2.6.0] - 2026-05-10
### Adicionado
- **Layout de Fluxograma Profissional**: Novo modo de visualização tipo mindmap/fluxograma com conexões visuais entre nós.
  - Nós centrais no centro da tela
  - Subtópicos distribuídos em colunas esquerda/direita alternadamente
  - Sub-subtópicos expandem para as laterais externas
  - Conexões SVG com curvas bezier suaves
- **Alternância de Layout**: Botão "🔀 Layout" para alternar entre modo árvore e modo fluxograma.
- **Arquivos Criados**:
  - `flowchart_layout.js` - Sistema de renderização de fluxograma
  - `flowchart_layout.css` - Estilos profissionais para o layout de fluxograma
  - `test_flowchart.html` - Demonstração completa do novo layout
- **Integração Completa**: Sistema de fluxograma integrado ao `app.js` e `index.html` principal.

### Alterado
- **index.html**: Adicionado container de fluxograma e botão de alternância de layout.
- **app.js**: Adicionada função `toggleLayoutMode()` para alternar entre layouts.

### Memória Técnica
- O layout de fluxograma usa posicionamento absoluto calculado dinamicamente baseado na hierarquia dos nós.
- Conexões SVG são desenhadas usando curvas quadráticas bezier para aparência profissional.
- O sistema mantém a estilização glass morphism existente para consistência visual.
- Nós são distribuídos alternadamente (esquerda/direita) para balancear o layout e aproveitar espaço horizontal.
- A classe `FlowchartLayout` é independente e pode ser reutilizada em outros projetos.

## [v2.5.0] - 2026-05-10
### Adicionado
- **Sistema de Expansão Inteligente**: Layout adaptativo que aproveita melhor o espaço da tela em diferentes níveis de hierarquia.
  - **Nível 1**: Subtópicos expandem HORIZONTALMENTE (esquerda/direita)
  - **Nível 2+**: Subtópicos expandem VERTICALMENTE (cima/baixo)
- **Arquivo de Teste**: `test_expansion_layout.html` para visualizar e testar o novo sistema de expansão.
- **Responsividade Aprimorada**: Em telas menores (< 1200px), o layout força expansão vertical para melhor usabilidade.

### Alterado
- **CSS de Subtópicos**: Refatorado `.node-subtopics-tree` para suportar `flex-direction` dinâmica baseada em `data-level`.
- **Conectores Visuais**: Linhas de conexão adaptadas para layout horizontal (nível 1) e vertical (níveis 2+).
- **Tamanhos de Nós**: Ajustados progressivamente por nível (nível 1: 240px, nível 2: 200px, nível 3: 180px).

### Memória Técnica
- O layout anterior expandia todos os níveis verticalmente, desperdiçando espaço horizontal em telas grandes.
- A nova abordagem usa `flex-direction: row` no primeiro nível de subtópicos e `flex-direction: column` nos níveis subsequentes.
- Os conectores visuais (linhas) foram adaptados: verticais para layout horizontal, horizontais para layout vertical.
- O atributo `data-level` já existente no código foi aproveitado para aplicar estilos específicos via CSS.

## [v2.4.0] - 2026-05-10
### Adicionado
- **Padrão JSON Unificado**: Documentação oficial em `docs/PADRAO_JSON_ROADMAP.md` definindo estrutura v2.0 para roadmaps.
- **Estrutura Hierárquica com `subtopics`**: Nova estrutura usando objetos aninhados em vez de referências por ID (`children`), permitindo múltiplos níveis de profundidade nativamente.
- **Script de Migração**: `scripts/migrate_roadmap_structure.py` para converter automaticamente arquivos do formato antigo (`children` + `side`) para o novo formato (`subtopics`).

### Alterado
- **Formato Oficial**: `roadmap_exemplo_arvore.json` agora é a referência oficial da estrutura. O formato antigo (`python_fundamentos.json`) ainda é suportado para retrocompatibilidade, mas está descontinuado.

### Memória Técnica
- A estrutura antiga usava `children` (array de IDs) que exigia duplicação de nós no array principal, tornando a manutenção complexa e propensa a erros de referência.
- A nova estrutura com `subtopics` aninhados é mais intuitiva, reduz redundância e permite hierarquias ilimitadas sem necessidade de campos auxiliares como `side`.
- O campo `side` ("left"/"right") foi removido da estrutura oficial, mas pode ser calculado dinamicamente no frontend se necessário para layout.

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
