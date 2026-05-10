import os
from openai import OpenAI

# Define o diretório base para caminhos relativos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", ""),
)


def gerar_conteudo_ia(topico, tipo):
    prompt = f"""
    Você é um professor de Engenharia de Software especialista em Gamificação. 
    Gere uma lição completa e um quiz de validação sobre '{topico}' para um desenvolvedor Fullstack.
    
    ESTRUTURA DA LIÇÃO:
    1. # [Título do Tópico]
    2. ## 📋 Metadados (Título, Data, Tags)
    3. ## 🎯 Resumo Executivo
    4. ## 📚 Conteúdo Detalhado (Use Mermaid.js se for explicar processos ou fluxos)
    5. ## 💡 Insights e Conexões
    6. ## ✅ Checklist
    
    ESTRUTURA DO QUIZ (OBRIGATÓRIO):
    Ao final do documento, adicione um bloco de código JSON contendo EXATAMENTE 3 questões de múltipla escolha no seguinte formato:
    
    ```json
    [
      {{
        "question": "Pergunta 1?",
        "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
        "answer": 0
      }},
      ...
    ]
    ```
    Onde "answer" é o índice (0-3) da resposta correta.
    
    Idioma: Português do Brasil.
    """
    response = client.chat.completions.create(
        model="openrouter/auto", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def processar_node(node_id, title, node_type, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(BASE_DIR, "licoes")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nome_arquivo = os.path.join(output_dir, f"{node_id}.md")
    conteudo = gerar_conteudo_ia(title, node_type)

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return nome_arquivo


if __name__ == "__main__":
    # Mantém compatibilidade com execução manual
    import sys

    if len(sys.argv) > 2:
        processar_node(
            sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "subtopic"
        )
    else:
        print("Uso: python3 generate_lessons.py <id> <titulo> <tipo>")
