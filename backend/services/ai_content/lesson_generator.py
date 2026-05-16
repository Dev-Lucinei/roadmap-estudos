"""Serviço de geração de lições usando IA (OpenRouter)."""

import os
from typing import Any
from backend.core.config import (
    OPENROUTER_BASE_URL,
    LICOES_DIR,
    get_api_key,
)


def get_client() -> Any:
    """Configura e retorna o cliente OpenAI configurado para OpenRouter."""
    from openai import OpenAI

    api_key = get_api_key()
    if not api_key:
        raise PermissionError("OPENROUTER_API_KEY não configurada")

    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=api_key,
    )


def gerar_conteudo_ia(tema: str, tipo: str = "subtopic") -> str | None:
    """Gera o conteúdo da lição via OpenRouter API."""
    client = get_client()
    prompt = f"""Você é um tutor especializado. Crie uma lição detalhada em Markdown sobre: "{tema}".
Tipo de tópico: {tipo}

A lição deve conter:
1. Título chamativo
2. Explicação teórica clara e profunda
3. Exemplos práticos
4. Dicas de "Modo Zen" (foco e bem-estar)
5. Um bloco final de quiz em formato JSON (estritamente conforme exemplo abaixo).

Exemplo de bloco de quiz:
```json
[
  {{
    "question": "Pergunta 1?",
    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
    "answer": 0,
    "explanation": "Explicação da resposta"
  }}
]
```

Importante: O JSON do quiz deve conter pelo menos 3 perguntas.
Responda em Português do Brasil."""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    return content.strip() if content else None


def processar_node(
    node_id: str, title: str, node_type: str, output_dir: str | None = None
) -> str:
    """Gera uma lição para um nó do roadmap e salva em Markdown."""
    final_output_dir: str = output_dir if output_dir is not None else str(LICOES_DIR)

    if not os.path.exists(final_output_dir):
        os.makedirs(final_output_dir)

    nome_arquivo = os.path.join(final_output_dir, f"{node_id}.md")
    conteudo = gerar_conteudo_ia(title, node_type)

    if not conteudo:
        raise ValueError(f"Falha ao gerar conteúdo para o tópico: {title}")

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    return nome_arquivo
