---
name: roadmap_generation
version: "1.0"
description: Gera um roadmap de estudos estruturado via IA a partir de um tema
author: Antigravity
tags: [ia, roadmap, geração, openrouter]
---

## steps

1. Receber o tema do roadmap como entrada
2. Construir o prompt de geração com a estrutura JSON esperada
3. Chamar a API OpenRouter com o modelo `openrouter/auto`
4. Parsear o JSON retornado pela IA
5. Salvar o roadmap em `data/roadmap_<tema>.json`

## output

```json
{
  "title": "Título do Roadmap",
  "nodes": [
    {
      "id": "id-unico",
      "title": "Nome do Tópico",
      "type": "central",
      "group": "Nome da Seção",
      "children": ["id-filho-1"],
      "difficulty": "easy"
    }
  ]
}
```
