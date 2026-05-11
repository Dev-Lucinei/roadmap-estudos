# Sistema de Avaliação de Conhecimento

## Visão Geral

O sistema de avaliação garante que o usuário tenha conhecimento adequado antes de avançar para tópicos mais complexos. Oferece duas modalidades de avaliação:

1. **Checklist de Auto-avaliação** (rápido, sem custo de tokens)
2. **Quiz Diagnóstico IA** (assertivo, com avaliação automática)

## Fluxo de Avaliação

```
Usuário clica em tópico com pré-requisitos
    ↓
Modal de Avaliação abre com 2 tabs
    ↓
┌─────────────────┬─────────────────┐
│  📋 Checklist   │   🧠 Quiz IA    │
└─────────────────┴─────────────────┘
    ↓                    ↓
Auto-avaliação      Gera 4 perguntas
5 itens (IA)        Usuário responde
    ↓                    ↓
Marca ≥70%          IA avalia respostas
    ↓                    ↓
┌────────────────────────────────────┐
│  ✅ Aprovado  ou  ⚠️ Revisar       │
└────────────────────────────────────┘
```

## 1. Checklist de Auto-avaliação

### Características
- **Geração**: IA cria 5 itens objetivos sobre o tópico
- **Critério**: Usuário deve marcar ≥70% (4 de 5 itens)
- **Tempo**: ~2 segundos
- **Custo**: ~200 tokens (geração única)

### Exemplo de Checklist
Para o tópico "Funções em Python":
- ✅ Entendo como definir funções com `def`
- ✅ Sei usar parâmetros e argumentos
- ✅ Conheço a diferença entre `return` e `print`
- ⬜ Sei criar funções com argumentos padrão
- ⬜ Entendo escopo de variáveis (local vs global)

**Resultado**: 3/5 (60%) → ⚠️ Revisar

## 2. Quiz Diagnóstico IA

### Características
- **Geração**: IA cria 4 perguntas dissertativas curtas
- **Contexto**: Usa primeiros 500 chars da lição para relevância
- **Limite**: 500 caracteres por resposta
- **Avaliação**: IA analisa e retorna score 0-100
- **Critério**: Score ≥70 para aprovação

### Exemplo de Quiz
**Tópico**: Funções em Python

**Pergunta 1**: O que é uma função e qual sua importância?
**Resposta**: _"Uma função é um bloco de código reutilizável que executa uma tarefa específica. É importante para organizar código e evitar repetição."_

**Pergunta 2**: Como você define uma função com parâmetros?
**Resposta**: _"Uso def nome_funcao(parametro1, parametro2): e dentro do bloco coloco o código."_

**Avaliação IA**:
- Score: 85/100
- Feedback: "Demonstra compreensão sólida dos conceitos fundamentais. Bom uso de exemplos práticos."
- Resultado: ✅ Aprovado

## Segurança e Proteção

### Proteção contra Prompt Injection

```python
def _sanitize_input(self, text, max_length=500):
    """Remove caracteres de controle e limita tamanho."""
    sanitized = "".join(char for char in text if char.isprintable() or char.isspace())
    return sanitized[:max_length].strip()
```

**Proteções implementadas**:
- ✅ Remove caracteres não-printable
- ✅ Limita a 500 caracteres por resposta
- ✅ Valida JSON retornado pela IA
- ✅ Máximo 5 respostas por quiz
- ✅ Prompts estruturados com separadores claros

### Limite de Tokens

| Operação | Tokens Max | Custo Estimado |
|----------|-----------|----------------|
| Gerar Checklist | 200 | ~$0.0002 |
| Gerar Quiz | 300 | ~$0.0003 |
| Avaliar Respostas | 200 | ~$0.0002 |

**Total por avaliação completa**: ~$0.0007 (menos de 1 centavo)

## Fallback Inteligente

Se a IA falhar, o sistema usa fallbacks:

### Checklist Fallback
```javascript
{
  "items": [
    "Entendo os conceitos fundamentais de {tópico}",
    "Consigo explicar {tópico} com minhas próprias palavras",
    "Sei aplicar {tópico} em exemplos práticos",
    "Conheço os erros comuns relacionados a {tópico}",
    "Consigo relacionar {tópico} com outros conceitos"
  ]
}
```

### Quiz Fallback
```javascript
{
  "questions": [
    {"question": "O que é {tópico} e qual sua importância?"},
    {"question": "Quais são os principais conceitos relacionados a {tópico}?"},
    {"question": "Como você aplicaria {tópico} na prática?"},
    {"question": "Quais erros comuns devem ser evitados ao trabalhar com {tópico}?"}
  ]
}
```

### Avaliação Fallback
Se a IA não responder, avalia por tamanho:
- **Aprovado**: Média ≥10 palavras por resposta
- **Reprovado**: Respostas muito curtas

## API Endpoints

### POST /api/generate-checklist
```json
Request:
{
  "topic": "Funções em Python"
}

Response:
{
  "status": "success",
  "items": ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
}
```

### POST /api/generate-diagnostic-quiz
```json
Request:
{
  "topic": "Funções em Python"
}

Response:
{
  "status": "success",
  "questions": [
    {"question": "Pergunta 1?"},
    {"question": "Pergunta 2?"},
    {"question": "Pergunta 3?"},
    {"question": "Pergunta 4?"}
  ]
}
```

### POST /api/evaluate-quiz
```json
Request:
{
  "topic": "Funções em Python",
  "answers": [
    "Resposta 1...",
    "Resposta 2...",
    "Resposta 3...",
    "Resposta 4..."
  ]
}

Response:
{
  "status": "success",
  "score": 85,
  "passed": true,
  "feedback": "Demonstra compreensão sólida dos conceitos fundamentais."
}
```

## Interface do Usuário

### Modal de Avaliação
- **Header**: Gradiente roxo com título do tópico
- **Tabs**: Alterna entre Checklist e Quiz
- **Animações**: Fade in, slide in, scale in
- **Responsivo**: 90% largura, max 700px

### Modal de Resultado
- **Aprovado**: Fundo verde, ícone ✅
- **Reprovado**: Fundo laranja, ícone ⚠️
- **Score**: Exibido em destaque (se quiz)
- **Dica**: Sugestão de revisão (se reprovado)

## Boas Práticas

### Para Usuários
1. **Checklist**: Use para revisão rápida de tópicos conhecidos
2. **Quiz**: Use para validação profunda antes de tópicos críticos
3. **Respostas**: Seja específico, mencione conceitos-chave
4. **Limite**: Respostas concisas (1-3 frases) são suficientes

### Para Desenvolvedores
1. **Sanitização**: Sempre sanitize inputs antes de enviar à IA
2. **Fallback**: Implemente fallbacks para todas as operações com IA
3. **Validação**: Valide JSON retornado pela IA antes de usar
4. **Limites**: Respeite limites de caracteres e tokens
5. **Contexto**: Carregue contexto da lição para perguntas relevantes

## Métricas de Sucesso

- **Taxa de Aprovação**: 70% (configurável)
- **Tempo Médio (Checklist)**: ~30 segundos
- **Tempo Médio (Quiz)**: ~3 minutos
- **Custo por Avaliação**: <$0.001
- **Taxa de Fallback**: <5% (meta)

## Roadmap Futuro

- [ ] Histórico de avaliações por usuário
- [ ] Recomendações personalizadas de revisão
- [ ] Dificuldade adaptativa (mais perguntas se score baixo)
- [ ] Integração com sistema de XP/gamificação
- [ ] Analytics de lacunas de conhecimento mais comuns
