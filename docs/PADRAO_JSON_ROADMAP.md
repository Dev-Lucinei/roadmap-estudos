# Padrão JSON para Roadmaps

## Estrutura Oficial (v2.0)

A partir de agora, todos os roadmaps devem seguir esta estrutura:

```json
{
  "title": "Título do Roadmap",
  "description": "Descrição opcional do roadmap",
  "nodes": [
    {
      "id": "identificador-unico",
      "title": "Título do Nó",
      "type": "central",
      "group": "Nome do Grupo",
      "difficulty": "easy|medium|hard",
      "content": "Descrição opcional do conteúdo",
      "subtopics": [
        {
          "id": "subtopico-1",
          "title": "Título do Subtópico",
          "difficulty": "easy|medium|hard",
          "content": "Descrição opcional",
          "subtopics": [
            {
              "id": "subtopico-1-1",
              "title": "Subtópico Aninhado"
            }
          ]
        }
      ]
    }
  ]
}
```

## Campos Obrigatórios

### Nível Raiz
- `title` (string): Título do roadmap
- `nodes` (array): Lista de nós principais

### Nós Centrais
- `id` (string): Identificador único (kebab-case)
- `title` (string): Título exibido
- `type` (string): Sempre "central" para nós principais
- `group` (string): Categoria/agrupamento
- `difficulty` (string): "easy", "medium" ou "hard"

### Subtópicos
- `id` (string): Identificador único
- `title` (string): Título exibido

## Campos Opcionais

- `description` (string): Descrição do roadmap (nível raiz)
- `content` (string): Descrição do nó/subtópico
- `difficulty` (string): Dificuldade do subtópico
- `subtopics` (array): Lista de subtópicos aninhados (recursivo)

## Regras de Nomenclatura

1. **IDs**: Usar kebab-case (ex: `docker-conceitos`, `wsl-instalacao`)
2. **Hierarquia**: IDs de subtópicos devem incluir prefixo do pai (ex: `docker-conceitos`, `docker-conceitos-containers`)
3. **Títulos**: Usar capitalização adequada e ser descritivo

## Migração da Estrutura Antiga

### Estrutura Antiga (DESCONTINUADA)
```json
{
  "children": ["id1", "id2"],
  "side": "left",
  "type": "subtopic"
}
```

### Estrutura Nova (ATUAL)
```json
{
  "subtopics": [
    { "id": "id1", "title": "..." },
    { "id": "id2", "title": "..." }
  ]
}
```

## Exemplo Completo

Ver: `data/roadmap_exemplo_arvore.json`

## Compatibilidade

O sistema ainda suporta a estrutura antiga para retrocompatibilidade, mas novos roadmaps devem usar exclusivamente a estrutura nova.
