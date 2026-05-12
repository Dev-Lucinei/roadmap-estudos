import json
import os
import re
from openai import OpenAI
from backend.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    DATA_DIR,
    check_api_key,
)


def get_client():
    check_api_key()
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )


def gerar_roadmap_ia(tema):
    client = get_client()
    prompt = f"""
    Você é um arquiteto de currículo técnico. Gere um objeto JSON que represente um roadmap de estudos sobre o tema '{tema}'.
    
    O JSON deve seguir este formato estrito (estrutura v2.0 com subtopics):
    {{
      "title": "Título do Roadmap",
      "description": "Breve descrição do roadmap (opcional)",
      "nodes": [
        {{
          "id": "id-unico-kebab-case",
          "title": "Nome do Tópico Central",
          "type": "central",
          "group": "Nome da Seção (ex: Fundamentos)",
          "difficulty": "easy|medium|hard",
          "content": "Breve descrição do tópico",
          "subtopics": [
            {{
              "id": "subtopico-1",
              "title": "Nome do Subtópico",
              "difficulty": "easy|medium|hard",
              "content": "Descrição opcional",
              "subtopics": [
                {{
                  "id": "sub-subtopico-1",
                  "title": "Nome do Sub-subtópico",
                  "difficulty": "easy|medium|hard"
                }}
              ]
            }}
          ]
        }}
      ]
    }}
    
    REGRAS IMPORTANTES:
    1. Use APENAS a estrutura com "subtopics" (objetos aninhados), NÃO use "children" ou "side"
    2. IDs devem ser em kebab-case (ex: "introducao-poo", "classes-objetos")
    3. Cada nó central deve ter de 4 a 8 subtópicos
    4. Subtópicos podem ter seus próprios subtópicos (até 2 níveis de profundidade)
    5. Agrupe os tópicos em pelo menos 3 seções lógicas (groups diferentes)
    6. Distribua as dificuldades: 40% easy, 40% medium, 20% hard
    7. O output deve ser APENAS o JSON válido, sem explicações ou markdown
    8. Garanta que todos os IDs sejam únicos
    """

    response = client.chat.completions.create(
        model="openrouter/auto", messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    try:
        # Remover markdown code blocks se existirem
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```\s*$", "", content)
        json_str = re.search(r"(\{[\s\S]*\})", content).group(1)
        roadmap_data = json.loads(json_str)

        # Validar estrutura
        if not roadmap_data.get("nodes"):
            raise ValueError("JSON não contém 'nodes'")

        return roadmap_data
    except Exception as e:
        print(f"Erro ao parsear JSON: {e}")
        return None


def salvar_roadmap(tema, dados):
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
