"""Geração de roadmaps de estudo via OpenRouter API."""

import json
import logging
import os
import re
from typing import Any, cast

from backend.core.config import (
    DATA_DIR,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    check_api_key,
)

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment,misc]


# Type aliases for roadmap structure
RoadmapNode = dict[str, Any]
RoadmapData = dict[str, str | list[RoadmapNode]]


def get_client() -> "OpenAI":
    """Retorna cliente OpenAI configurado para OpenRouter."""
    if OpenAI is None:
        raise ImportError("openai package not installed")
    check_api_key()
    if OpenAI is None:
        raise ImportError("openai package not installed")
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )


def gerar_roadmap_ia(tema: str) -> RoadmapData | None:
    """Gera um roadmap de estudos via OpenRouter API."""
    client = get_client()
    prompt = (
        f"Você é um arquiteto de currículo técnico. Gere um objeto JSON que represente "
        f"um roadmap de estudos sobre o tema '{tema}'.\n\n"
        "O JSON deve seguir este formato estrito (estrutura v2.0 com subtopics):\n"
        "{\n"
        '  "title": "Título do Roadmap",\n'
        '  "description": "Breve descrição do roadmap (opcional)",\n'
        '  "nodes": [\n'
        "    {\n"
        '      "id": "id-unico-kebab-case",\n'
        '      "title": "Nome do Tópico Central",\n'
        '      "type": "central",\n'
        '      "group": "Nome da Seção (ex: Fundamentos)",\n'
        '      "difficulty": "easy|medium|hard",\n'
        '      "content": "Breve descrição do tópico",\n'
        '      "subtopics": [\n'
        "        {\n"
        '          "id": "subtopico-1",\n'
        '          "title": "Nome do Subtópico",\n'
        '          "difficulty": "easy|medium|hard",\n'
        '          "content": "Descrição opcional",\n'
        '          "subtopics": [\n'
        "            {\n"
        '              "id": "sub-subtopico-1",\n'
        '              "title": "Nome do Sub-subtópico",\n'
        '              "difficulty": "easy|medium|hard"\n'
        "            }\n"
        "          ]\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "REGRAS IMPORTANTES:\n"
        "1. Use APENAS a estrutura com 'subtopics' (objetos aninhados)\n"
        "2. IDs devem ser em kebab-case (ex: 'introducao-poo', 'classes-objetos')\n"
        "3. Cada nó central deve ter de 4 a 8 subtópicos\n"
        "4. Subtópicos podem ter seus próprios subtópicos (até 2 níveis de profundidade)\n"
        "5. Agrupe os tópicos em pelo menos 3 seções lógicas (groups diferentes)\n"
        "6. Distribua as dificuldades: 40% easy, 40% medium, 20% hard\n"
        "7. O output deve ser APENAS o JSON válido, sem explicações ou markdown\n"
        "8. Garanta que todos os IDs sejam únicos"
    )

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um arquiteto de currículo técnico."
                    " Gere APENAS JSON válido, sem explicações"
                    " ou markdown."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=4000,
        temperature=0.7,
    )

    content = response.choices[0].message.content
    if not content:
        return None

    try:
        # Remover markdown code blocks se existirem
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```\s*$", "", content)
        match = re.search(r"(\{[\s\S]*\})", content)
        if not match:
            return None
        json_str = match.group(1)
        roadmap_data = json.loads(json_str)

        # Validar estrutura
        if not roadmap_data.get("nodes"):
            raise ValueError("JSON não contém 'nodes'")

        return cast(RoadmapData, roadmap_data)
    except Exception as e:
        logger.error("Erro ao parsear JSON: %s", e)
        return None


def salvar_roadmap(tema: str, dados: RoadmapData) -> str:
    """Salva um roadmap no diretório de dados."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Normalizar o nome do arquivo removendo acentos e caracteres especiais
    import unicodedata

    tema_normalizado = unicodedata.normalize("NFKD", tema)
    tema_normalizado = tema_normalizado.encode("ASCII", "ignore").decode("ASCII")
    tema_normalizado = tema_normalizado.lower().replace(" ", "_")
    tema_normalizado = re.sub(r"[^a-z0-9_]", "", tema_normalizado)

    filename = os.path.join(DATA_DIR, f"roadmap_{tema_normalizado}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    return filename
