# Requirements Document: Roadmap-Estudos

## Requisito R.1: Gerenciamento de Roadmaps
**User Story:** Como um estudante, eu quero criar, listar e visualizar roadmaps de estudo, para que eu possa organizar meu aprendizado em tópicos estruturados.

**Acceptance Criteria (EARS):**
- WHEN o usuário acessa a página inicial, THEN a lista de roadmaps disponíveis é exibida.
- WHEN o usuário clica em um roadmap, THEN a árvore de tópicos é renderizada com fluxograma expansível.
- WHEN o usuário preenche o modal de novo roadmap, THEN um novo roadmap é gerado via IA e salvo em JSON.
- WHEN um roadmap é criado, THEN ele deve seguir o schema PADRAO_JSON_ROADMAP (v2.0) com `subtopics` aninhados.
- WHEN roadmaps são carregados, THEN o sistema deve ler do diretório `data/` arquivos JSON.

## Requisito R.2: Geração de Lições com IA
**User Story:** Como um estudante, eu quero gerar lições detalhadas sobre tópicos específicos, para que eu possa aprender com conteúdo personalizado.

**Acceptance Criteria (EARS):**
- WHEN o usuário solicita uma lição para um tópico, THEN o sistema chama a OpenRouter API para gerar o conteúdo.
- WHEN a lição é gerada, THEN ela é salva como arquivo Markdown em `licoes/`.
- WHEN a lição contém um quiz, THEN o quiz é extraído via Regex do bloco ```json no final do .md.
- WHEN o conteúdo é gerado, THEN deve incluir seções de introdução, desenvolvimento, exemplos e exercícios.

## Requisito R.3: Sistema de Quiz
**User Story:** Como um estudante, eu quero responder quizzes sobre as lições e receber feedback, para que eu possa validar meu aprendizado.

**Acceptance Criteria (EARS):**
- WHEN o usuário solicita um quiz para uma lição, THEN 4 perguntas de múltipla escolha são geradas.
- WHEN o usuário envia respostas, THEN o sistema avalia cada resposta via IA e retorna feedback.
- WHEN o quiz tem menos de 3 perguntas, THEN um aviso de conteúdo é emitido.
- WHEN perguntas são geradas, THEN cada uma deve ter exatamente 4 opções.

## Requisito R.4: Diagnóstico de Conhecimento
**User Story:** Como um estudante, eu quero diagnosticar meu nível de conhecimento em uma área, para que eu saiba quais tópicos preciso estudar.

**Acceptance Criteria (EARS):**
- WHEN o usuário informa uma área de estudo e seu conhecimento atual, THEN o sistema retorna uma análise detalhada.
- WHEN o diagnóstico é processado, THEN ele consulta o `dep_map.json` para determinar dependências entre tópicos.
- WHEN tópicos têm dependências não atendidas, THEN eles são marcados como "bloqueados" no resultado.
- WHEN o `dep_map.json` está vazio ou incompleto, THEN o diagnóstico deve funcionar com dados parciais.

## Requisito R.5: Interface de Usuário
**User Story:** Como um estudante, eu quero uma interface visual moderna e responsiva, para que eu possa navegar pelos roadmaps e lições confortavelmente.

**Acceptance Criteria (EARS):**
- WHEN a interface é renderizada, THEN deve usar tema escuro com design glassmorphism.
- WHEN o usuário navega no fluxograma, THEN os tópicos são exibidos com linhas SVG bezier alternando lados.
- WHEN o usuário clica em expandir/recolher, THEN os subtópicos são mostrados/ocultados com animação.
- WHEN há muitos tópicos, THEN o layout deve calcular posicionamento dinâmico para evitar sobreposição.
- WHEN o usuário usa dispositivo móvel, THEN a interface deve ser responsiva.

## Requisito R.6: Validação de Conteúdo
**User Story:** Como um mantenedor, eu quero validar automaticamente o formato de roadmaps e lições, para garantir a integridade dos dados.

**Acceptance Criteria (EARS):**
- WHEN o script de validação é executado, THEN ele verifica naming, estrutura JSON, formato de quiz.
- WHEN um arquivo não segue o padrão, THEN o validador reporta erro específico com linha e ação corretiva.
- WHEN lições não contêm quiz embutido, THEN um aviso é emitido (não bloqueante).

## Requisito R.7: Motor DSL (Domain Specific Language)
**User Story:** Como um desenvolvedor, eu quero um motor DSL para definir fluxos de aprendizado customizados, para que eu possa criar experiências interativas programaticamente.

**Acceptance Criteria (EARS):**
- WHEN uma DSL é submetida, THEN o motor deve validar sua sintaxe.
- WHEN a DSL é válida, THEN o motor deve executar os comandos definidos.
- WHEN a DSL tem erros de sintaxe, THEN o motor deve retornar erros descritivos com localização.

## Requisito R.8: Segurança e Integridade
**User Story:** Como um mantenedor, eu quero que artefatos críticos do projeto sejam protegidos contra modificação não autorizada.

**Acceptance Criteria (EARS):**
- WHEN o guard_harness é executado, THEN arquivos protegidos têm seus hashes SHA256 verificados.
- WHEN um arquivo protegido é modificado sem autorização, THEN o guard_harness reporta VIOLATED e bloqueia o pipeline.
- WHEN credenciais são acessadas, THEN elas vêm de variáveis de ambiente, nunca hardcodadas.
- WHEN o servidor recebe uma requisição, THEN path traversal e XSS são prevenidos.

## Requisito R.9: Testabilidade
**User Story:** Como um desenvolvedor, eu quero uma suíte de testes automatizados, para garantir que regressões sejam detectadas.

**Acceptance Criteria (EARS):**
- WHEN testes são executados, THEN `pytest` cobre serviços de diagnóstico, quiz e motor DSL.
- WHEN o harness é executado, THEN testes devem passar sem erros.
- WHEN uma nova funcionalidade é adicionada, THEN testes correspondentes devem ser criados.

## Requisito R.E: Tratamento de Erros
**User Story:** Como um usuário, eu quero mensagens de erro claras quando algo der errado, para que eu possa entender e corrigir o problema.

**Acceptance Criteria (EARS):**
- WHEN a API key não está configurada, THEN o sistema retorna erro `PermissionError` com mensagem clara.
- WHEN um arquivo não é encontrado, THEN o sistema retorna HTTP 404 com descrição do recurso ausente.
- WHEN a API da OpenRouter falha, THEN o sistema retorna erro com status code e mensagem original.
- WHEN a validação Pydantic falha, THEN o sistema retorna HTTP 422 com detalhes dos campos inválidos.

## Requisito UI-1: Identidade Visual — Sistema Cartográfico
**User Story:** Como um estudante, eu quero uma interface com identidade visual de mapa de exploração (tons navy/âmbar, tipografia serifada, fundo topográfico), para que eu me sinta imerso em uma jornada de aprendizado.

**Critérios de Aceite (EARS):**
- [Ubíquo] Durante toda a navegação, o sistema DEVE aplicar a paleta de cores definida no design system (navy profundo #0f172a, âmbar #f59e0b, superfície #1e293b).
- [Evento] QUANDO a página carrega, ENTÃO o sistema DEVE exibir o fundo topográfico SVG animado e as fontes Playfair Display (títulos) + DM Sans (corpo) + JetBrains Mono (código).
- [Estado] ENQUANTO o usuário estiver em uma seção com glassmorphism, o sistema DEVE manter blur mínimo de 16px e borda com opacidade âmbar de 20%.
- [Opcional] ONDE a animação de background consumir muitos recursos, o sistema PODE reduzir a taxa de quadros ou desativar animações decorativas.
- [Indesejado] SE as fontes do Google Fonts não carregarem, ENTÃO o sistema DEVE aplicar fallback para serifa/sans-serif/monospace do sistema.

**Perspectiva de Segurança/Abuse Case:**
- [Indesejado] SE um payload XSS tentar alterar variáveis CSS via style injection, ENTÃO o sistema DEVE sanitizar todo conteúdo dinâmico antes de aplicar ao DOM.

**Perspectiva de Manutenção/Operação:**
- [Evento] QUANDO um novo tema ou variação cromática for necessário, ENTÃO a equipe DEVE alterar exclusivamente as variáveis no bloco `:root` do CSS, sem modificar componentes individuais.

**Perspectiva API/Infra:**
- [Evento] QUANDO as fontes são carregadas via Google Fonts CDN, ENTÃO o sistema DEVE usar `display=swap` para não bloquear a renderização da página.

## Requisito UI-2: Estados de Componente — Loading, Empty, Error, Success
**User Story:** Como um estudante, eu quero feedback visual claro para cada estado da interface (carregando, vazio, erro, sucesso), para que eu entenda o que está acontecendo a todo momento.

**Critérios de Aceite (EARS):**
- [Ubíquo] Em toda requisição de dados, o sistema DEVE exibir um shimmer skeleton animado durante o carregamento.
- [Evento] QUANDO uma requisição retorna dados vazios, ENTÃO o sistema DEVE exibir uma ilustração de empty state com mensagem amigável e ação sugerida.
- [Estado] ENQUANTO uma requisição está em andamento, o sistema DEVE desabilitar interações repetidas (debounce) no botão acionador.
- [Opcional] ONDE o componente suportar retry automático, o sistema PODE re-tentar a requisição uma vez antes de exibir o estado de erro.
- [Indesejado] SE uma requisição falhar, ENTÃO o sistema DEVE exibir um error state com descrição amigável do problema e botão "Tentar novamente".

**Perspectiva de Segurança/Abuse Case:**
- [Indesejado] SE um erro de servidor expuser detalhes internos (stack trace, SQL, path real), ENTÃO o sistema DEVE ocultar informações sensíveis e exibir apenas mensagem genérica amigável.

**Perspectiva de Manutenção/Operação:**
- [Evento] QUANDO um novo componente é criado, ENTÃO o desenvolvedor DEVE implementar os 4 estados (loading, empty, error, success) seguindo os templates do design system.

**Perspectiva API/Infra:**
- [Evento] QUANDO uma chamada de API retorna HTTP 4xx/5xx, ENTÃO o frontend DEVE capturar o status code e exibir mensagem correspondente ao tipo de erro, com opção de retry.

## Requisito UI-3: Sistema de Movimento e Animações
**User Story:** Como um estudante, eu quero transições animadas e feedback visual nas interações, para que a navegação seja fluida e prazerosa.

**Critérios de Aceite (EARS):**
- [Ubíquo] Durante toda a navegação, animações DEVEM seguir a curva padrão `cubic-bezier(0.4, 0, 0.2, 1)` com duração máxima de 400ms.
- [Evento] QUANDO a página carrega, ENTÃO os nós do fluxograma DEVEM aparecer com staggered reveal (atraso progressivo de 50ms entre cada nó).
- [Estado] ENQUANTO o painel de lição está abrindo/fechando, o sistema DEVE animar o slide-in/out com duração de 300ms.
- [Opcional] ONDE um nó do fluxograma é completado, o sistema PODE disparar uma animação de confete ou partículas.
- [Indesejado] SE o usuário tiver preferência por movimento reduzido (`prefers-reduced-motion`), ENTÃO o sistema DEVE desabilitar todas as animações não essenciais e exibir transições instantâneas.

**Perspectiva de Segurança/Abuse Case:**
- [Indesejado] SE múltiplas animações forem acionadas simultaneamente (cliques rápidos em série), ENTÃO o sistema DEVE aplicar throttle/debounce para evitar sobrecarga de renderização.

**Perspectiva de Manutenção/Operação:**
- [Evento] QUANDO uma nova animação é adicionada, ENTÃO o desenvolvedor DEVE registrar sua duração e curva no sistema de tokens de motion.

**Perspectiva API/Infra:**
- [Evento] QUANDO dados são carregados via API, ENTÃO o sistema DEVE aguardar o término do carregamento antes de iniciar animações de transição, evitando flashes de conteúdo não estilizado.

## Requisito UI-4: Navegação, Busca e Filtros
**User Story:** Como um estudante, eu quero buscar roadmaps, filtrar por dificuldade/status e navegar com teclado, para que eu encontre rapidamente o que preciso estudar.

**Critérios de Aceite (EARS):**
- [Ubíquo] Em todas as telas com lista de roadmaps, o sistema DEVE exibir um campo de busca com feedback visual instantâneo.
- [Evento] QUANDO o usuário digita no campo de busca, ENTÃO o sistema DEVE filtrar a lista em tempo real com debounce de 300ms.
- [Estado] ENQUANTO o filtro está ativo, o sistema DEVE exibir contagem de resultados e botão "Limpar filtro".
- [Opcional] ONDE houver mais de 10 itens filtrados, o sistema PODE paginar em grupos de 10.
- [Indesejado] SE a busca não retornar resultados, ENTÃO o sistema DEVE exibir empty state com sugestão de termos alternativos.

**Perspectiva de Segurança/Abuse Case:**
- [Indesejado] SE um termo de busca contiver caracteres de injeção HTML/JS, ENTÃO o sistema DEVE sanitizar a entrada antes de exibir no DOM.

**Perspectiva de Manutenção/Operação:**
- [Evento] QUANDO um novo tipo de filtro é adicionado, ENTÃO o desenvolvedor DEVE registrá-lo no módulo de filtros e atualizar os atalhos de teclado correspondentes.

**Perspectiva API/Infra:**
- [Evento] QUANDO o usuário pressionar atalho de teclado (ex: Ctrl+K para busca), ENTÃO o sistema DEVE focar o campo de busca sem fazer requisição de rede.

## Requisito UI-5: Responsividade e Mobile
**User Story:** Como um estudante que acessa pelo celular, eu quero uma interface adaptada para telas pequenas com interações por toque, para que eu possa estudar em qualquer lugar.

**Critérios de Aceite (EARS):**
- [Ubíquo] Em dispositivos com largura mínima de 320px, o sistema DEVE exibir todo o conteúdo sem cortes horizontais.
- [Evento] QUANDO o usuário toca em um nó do fluxograma em mobile, ENTÃO o sistema DEVE exibir o painel de lição como bottom sheet (não como slide lateral).
- [Estado] ENQUANTO o dispositivo estiver em orientação retrato em tela < 768px, o sistema DEVE reorganizar o fluxograma para layout vertical simplificado.
- [Opcional] ONDE o dispositivo suportar gestos de swipe, o sistema PODE aceitar swipe horizontal para navegar entre roadmaps.
- [Indesejado] SE o dispositivo tiver tela muito pequena (< 375px), ENTÃO o sistema DEVE ocultar elementos decorativos (background topográfico, glow effects) para priorizar conteúdo.

**Perspectiva de Segurança/Abuse Case:**
- [Indesejado] SE um iframe malicioso tentar simular interação touch para execução não autorizada, ENTÃO o sistema DEVE validar a origem do evento de toque.

**Perspectiva de Manutenção/Operação:**
- [Evento] QUANDO um novo componente é adicionado, ENTÃO o desenvolvedor DEVE testá-lo em 3 breakpoints: ≥ 1024px (desktop), 768-1023px (tablet), 320-767px (mobile).

**Perspectiva API/Infra:**
- [Evento] QUANDO o servidor detectar requisições de dispositivo mobile (via User-Agent), ENTÃO a API PODE priorizar respostas menores para reduzir tempo de carregamento.

## Requisito UI-6: Acessibilidade (WCAG AA)
**User Story:** Como um usuário com deficiência visual ou motora, eu quero uma interface acessível por teclado e leitores de tela, para que eu possa utilizar a plataforma de forma autônoma.

**Critérios de Aceite (EARS):**
- [Ubíquo] Todos os componentes interativos DEVEM ter contraste mínimo de 4.5:1 para texto normal e 3:1 para texto grande (WCAG AA).
- [Evento] QUANDO um elemento recebe foco via teclado, ENTÃO o sistema DEVE exibir um focus indicator visível com outline de 2px e offset de 2px.
- [Estado] ENQUANTO o usuário navega por teclado, o sistema DEVE manter uma ordem de tabulação lógica (Tab segue ordem natural do DOM, sem tabindex positivo).
- [Opcional] ONDE o usuário utilizar leitor de tela, o sistema PODE adicionar regiões de landmark ARIA (`role="navigation"`, `role="main"`, `role="complementary"`).
- [Indesejado] SE o usuário ativar `prefers-reduced-motion`, ENTÃO o sistema DEVE desabilitar todas as animações CSS e JS não essenciais.

**Perspectiva de Segurança/Abuse Case:**
- [Indesejado] SE um atacante tentar ocultar elementos maliciosos usando ARIA hidden, ENTÃO o sistema DEVE auditar a presença de ARIA attributes inconsistentes.

**Perspectiva de Manutenção/Operação:**
- [Evento] QUANDO um novo componente é criado, ENTÃO o desenvolvedor DEVE garantir que ele possua: (1) foco visível, (2) label ARIA, (3) suporte a Enter/Esc, (4) papel semântico apropriado.

**Perspectiva API/Infra:**
- [Evento] QUANDO o sistema detectar idioma do navegador diferente de pt-BR, ENTÃO os documentos HTML DEVEM conter lang tag apropriada para suporte a leitores de tela.
