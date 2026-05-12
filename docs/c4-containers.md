# C4 Containers Diagram

## Containers do Sistema Roadmap Estudos

### Application
- **Frontend Web (Static)**
  - Tecnologia: HTML5, CSS3, JavaScript (ES6+)
  - Responsabilidade: Interface do usuário para visualização de roadmaps, leitura de lições e interação com quizzes
  - Deploy: Servido diretamente pelo servidor Python via http.server

- **Backend API Server**
  - Tecnologia: Python 3.11+, http.server (padrão)
  - Responsabilidade: Exposição de endpoints RESTful para geração de conteúdo, gerenciamento de roadmaps e serviços educacionais
  - Deploy: Processo Python independente na porta 8000

### Data Stores
- **Arquivos JSON de Roadmap**
  - Tecnologia: Sistema de arquivos local
  - Responsabilidade: Armazenamento de estruturas de roadmap geradas
  - Localização: `/data/roadmap_{tema}.json`
  
- **Arquivos Markdown de Lições**
  - Tecnologia: Sistema de arquivos local
  - Responsabilidade: Armazenamento de conteúdo educacional com quizzes embutidos
  - Localização: `/licoes/{node_id}.md`
  
- **Mapa de Dependências (dep_map.json)**
  - Tecnologia: Sistema de arquivos local
  - Responsabilidade: Mapeamento de pré-requisitos entre tópicos para diagnóstico de lacunas
  - Localização: `/data/dep_map.json`

### Systems Externos
- **OpenRouter API Service**
  - Tecnologia: REST API externa
  - Responsabilidade: Fornecimento de modelos de linguagem para geração de conteúdo educacional
  - Autenticação: Bearer Token via variável de ambiente OPENROUTER_API_KEY

### Container Interactions

#### Frontend ↔️ Backend
- **Protocol**: HTTP/HTTPS
- **Formato**: JSON para API, HTML/CSS/JS para recursos estáticos
- **Padrões de Comunicação**:
  - GET `/api/roadmaps` - Lista roadmaps disponíveis
  - GET `/api/roadmap/{nome}` - Carrega roadmap específico
  - POST `/api/generate-lesson` - Solicita geração de lição individual
  - POST `/api/generate-roadmap` - Solicita geração de roadmap completo
  - POST `/api/save-roadmap` - Salva roadmap gerado
  - POST `/api/generate-quiz` - Gera quiz para lição específica
  - POST `/api/evaluate-quiz` - Avalia respostas de quiz
  - POST `/api/diagnose` - Diagnostica lacunas de conhecimento
  - GET `/api/dep-map` - Obtém mapa de dependências

#### Backend ↔️ OpenRouter API
- **Protocol**: HTTPS
- **Formato**: JSON
- **Endpoints Utilizados**:
  - `POST /v1/chat/completions` - Para todas as gerações de conteúdo
- **Modelos Utilizados**: `openrouter/auto` (seleção automática de modelo)
- **Tipos de Requisição**:
  - Geração de lições educacionais
  - Criação de estrutura de roadmap
  - Geração de questões de quiz
  - Avaliação de respostas de quiz
  - Diagnóstico de lacunas de conhecimento

#### Backend ↔️ Sistema de Arquivos
- **Operações**: Leitura e escrita de arquivos
- **Locais Acessados**:
  - Leitura: `/licoes/{node_id}.md` (conteúdo das lições)
  - Leitura/Escrita: `/data/roadmap_*.json` (roadmaps)
  - Leitura/Escrita: `/data/dep_map.json` (mapa de dependências)
  - Leitura: `.env` (variáveis de ambiente)

### Tecnologias por Container

#### Frontend Web
- HTML5: Estrutura semântica
- CSS3: Estilização e layout (incluindo suporte a diagramas Mermaid)
- JavaScript (ES6+): Interatividade, manipulação de DOM, chamadas API
- Bibliotecas: Nenhuma externa (vanilla JS para compatibilidade com http.server)

#### Backend API Server
- Python 3.11+: Linguagem principal
- http.server: Servidor HTTP básico com suporte a CORS
- openai Python SDK: Cliente para OpenRouter API
- json: Manipulação de dados JSON
- os, pathlib: Manipulação de filesystem
- re: Expressões regulares para extração de JSON
- threading: Suporte básico para requisições concorrentes (via socketserver)

#### Armazenamento de Dados
- Sistema de Arquivos Local: Armazenamento persistente simples
- Formato JSON: Para roadmaps e mapa de dependências
- Formato Markdown: Para lições educacionais com quizzes embutidos

#### OpenRouter API
- RESTful API: Interface padronizada
- Autenticação: Bearer Token
- Modelos: Acesso a diversos LLMs via roteamento automático