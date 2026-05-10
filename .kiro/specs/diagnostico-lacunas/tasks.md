# Implementation Plan: Diagnóstico de Lacunas de Base

## Fase 1: Estrutura Base e Governança

- [ ] 1.1 Configurar estrutura de diretórios conforme design.md
  - Criar .kiro/specs/diagnostico-lacunas/
  - Criar data/dep_map.json para mapeamento de dependências
  - _Requirements: Estrutura_

- [ ] 1.2 Configurar harness de validação
  - Copiar harness.py e scripts/guard_harness.py para o repositório (se não existirem)
  - Executar: python scripts/guard_harness.py --seal
  - Commitar .harness.hash
  - Confirmar: python harness.py retorna status "healthy"
  - _Requirements: Req. Testabilidade_

- [ ] 1.3 Configurar dependências de desenvolvimento
  - Verificar se requests está disponível para chamadas à OpenRouter
  - _Requirements: Estrutura_

## Fase 2: Mapeamento de Dependências e Backend

- [ ] 2.1 Criar arquivo de mapeamento de dependências
  - Criar data/dep_map.json com estrutura { "tópicoA": ["préReqB", "préReqC"] }
  - Preencher com exemplos baseado nos roadmaps existentes (python_fundamentos.json, roadmap_analise_de_dados.json)
  - _Requirements: Mapeamento de Dependências Critical_

- [ ] 2.2 Implementar endpoint de diagnóstico no backend
  - Adicionar rota POST /api/diagnose em server.py
  - Implementar validação de entrada (topic, user_answer)
  - Integrar chamada à OpenRouter API com limite de 100 palavras
  - Verificar dependências no JSON de mapeamento
  - Retornar JSON com status, message e tags
  - _Requirements: Geração de Conteúdo Limitada, Latência de Geração, Segurança_

- [ ] 2.3 Implementar tratamento de erro e timeouts
  - Adicionar timeout de 2,5s para chamada à LLM
  - Tratar erros de rede e resposta inválida
  - Retornar mensagem amigável em caso de falha
  - _Requirements: Latência de Geração, Alertas Não Excessivos_

## Fase 3: Frontend e UI

- [ ] 3.1 Adicionar funções de diagnóstico ao app.js
  - Criar função runDiagnosis(topic, callback) que envia POST para /api/diagnose
  - Criar função showReviewModal(data) para exibir modal com styles glassmorphism
  - Implementar função hideReviewModal() para fechar overlay
  - _Requirements: UI Glassmorphism Minimalista, Latência de Geração_

- [ ] 3.2 Integrar diagnóstico ao fluxo de tópicos avançados
  - Identificar pontos de entrada em tópicos avançados em app.js ou roadmap_data.js
  - Antes de liberar conteúdo avançado, chamar runDiagnosis
  - Se status "miss", exibir modal de revisão e bloquear acesso
  - Se status "hit", permitir acesso normalmente
  - _Requirements: Bloqueio em Falha de Diagnóstico_

- [ ] 3.3 Implementar estilos CSS para modo foco
  - Adicionar classes CSS para overlay com backdrop-filter: blur
  - Garantir responsividade em mobile e desktop
  - Manter estética minimalista
  - _Requirements: UI Glassmorphism Minimalista_

## Fase 4: Testes e Validação

- [ ] 4.1 Criar testes unitários para lógica de diagnóstico
  - Testar validação de entrada
  - Testar chamada simulada à LLM
  - Testar verificação de dependências
  - _Requirements: Testabilidade_

- [ ] 4.2 Executar testes de integração
  - Verificar fluxo completo: frontend → backend → LLM → frontend
  - Testar cenários de hit e miss
  - Verificar latência total < 3s
  - _Requirements: Latência de Geração, Segurança_

- [ ] 4.3 Validar UI e experiência do usuário
  - Testar modal em diferentes tamanhos de tela
  - Verificar que conteúdo gerado é aplicável ao contexto
  - Confirmar que layout não quebra
  - _Requirements: UI Glassmorphism Minimalista, Testes Obrigatórios_

## Fase Final - 1: Segurança e Validação

- [ ] S.1 Auditoria de segurança via harness
  - Executar: python harness.py security
  - Corrigir todos os erros SEC_FORBIDDEN na causa raiz
  - _Requirements: Req. Segurança_

- [ ] S.2 Verificar integridade dos artefatos protegidos
  - Executar: python scripts/guard_harness.py
  - Confirmar STATUS: INTACT
  - _Requirements: Req. Segurança_

- [ ] S.3 Auditar gestão de credenciais
  - Confirmar que OpenRouter API key é lida de variável de ambiente
  - Confirmar que nenhuma credencial está hardcodada
  - _Requirements: Req. Segurança_

## Fase Final: Testes e Gate de Qualidade

- [ ] T.1 Testes unitários para toda lógica de negócio
  - Executar testes de unidade para backend e frontend
  - _Requirements: Req. Testabilidade_

- [ ] T.2 Testes de integração para fluxos ponta-a-ponta
  - Simular fluxo completo de diagnóstico
  - _Requirements: Req. Testabilidade_

- [ ] T.3 Gate final de qualidade
  - Executar: python harness.py
  - Confirmar: status == "healthy", 0 erros críticos
  - Nenhum merge permitido com harness falhando
  - _Requirements: Todos_