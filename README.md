# 🗺️ Portal de Estudos Interativo (Roadmap Learning)

Este projeto é um **Sistema de Gestão de Aprendizado (LMS) Pessoal** que transforma roteiros técnicos estáticos (inspirados no roadmap.sh) em uma plataforma de estudo interativa e automatizada. Ele utiliza Inteligência Artificial para gerar conteúdos teóricos estruturados a partir de metas de estudo.

## 🚀 Funcionalidades Principais

- **Visualização de Roadmap**: Interface interativa com visão macro e micro dos tópicos de estudo.
- **Geração de Conteúdo via IA**: Script automatizado que cria lições completas em Markdown seguindo um template profissional.
- **Interface Premium**: Design em Dark Mode com efeitos de *glassmorphism* e renderização dinâmica de Markdown.
- **Painel Lateral de Estudo**: Acesso instantâneo à teoria e objetivos de cada nó do roadmap sem sair da visão geral.

## 🛠️ Tecnologias Utilizadas

- **Frontend**: HTML5, Vanilla CSS (Design Moderno), JavaScript (ES6+).
- **Processamento de Markdown**: [Marked.js](https://marked.js.org/) via CDN.
- **Automação de Conteúdo**: Python 3.x com integração [OpenAI/OpenRouter API](https://openrouter.ai/).
- **Design System**: Inspirado na estética premium do roadmap.sh com tipografia Inter.

## 📁 Estrutura do Projeto

```
roadmap-estudos/
├── backend/                    # Servidor Python (FastAPI/serviços)
│   ├── api/                    # Rotas da API REST
│   ├── core/                   # Configurações centrais
│   └── services/               # Lógica de negócio
│       ├── ai_content/         # Geração de roadmaps e lições
│       ├── diagnosis/          # Serviço de diagnóstico
│       ├── quiz/               # Serviço de quizzes
│       └── dsl/                # Motor DSL
├── frontend/                   # Interface web
│   └── public/                 # Arquivos estáticos servidos
│       ├── index.html          # Página principal
│       └── assets/             # CSS, JS, dados
├── data/                       # Roadmaps em JSON
├── licoes/                     # Lições em Markdown
├── docs/                       # Documentação técnica
├── scripts/                    # Utilitários e automação
├── tests/                      # Testes automatizados
├── skill/                      # Skill do agente
├── harness.py                  # Orquestrador de validação
└── AGENTS.md                   # Instruções para agentes
```

## ⚙️ Configuração e Instalação

### 1. Pré-requisitos
- Python 3.11 ou superior instalado.
- Ambiente virtual configurado (opcional, mas recomendado).

### 2. Rodando o Servidor
Inicie o servidor web para visualizar o portal:
```bash
cd backend && python main.py
```
*O servidor API estará disponível em `http://localhost:8000`*

## 📖 Como Usar

1.  Inicie o servidor backend: `cd backend && python main.py`
2.  Acesse `http://localhost:8000` no navegador
3.  Navegue pelo roadmap visual para ter a visão geral do curso
4.  **Clique em um nó central**: Para visualizar os objetivos gerais daquela área
5.  **Clique em um nó de tópico**: Para abrir o conteúdo teórico detalhado no painel lateral

## 🧠 Metodologia de Estudo
O conteúdo gerado segue a técnica de **Síntese Acadêmica**, focando em:
- **Metadados**: Tags e contexto.
- **Resumo Executivo**: Essência do conceito.
- **Checklist de Revisão**: Para garantir a retenção do conhecimento.

---
*Documentação gerada pelo Agente Antigravity para suporte ao aprendizado contínuo.*
