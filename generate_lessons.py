import os
import json
from openai import OpenAI

# --- CONFIGURAÇÃO ---
# Reutilizando sua configuração do OpenRouter encontrada no main.py
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

TEMPLATE_PATH = "../aulas/01_automacao_tarefas/anotacoes/skills/anotacao_profissional.md"
OUTPUT_DIR = "licoes"

def carregar_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

def carregar_dados_roadmap():
    # Simplificado: extraindo os nós que definimos no roadmap_data.js
    # Em uma versão real, poderíamos ler o arquivo .js ou ter um .json
    return [
        {"id": "sw-eng-basics", "title": "Software Engineering Basics", "type": "central"},
        {"id": "sdlc", "title": "SDLC (Lifecycle)", "type": "subtopic"},
        {"id": "agile-scrum", "title": "Agile & Scrum", "type": "subtopic"},
        {"id": "algos-ds", "title": "Algorithms & Data Structures", "type": "central"},
        {"id": "big-o", "title": "Big O Notation", "type": "subtopic"},
        {"id": "arch", "title": "Software Architecture", "type": "central"},
        {"id": "solid", "title": "SOLID Principles", "type": "subtopic"},
    ]

def gerar_conteudo_ia(topico, tipo):
    print(f"🤖 Gerando conteúdo para: {topico}...")
    
    prompt = f"""
    Você é um professor de Engenharia de Software. 
    Gere uma lição completa sobre '{topico}' para um desenvolvedor Fullstack.
    
    Se o tipo for 'central', foque em Objetivos Gerais e Visão Macro.
    Se o tipo for 'subtopic', foque em Teoria Detalhada, Exemplos e 'Por que importa'.
    
    Use o seguinte formato Markdown (preencha as tags entre []):
    
    # [Título do Tópico]
    ## 📋 Metadados
    - **Título:** [Título]
    - **Data:** 08/05/2026
    - **Tags:** #estudo #engenharia #[topico]
    
    ## 🎯 Resumo Executivo
    [Breve resumo do conceito]
    
    ## 📚 Conteúdo Detalhado
    [Explicação técnica profunda]
    
    ## 💡 Insights e Conexões
    - **Por que importa:** [Explicação]
    - **Conexões:** [Relacionar com outros tópicos]
    
    ## ✅ Checklist de Revisão
    - [ ] Entendi o conceito de [X]?
    - [ ] Sei aplicar [Y]?
    """

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    dados = carregar_dados_roadmap()
    
    for item in dados:
        nome_arquivo = f"{OUTPUT_DIR}/{item['id']}.md"
        
        if os.path.exists(nome_arquivo):
            print(f"⏩ Pulando {item['title']} (já existe)")
            continue
            
        conteudo = gerar_conteudo_ia(item['title'], item['type'])
        
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)
            
    print("\n🏁 Todas as lições foram geradas com sucesso!")

if __name__ == "__main__":
    main()
