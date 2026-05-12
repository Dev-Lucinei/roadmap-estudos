# Padrões de Formato de Conteúdo

**Data:** 11/05/2026  
**Versão:** 1.0

Este documento define os padrões obrigatórios para todos os conteúdos gerados no projeto Roadmap-Estudos.

## 📋 Índice

1. [Roadmaps](#roadmaps)
2. [Lições](#lições)
3. [Quizzes](#quizzes)
4. [Validação](#validação)

---

## 🗺️ Roadmaps

### Nomenclatura de Arquivo

**Padrão:** `roadmap_<nome_normalizado>.json`

**Regras:**
- Prefixo obrigatório: `roadmap_`
- Nome normalizado: apenas `a-z`, `0-9`, `_`
- Sem acentos ou caracteres especiais
- Extensão: `.json`

**Exemplos:**
- ✅ `roadmap_python_fundamentos_v2.json`
- ✅ `roadmap_automacao_de_tarefas_com_python.json`
- ❌ `python_fundamentos.json` (falta prefixo)
- ❌ `roadmap_automação.json` (contém acento)

### Estrutura JSON (v2.0)

```json
{
  "title": "Título do Roadmap",
  "description": "Descrição opcional",
  "nodes": [
    {
      "id": "id-kebab-case",
      "title": "Nome do Tópico Central",
      "type": "central",
      "group": "Nome da Seção",
      "difficulty": "easy|medium|hard",
      "content": "Descrição breve",
      "subtopics": [
        {
          "id": "subtopico-id",
          "title": "Nome do Subtópico",
          "difficulty": "easy|medium|hard",
          "subtopics": [
            {
              "id": "sub-subtopico-id",
              "title": "Nome do Sub-subtópico",
              "difficulty": "easy|medium|hard"
            }
          ]
        }
      ]
    }
  ]
}
```

**Campos Obrigatórios:**
- `title` (string): Título do roadmap
- `nodes` (array): Lista de nós centrais
- `nodes[].id` (string): ID único em kebab-case
- `nodes[].title` (string): Título do nó

**Campos Opcionais:**
- `description` (string): Descrição do roadmap
- `nodes[].type` (string): Tipo do nó (default: "central")
- `nodes[].group` (string): Agrupamento lógico
- `nodes[].difficulty` (string): Nível de dificuldade
- `nodes[].content` (string): Descrição do nó
- `nodes[].subtopics` (array): Subtópicos aninhados

**⚠️ Estrutura Antiga (Descontinuada):**
- Não use `children` (array de IDs)
- Não use `side` ("left"/"right")
- Migre para `subtopics` (objetos aninhados)

---

## 📝 Lições

### Nomenclatura de Arquivo

**Padrão:** `<node_id>.md`

**Regras:**
- Nome deve corresponder ao `id` do nó no roadmap
- Apenas `a-z`, `0-9`, `_`, `-`
- Extensão: `.md`

**Exemplos:**
- ✅ `logica-prog.md`
- ✅ `conceitos_poo.md`
- ✅ `funcoes-escopo.md`

### Estrutura Markdown

```markdown
# Título da Lição

## 🎯 Resumo Executivo
Breve descrição (2-3 frases) sobre o que é e por que importa.

## 📚 Conceitos-Chave
- **Conceito 1**: Explicação com exemplo
- **Conceito 2**: Explicação com exemplo
- **Conceito 3**: Explicação com exemplo

## 💡 Aplicação Prática
Exemplos de uso real com código ou cenários.

## ⚠️ Erros Comuns
- Erro 1 e como evitar
- Erro 2 e como evitar

## ✅ Checklist de Domínio
- [ ] Item 1 para validar conhecimento
- [ ] Item 2 para validar conhecimento
- [ ] Item 3 para validar conhecimento

## 🧠 Quiz de Validação

```json
[
  {
    "question": "Pergunta sobre o tópico?",
    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
    "answer": 0
  },
  {
    "question": "Segunda pergunta?",
    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
    "answer": 2
  },
  {
    "question": "Terceira pergunta?",
    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
    "answer": 1
  }
]
\```
```

**Seções Obrigatórias:**
1. Título principal (`#`)
2. Resumo Executivo
3. Conceitos-Chave
4. Quiz JSON embutido (mínimo 3 perguntas)

**Seções Opcionais:**
- Aplicação Prática
- Erros Comuns
- Checklist de Domínio
- Diagramas Mermaid (quando necessário)

---

## 🧠 Quizzes

### Quiz Embutido (em Lições)

**Formato:** Bloco de código JSON no final do arquivo markdown

```json
[
  {
    "question": "Texto da pergunta?",
    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
    "answer": 0
  }
]
```

**Regras:**
- Mínimo: 3 perguntas
- Máximo recomendado: 5 perguntas
- Cada pergunta deve ter exatamente 4 opções
- `answer` é o índice (0-3) da resposta correta
- Perguntas devem focar APENAS no tópico da lição

### Quiz Gerado Dinamicamente

**Endpoint:** `POST /api/quiz/generate`

**Request:**
```json
{
  "node_id": "logica-prog",
  "title": "Lógica de Programação"
}
```

**Response:**
```json
{
  "status": "success",
  "quiz": [
    {
      "question": "Pergunta?",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "explanation": "Explicação da resposta"
    }
  ]
}
```

**Campos Obrigatórios:**
- `question` (string): Texto da pergunta
- `options` (array[4]): Exatamente 4 alternativas
- `answer` (int): Índice 0-3 da resposta correta

**Campos Opcionais:**
- `explanation` (string): Explicação da resposta correta

---

## ✅ Validação

### Script de Validação

Execute o script para validar todos os conteúdos:

```bash
python3 scripts/validate_content_format.py
```

**O que é validado:**

**Roadmaps:**
- ✅ Nome de arquivo segue padrão `roadmap_*.json`
- ✅ Sem caracteres especiais ou acentos
- ✅ JSON válido
- ✅ Campos obrigatórios presentes
- ✅ IDs em kebab-case
- ⚠️ Detecta estrutura antiga (children/side)

**Lições:**
- ✅ Arquivo markdown válido
- ✅ Começa com título (`#`)
- ✅ Contém quiz JSON embutido
- ✅ Quiz tem mínimo 3 perguntas
- ✅ Cada pergunta tem 4 opções
- ✅ Campo `answer` é válido (0-3)

### Integração CI/CD

Adicione ao seu pipeline:

```yaml
- name: Validar Formato de Conteúdo
  run: python3 scripts/validate_content_format.py
```

---

## 🔧 Geradores de Conteúdo

### Gerador de Lições

**Arquivo:** `backend/services/ai_content/lesson_generator.py`

**Função:** `processar_node(node_id, title, node_type)`

**Garante:**
- ✅ Estrutura markdown correta
- ✅ Quiz JSON embutido com 3 perguntas
- ✅ Conteúdo focado no tópico específico
- ✅ Máximo 800 palavras (conciso)

### Gerador de Roadmaps

**Arquivo:** `backend/services/ai_content/roadmap_generator.py`

**Função:** `gerar_roadmap_ia(tema)`

**Garante:**
- ✅ Estrutura v2.0 com subtopics
- ✅ IDs em kebab-case
- ✅ Nome de arquivo normalizado (sem acentos)
- ✅ JSON válido

### Gerador de Quiz

**Arquivo:** `backend/services/quiz/quiz_service.py`

**Método:** `QuizService.generate_quiz(node_id, title)`

**Garante:**
- ✅ 4 perguntas baseadas no conteúdo da lição
- ✅ 4 opções por pergunta
- ✅ Campo `explanation` presente
- ✅ JSON válido

---

## 📊 Status Atual

**Última validação:** 11/05/2026

**Resultados:**
- ✅ 4 roadmaps válidos
- ✅ 19 lições válidas
- ⚠️ 6 lições sem quiz embutido (lições antigas)

**Ações recomendadas:**
1. Adicionar quizzes às 6 lições antigas
2. Executar validação antes de cada commit
3. Configurar CI/CD para validação automática

---

## 🔗 Referências

- [Padrão JSON Roadmap](./PADRAO_JSON_ROADMAP.md)
- [Diagnóstico de Roadmaps e Lições](./diagnostico-roadmaps-licoes.md)
- [CHANGELOG](../CHANGELOG.md)
