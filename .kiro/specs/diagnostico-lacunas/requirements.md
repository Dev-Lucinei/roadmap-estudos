# Requirements Document: Diagnóstico de Lacunas de Base

## Introduction

O módulo permite ao usuário diagnosticar lacunas conceituais em conceitos avançados, gerando material de apoio comântico e mantém o fluxo de aprendizado sem desvios.

## Glossary
- **Diagnóstico**: Avaliação de conhecimento em um tópico avançado.
- **Conteúdo Base**: Materiais que devem estar assimilados antes de avançar.
- **Modo Foco**: UI que bloqueia o acesso a tópicos avançados até diagnóstico.

## Requirements

### 1. Mapeamento de Dependências Critical
**User Story**: Como instrutor, quero mapear dependências críticas em JSON para que o sistema valide lacunas.

#### Acceptance Criteria
1. Quando a base de dados estiver em `data/`, o sistema deve gerar um mapa JSON `{topic: [prerequisites]}`.
2. O mapa deve ser atualizado automaticamente ao adicionar ou remover tópicos.

### 2. Geração de Conteúdo Limitada a 100 Palavras
**User Story**: Como usuário, quero respostas concisas focadas em fórmula/regra e erro comum.

#### Acceptance Criteria
1. Quando LLM gerar resposta, ela deve ter menos de 100 palavras.
2. O conteúdo deve incluir, no mínimo, 1 fórmula ou regra, 1 erro comum.

### 3. UI Glassmorphism Minimalista
**User Story**: Como designer, quero UI com blur e overlay suave.

#### Acceptance Criteria
1. Quando modal de revisão aberto, deve usar `backdrop-filter: blur`.
2. Layout deve permanecer responsivo em mobile e desktop.

### 4. Latência de Geração ≤ 3s
**User Story**: Como estudante, quero resposta rápida.

#### Acceptance Criteria
1. Tempo total entre envio de prompt e mensagem na tela não exceder 3 segundos.

### 5. Bloqueio em Falha de Diagnóstico
**User Story**: Como instrutor, quero impedir avanço se diagnóstico falhar.

#### Acceptance Criteria
1. Se diagnóstico devolve `miss`, tópico avançado fica bloqueado.
2. Modal de revisão apresenta detalhes para remediar lacunas.

### 6. Segurança: Sem Tecnologias Exigindo Reescrita Total
**User Story**: Como mantenedor, quero evitar reescrita de stack.

#### Acceptance Criteria
1. Se uma solução exigir reescrita completa do front‑end em React, rejeitar.

### 7. Consumo ≤ 15 Minutos
**User Story**: Como usuário, conteúdo deve ser consumível em menos de 15 minutos.

#### Acceptance Criteria
1. Respostas geradas não exigem mais que 15 minutos de leitura.

### 8. Alertas Não Excessivos
**User Story**: Como usuário, não quero relatos de erro em excesso.

#### Acceptance Criteria
1. Modal de revisão contém apenas instruções essenciais.

### 9. Testes Obrigatórios
**User Story**: Como QA, quero validar requisitos específicos.

#### Acceptance Criteria
1. Diagnóstico identifica lacuna específica.
2. Conteúdo gerado é aplicável ao contexto.
3. Modo foco não quebra layout.
4. Fluxo de sucesso libera acesso sem revisão.
