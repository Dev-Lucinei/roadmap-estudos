# C4 Context Diagram

## Sistema: Roadmap Estudos

### Descrição
Aplicação educacional para geração e visualização de roadmaps de estudos com integração a IA para criação de conteúdo dinâmico e personalizado.

### Elementos do Contexto

#### Sistema Central
- **Roadmap Estudos**
  - Aplicação web que permite aos usuários criar, visualizar e estudar roadmaps de conteúdo educacional
  - Gera lições personalizadas usando IA
  - Fornece quizzes interativos para avaliação de aprendizado
  - Diagnostica lacunas de conhecimento baseado em mapa de dependências

#### Personas (Usuários)
- **Estudante/Aluno**
  - Necessita: Aprender novos tópicos de forma estruturada
  - Interage com: Visualização de roadmaps, leitura de lições, resposta a quizzes
  - Recebe: Conteúdo educacional personalizado, feedback de avaliação, diagnóstico de lacunas
  
- **Instrutor/Professor**
  - Necessita: Criar materiais didáticos estruturados
  - Interage com: Geração de roadmaps e lições via API
  - Recebe: Conteúdo pronto para uso, mapas de dependências

#### Sistemas Externos
- **OpenRouter API** (Fornecedor de IA)
  - Fornece: Acesso a modelos de linguagem grandes para geração de conteúdo
  - Interface: REST API com autenticação via Bearer Token
  - Dados trocados: Prompts de geração de conteúdo, respostas em formato texto/JSON
  
- **Navegador Web**
  - Fornece: Interface para acesso à aplicação
  - Interface: HTTP/HTTPS
  - Dados trocados: Arquivos estáticos (HTML/CSS/JS), requisições API JSON

#### Relacionamentos
- **Estudante ↔️ Roadmap Estudos**
  - Protocolo: HTTP/HTTPS
  - Formato: HTML/CSS/JS para interface, JSON para API
  - Propósito: Acesso à interface web e consumo de serviços API
  
- **Instrutor ↔️ Roadmap Estudos**
  - Protocolo: HTTP/HTTPS
  - Formato: JSON
  - Propósito: Solicitação de geração de conteúdo via endpoints API
  
- **Roadmap Estudos ⇆ OpenRouter API**
  - Protocolo: HTTPS
  - Formato: JSON
  - Propósito: Geração de lições, roadmaps, quizzes e diagnósticos
  
- **Roadmap Estudos ⇆ Navegador Web**
  - Protocolo: HTTP/HTTPS
  - Formato: HTML/CSS/JS, JSON
  - Propósito: Servir interface estática e consumir serviços API

### Limites do Sistema
- Frontend: HTML/CSS/JS puro servido via http.server do Python
- Backend: Servidor Python com endpoints RESTful
- External: Serviços de IA via OpenRouter API
- Armazenamento: Sistema de arquivos local (JSON e Markdown)