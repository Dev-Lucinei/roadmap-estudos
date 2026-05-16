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
