import os
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


def gerar_conteudo_ia(topico, tipo):
    prompt = f"""
    Você é um professor de Engenharia de Software especialista em criar conteúdo educacional focado e conciso.
    
    TAREFA: Gere uma lição EXCLUSIVAMENTE sobre '{topico}'. 
    
    RESTRIÇÕES CRÍTICAS:
    - Aborde APENAS o tópico '{topico}' - não divague para tópicos relacionados
    - Mantenha o conteúdo conciso e direto (máximo 800 palavras)
    - Foque em conceitos práticos e aplicáveis
    - Use exemplos específicos do tópico solicitado
    
    ESTRUTURA DA LIÇÃO:
    1. # {topico}
    2. ## 🎯 Resumo Executivo (2-3 frases sobre o que é e por que importa)
    3. ## 📚 Conceitos-Chave (3-5 pontos principais com exemplos práticos)
    4. ## 💡 Aplicação Prática (1-2 exemplos de uso real)
    5. ## ⚠️ Erros Comuns (2-3 armadilhas a evitar)
    6. ## ✅ Checklist de Domínio (3-5 itens para validar conhecimento)
    
    ESTRUTURA DO QUIZ (OBRIGATÓRIO):
    Ao final do documento, adicione um bloco de código JSON contendo EXATAMENTE 3 questões de múltipla escolha focadas APENAS em '{topico}':
    
    ```json
    [
      {{
        "question": "Pergunta específica sobre {topico}?",
        "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
        "answer": 0
      }},
      {{
        "question": "Segunda pergunta sobre {topico}?",
        "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
        "answer": 1
      }},
      {{
        "question": "Terceira pergunta sobre {topico}?",
        "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
        "answer": 2
      }}
    ]
    ```
    
    Onde "answer" é o índice (0-3) da resposta correta.
    
    IMPORTANTE: 
    - Use Mermaid.js APENAS se for essencial para explicar um fluxo ou diagrama
    - Mantenha linguagem clara e objetiva
    - Idioma: Português do Brasil
    - NÃO mencione outros tópicos além de '{topico}'
    """
    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,  # Limita resposta para manter conteúdo conciso
        temperature=0.7,
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
