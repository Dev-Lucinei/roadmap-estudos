"""Geração de lições educacionais via OpenRouter API."""

import os
from backend.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    LICOES_DIR,
    check_api_key,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


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


def gerar_conteudo_ia(topico: str, tipo: str) -> str | None:
    """Gera conteúdo de lição via OpenRouter API."""
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


def processar_node(
    node_id: str, title: str, node_type: str, output_dir: str | None = None
) -> str:
    """Gera uma lição para um nó do roadmap e salva em Markdown."""
    if output_dir is None:
        output_dir = LICOES_DIR

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    nome_arquivo = os.path.join(output_dir, f"{node_id}.md")
    conteudo = gerar_conteudo_ia(title, node_type)

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return nome_arquivo
