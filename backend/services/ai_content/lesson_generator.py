"""Serviço de geração de lições usando IA (OpenRouter)."""

import os

from openai import OpenAI

from backend.core.config import (
    LICOES_DIR,
    OPENROUTER_BASE_URL,
    get_api_key,
)

SYSTEM_PROMPT = (
    "Você é um Arquiteto Pedagógico Sênior e Especialista em Design Instrucional, "
    "com PhD em Ciência Cognitiva e vasta experiência em criar conteúdos educacionais "
    "de alta retenção para plataformas EAD de tecnologia. Sua expertise combina rigor "
    "técnico, clareza didática e a aplicação de metodologias ativas de aprendizagem."
)


def get_client() -> OpenAI:
    """Configura e retorna o cliente OpenAI configurado para OpenRouter."""
    api_key = get_api_key()
    if not api_key:
        raise PermissionError("OPENROUTER_API_KEY não configurada")

    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
    )


def _montar_contexto(
    *,
    tema: str,
    tipo: str,
    content: str | None = None,
    group: str | None = None,
    difficulty: str | None = None,
    roadmap_title: str | None = None,
    subtopics: list[str] | None = None,
) -> str:
    """Monta o bloco de contexto do roadmap para o prompt."""
    linhas = ["**[CONTEXTO DO ROADMAP]**"]

    if roadmap_title:
        linhas.append(f"- Trilha de estudos: {roadmap_title}")
    if group:
        linhas.append(f"- Seção: {group}")
    if difficulty:
        linhas.append(f"- Dificuldade: {difficulty}")
    if subtopics:
        linhas.append(f"- Tópicos relacionados: {', '.join(subtopics)}")

    linhas.append("")
    linhas.append("**[TEMA]**")
    linhas.append(tema)

    if content:
        linhas.append("")
        linhas.append("**[DESCRIÇÃO]**")
        linhas.append(content)

    linhas.append("")
    linhas.append("**[TIPO]**")
    linhas.append(tipo)

    return "\n".join(linhas)


def _montar_prompt(contexto: str) -> str:
    """Monta o prompt completo do usuário."""
    return f"""{contexto}

**[MISSÃO]**
Gere uma lição educacional completa e detalhada EXCLUSIVAMENTE sobre o tema indicado acima.
A lição DEVE estar 100% alinhada com o contexto do roadmap fornecido.
Se o tema é "Containers Docker", a lição DEVE ser sobre containers Docker — NÃO sobre Git,
CI/CD, ou qualquer outro assunto. Respeite rigorosamente o título, a descrição e a seção indicados.

**[INSTRUÇÕES]**
1. **Formatação**: Markdown (GitHub Flavored Markdown).
2. **Idioma**: Português do Brasil (PT-BR) com tom profissional, encorajador e técnico.
3. **Profundidade**: Intermediária, evitando generalismos.
4. **Sem meta-comentários**: Não inclua "Aqui está sua lição" ou similares.
5. **Foco absoluto**: Todo o conteúdo (teoria, exemplos, quiz) DEVE ser sobre o tema indicado acima.

**[ESTRUTURA OBRIGATÓRIA]**

# [Título Chamativo e Profissional]

## 1. Introdução e Fundamentos
[Texto explicando a importância do tema e conceitos base]

## 2. Imersão Técnica
[Explicação teórica aprofundada com uso de negrito para termos chave]

## 3. Aplicação Prática
[Exemplos de código, diagramas em texto ou cenários passo a passo]

## 4. Conexão Modo Zen
> [Dicas customizadas para manter o foco e bem-estar durante o estudo deste tema específico]

## 5. Avaliação de Retenção
```json
[
  {{
    "question": "Pergunta técnica sobre o conteúdo?",
    "options": ["Opção 0", "Opção 1", "Opção 2", "Opção 3"],
    "answer": 0,
    "explanation": "Explicação pedagógica sobre a resposta correta."
  }}
]
```

**[REGRAS DO QUIZ]**
- Mínimo de 3 perguntas.
- Campos obrigatórios: `question` (string), `options` (array de 4 strings),
  `answer` (índice 0-3), `explanation` (string detalhando o porquê).
- Proibido incluir textos explicativos antes ou depois do bloco JSON.
- O JSON deve ser sintaticamente perfeito e validável por parsers padrão."""


def gerar_conteudo_ia(
    *,
    tema: str,
    tipo: str = "subtopic",
    content: str | None = None,
    group: str | None = None,
    difficulty: str | None = None,
    roadmap_title: str | None = None,
    subtopics: list[str] | None = None,
) -> str | None:
    """Gera o conteúdo da lição via OpenRouter API."""
    client = get_client()

    contexto = _montar_contexto(
        tema=tema,
        tipo=tipo,
        content=content,
        group=group,
        difficulty=difficulty,
        roadmap_title=roadmap_title,
        subtopics=subtopics,
    )
    prompt = _montar_prompt(contexto)

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1500,
        temperature=0.7,
    )
    content_resp = response.choices[0].message.content
    return content_resp.strip() if content_resp else None


def processar_node(
    node_id: str,
    title: str,
    node_type: str,
    output_dir: str | None = None,
    *,
    content: str | None = None,
    group: str | None = None,
    difficulty: str | None = None,
    roadmap_title: str | None = None,
    subtopics: list[str] | None = None,
) -> str:
    """Gera uma lição para um nó do roadmap e salva em Markdown."""
    final_output_dir: str = output_dir if output_dir is not None else str(LICOES_DIR)

    if not os.path.exists(final_output_dir):
        os.makedirs(final_output_dir)

    nome_arquivo = os.path.join(final_output_dir, f"{node_id}.md")
    conteudo = gerar_conteudo_ia(
        tema=title,
        tipo=node_type,
        content=content,
        group=group,
        difficulty=difficulty,
        roadmap_title=roadmap_title,
        subtopics=subtopics,
    )

    if not conteudo:
        raise ValueError(f"Falha ao gerar conteúdo para o tópico: {title}")

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    return nome_arquivo
