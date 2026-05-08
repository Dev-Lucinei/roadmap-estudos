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

```text
portal_estudos/
├── licoes/                 # Arquivos .md gerados pela IA (Fonte de estudo)
├── app.js                  # Lógica de renderização e interatividade
├── style.css               # Design system e animações
├── index.html              # Estrutura principal da aplicação
├── roadmap_data.js         # Definição da estrutura do roteiro
└── generate_lessons.py     # Motor de geração de conteúdo com IA
```

## ⚙️ Configuração e Instalação

### 1. Pré-requisitos
- Python 3.11 ou superior instalado.
- Ambiente virtual configurado (opcional, mas recomendado).

### 2. Gerando as Lições
Para preencher o portal com conteúdo gerado por IA, execute o script de geração:
```bash
./.venv/bin/python3 portal_estudos/generate_lessons.py
```
*O script utiliza o template `anotacao_profissional.md` para garantir alta densidade de informação.*

### 3. Rodando o Servidor
Inicie o servidor web para visualizar o portal:
```bash
python3 -m http.server 8502 --directory portal_estudos
```

## 📖 Como Usar

1.  Acesse `http://localhost:8502` no seu navegador (Brave/Edge recomendado).
2.  Navegue pelo roadmap visual para ter a visão geral do curso.
3.  **Clique em um nó central**: Para visualizar os objetivos gerais daquela área.
4.  **Clique em um nó de tópico**: Para abrir o conteúdo teórico detalhado no painel lateral.

## 🧠 Metodologia de Estudo
O conteúdo gerado segue a técnica de **Síntese Acadêmica**, focando em:
- **Metadados**: Tags e contexto.
- **Resumo Executivo**: Essência do conceito.
- **Checklist de Revisão**: Para garantir a retenção do conhecimento.

---
*Documentação gerada pelo Agente Antigravity para suporte ao aprendizado contínuo.*
