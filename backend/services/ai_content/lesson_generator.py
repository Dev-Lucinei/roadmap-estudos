import os
from openai import OpenAI
from backend.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    LICOES_DIR,
    check_api_key,
)


def get_client():
    check_api_key()
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )


def gerar_conteudo_ia(topico, tipo):
    client = get_client()
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
        max_tokens=1500,
        temperature=0.7,
    )
    return response.choices[0].message.content


def processar_node(node_id, title, node_type, output_dir=None):
    if output_dir is None:
        output_dir = LICOES_DIR

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nome_arquivo = os.path.join(output_dir, f"{node_id}.md")
    conteudo = gerar_conteudo_ia(title, node_type)

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return nome_arquivo
