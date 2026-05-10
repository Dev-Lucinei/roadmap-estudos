import json
import os
import re
import sys
from openai import OpenAI

# Define o diretório base para caminhos relativos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# P1: Falha explícita se a chave não estiver configurada — sem fallback silencioso
_api_key = os.getenv("OPENROUTER_API_KEY")
if not _api_key:
    raise EnvironmentError(
        "OPENROUTER_API_KEY não encontrada. Configure a variável no arquivo .env antes de iniciar o servidor."
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=_api_key,
)


def gerar_roadmap_ia(tema):
    prompt = f"""
    Você é um arquiteto de currículo técnico. Gere um objeto JSON que represente um roadmap de estudos sobre o tema '{tema}'.
    
    O JSON deve seguir este formato estrito:
    {{
      "title": "Título do Roadmap",
      "nodes": [
        {{
          "id": "id-unico",
          "title": "Nome do Tópico",
          "type": "central",
          "group": "Nome da Seção (ex: Fundamentos)",
          "children": ["id-filho-1", "id-filho-2"],
          "content": "Breve descrição",
          "difficulty": "easy|medium|hard"
        }},
        {{
          "id": "id-filho-1",
          "title": "Subtópico",
          "type": "subtopic",
          "side": "left|right",
          "difficulty": "easy|medium|hard"
        }}
      ]
    }}
    
    REGRAS:
    1. O primeiro nó deve ser 'central'.
    2. Agrupe os tópicos em pelo menos 3 seções lógicas.
    3. Cada nó 'central' deve ter de 4 a 8 'children'.
    4. Atribua 'side' (left/right) equilibradamente para os subtopics.
    5. O output deve ser APENAS o JSON, sem explicações.
    """

    response = client.chat.completions.create(
        model="openrouter/auto", messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    try:
        json_str = re.search(r"(\{[\s\S]*\})", content).group(1)
        return json.loads(json_str)
    except Exception as e:
        print(f"Erro ao parsear JSON: {e}")
        return None


def salvar_roadmap(tema, dados):
    data_dir = os.path.join(BASE_DIR, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    filename = os.path.join(data_dir, f"roadmap_{tema.lower().replace(' ', '_')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    return filename


if __name__ == "__main__":
    if len(sys.argv) > 1:
        tema = " ".join(sys.argv[1:])
        dados = gerar_roadmap_ia(tema)
        if dados:
            salvar_roadmap(tema, dados)
