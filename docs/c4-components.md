# C4 Components Diagram

## Componentes do Backend API Server

### Container: Backend API Server
Tecnologia: Python 3.11+, http.server

### Componentes Principais

#### 1. RoadmapHandler (HTTP Handler)
- **Responsabilidade**: Processa todas as requisições HTTP e delega aos serviços apropriados
- **Métodos**:
  - `do_GET()`: Manipula requisições GET para listagem e carregamento de recursos
  - `do_POST()`: Manipula requisições POST para geração e processamento de dados
  - `do_DELETE()`: Manipula requisições DELETE (retorna 405 - não implementado)
  - `do_OPTIONS()`: Manipula requisições OPTIONS para CORS
- **Sub-componentes**:
  - `list_roadmaps()`: Lista roadmaps disponíveis no diretório /data
  - `load_roadmap()`: Carrega um roadmap específico por nome
  - `get_dep_map()`: Retorna o mapa de dependências
  - `handle_generate_lesson()`: Processa geração de lição individual
  - `handle_generate_roadmap()`: Processa geração de roadmap completo
  - `handle_save_roadmap()`: Processa salvamento de roadmap
  - `handle_diagnosis()`: Processa diagnóstico de lacunas de conhecimento
  - `handle_regenerate_dep_map()`: Regenera mapa de dependências a partir dos roadmaps
  - `handle_generate_quiz()`: Gera quiz para uma lição específica
  - `handle_evaluate_quiz()`: Avalia respostas de quiz

#### 2. QuizService
- **Responsabilidade**: Geração e avaliação de quizzes educacionais
- **Métodos Públicos**:
  - `generate_quiz(node_id, title)`: Gera 4 perguntas objetivas baseadas no conteúdo da lição
  - `evaluate_quiz(node_id, title, quiz_data, user_answers)`: Avalia respostas do usuário com feedback detalhado
- **Dependências**:
  - OpenRouter API (via cliente OpenAI)
  - Diretório de lições (/licoes)
  - Bibliotecas: json, re, os

#### 3. DiagnosisService
- **Responsabilidade**: Diagnóstico independente de lacunas de conhecimento
- **Métodos Públicos**:
  - `diagnose(topic, user_answer)`: Analisa resposta do usuário e identifica lacunas nos pré-requisitos
- **Dependências**:
  - OpenRouter API (via cliente OpenAI)
  - Mapa de dependências (/data/dep_map.json)
  - Bibliotecas: json

#### 4. Utilitários de Geração (Importados)
Esses são módulos importados e utilizados pelos handlers:

##### a. generate_lessons module
- **Funções**:
  - `gerar_conteudo_ia(topico, tipo)`: Gera conteúdo educacional via IA com estrutura padronizada
  - `processar_node(node_id, title, node_type, output_dir)`: Processa um nó e gera sua lição
- **Características**:
  - Gera lições em Markdown com quiz embutido (exatamente 3 questões)
  - Estrutura fixa: Resumo Executivo, Conceitos-Chave, Aplicação Prática, Erros Comuns, Checklist
  - Instruções rigorosas para IA focar exclusivamente no tópico solicitado

##### b. generate_roadmap module
- **Funções**:
  - `gerar_roadmap_ia(tema)`: Gera estrutura de roadmap via IA em formato JSON padronizado
  - `salvar_roadmap(tema, dados)`: Salva o roadmap gerado em arquivo JSON
- **Características**:
  - Estrutura JSON com nós centrais e subtopics
  - Organização em grupos/seções (mínimo 3)
  - Controle de dificuldade e posicionamento lateral (left/right)

### Dependências Externas
- **OpenRouter API**: 
  - Utilizada por: QuizService, DiagnosisService, generate_lessons, generate_roadmap
  - Propósito: Geração de conteúdo educacional via LLMs
  - Interface: REST API com autenticação Bearer Token

### Acesso a Dados
- **Sistema de Arquivos Local**:
  - Leitura de lições: /licoes/{node_id}.md
  - Leitura de roadmaps: /data/roadmap_{tema}.json
  - Leitura/Escrita de mapa de dependências: /data/dep_map.json
  - Leitura de configuração: .env (variáveis de ambiente)

### Pontos de Extensão
1. **Novos Services**: Adicionar novos serviços seguindo o padrão de QuizService/DiagnosisService
2. **Novos Endpoints**: Adicionar métodos em RoadmapHandler para novas funcionalidades
3. **Novos Utilitários de Geração**: Criar novos módulos similares a generate_lessons.py e generate_roadmap.py
4. **Armazenamento Alternativo**: Abstrair camada de acesso a dados para suportar outros tipos de storage

### Comunicação entre Componentes
- **RoadmapHandler → QuizService**: Instancia serviço e chama métodos para geração/avaliação de quiz
- **RoadmapHandler → DiagnosisService**: Instancia serviço e chama método para diagnóstico
- **RoadmapHandler → generate_lessons**: Importa e chama processar_node() para geração de lição
- **RoadmapHandler → generate_roadmap**: Importa e chama gerar_roadmap_ia() e salvar_roadmap() para geração de roadmap
- **QuizService/DiagnosisService → OpenRouter API**: Faz chamadas HTTP para geração de conteúdo
- **Todos os componentes → Sistema de Arquivos**: Leitura/escrita direta usando operações padrão de file I/O