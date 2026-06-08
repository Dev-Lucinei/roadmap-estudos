"""Serviço de geração de lições usando IA (OpenRouter)."""

import os

from openai import OpenAI

from backend.core.config import (
    LICOES_DIR,
    OPENROUTER_BASE_URL,
    get_api_key,
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


def gerar_conteudo_ia(tema: str, tipo: str = "subtopic") -> str | None:
    """Gera o conteúdo da lição via OpenRouter API."""
    client = get_client()
    prompt = (
        f'Você é um tutor especializado. Crie uma lição detalhada em Markdown sobre: "{tema}".\n'
        f"Tipo de tópico: {tipo}\n\n"
        "A lição deve conter:\n"
        "1. Título chamativo\n"
        "2. Explicação teórica clara e profunda\n"
        "3. Exemplos práticos\n"
        '4. Dicas de "Modo Zen" (foco e bem-estar)\n'
        "5. Um bloco final de quiz em formato JSON (estritamente conforme exemplo abaixo).\n\n"
        "Exemplo de bloco de quiz:\n"
        "```json\n"
        "[\n"
        "  {{\n"
        '    "question": "Pergunta 1?",\n'
        '    "options": ["Opção A", "Opção B", "Opção C", "Opção D"],\n'
        '    "answer": 0,\n'
        '    "explanation": "Explicação da resposta"\n'
        "  }}\n"
        "]\n"
        "```\n\n"
        "Importante: O JSON do quiz deve conter pelo menos 3 perguntas.\n"
        "Responda em Português do Brasil."
    )

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    return content.strip() if content else None


def processar_node(node_id: str, title: str, node_type: str, output_dir: str | None = None) -> str:
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
