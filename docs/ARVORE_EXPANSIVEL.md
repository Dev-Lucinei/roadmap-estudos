# Árvore Expansível - Guia de Uso

## 📋 Visão Geral

A funcionalidade de árvore expansível permite que nós do roadmap tenham **subtópicos** que podem ser expandidos/colapsados ao clicar no nó principal.

## 🎯 Como Funciona

### Estrutura de Dados

Para adicionar subtópicos a um nó, basta incluir a propriedade `subtopics` no JSON do roadmap:

```json
{
  "id": "docker",
  "title": "Docker",
  "type": "central",
  "subtopics": [
    { "id": "docker-intro", "title": "Introdução ao Docker" },
    { "id": "docker-containers", "title": "Containers vs VMs" },
    { "id": "docker-images", "title": "Imagens Docker" }
  ]
}
```

### Comportamento

1. **Nós com subtópicos** exibem um ícone `›` à direita
2. **Clicar no nó** expande/colapsa os subtópicos (não abre a lição diretamente)
3. **Clicar em um subtópico** abre a lição correspondente
4. **Animação suave** de expansão/colapso com transição CSS

## 🎨 Estilo Visual

- **Ícone de expansão**: Rotaciona 90° quando expandido
- **Subtópicos**: Aparecem abaixo do nó principal com animação de fade-in
- **Hover**: Subtópicos se deslocam levemente para a direita ao passar o mouse
- **Cores**: Mantém a paleta do projeto (glass morphism)

## 📝 Exemplo Prático

Veja o arquivo `data/roadmap_exemplo_arvore.json` para um exemplo completo com:
- Docker (3 subtópicos)
- WSL (3 subtópicos)
- Ollama (3 subtópicos)
- Aider (3 subtópicos)

## 🔧 Personalização

### CSS Customizável

```css
/* Ajustar altura máxima da expansão */
.node-subtopics.expanded {
    max-height: 2000px; /* Aumentar se tiver muitos subtópicos */
}

/* Ajustar velocidade da animação */
.node-subtopics {
    transition: max-height 0.4s ease, opacity 0.3s ease;
}

/* Ajustar espaçamento entre subtópicos */
.subtopic-item {
    margin: 8px 0; /* Aumentar para mais espaço */
}
```

### JavaScript

A função `toggleSubtopics(nodeId)` controla a expansão/colapso:

```javascript
function toggleSubtopics(nodeId) {
    const nodeEl = document.getElementById(`node-${nodeId}`);
    const subtopicsEl = document.getElementById(`subtopics-${nodeId}`);
    
    const isExpanded = nodeEl.classList.contains('expanded');
    
    if (isExpanded) {
        nodeEl.classList.remove('expanded');
        subtopicsEl.classList.remove('expanded');
    } else {
        nodeEl.classList.add('expanded');
        subtopicsEl.classList.add('expanded');
    }
}
```

## 🚀 Próximos Passos

1. **Testar**: Carregue o roadmap de exemplo no seletor
2. **Clicar**: Clique em "Docker" para ver a expansão
3. **Explorar**: Clique nos subtópicos para abrir lições
4. **Criar**: Adicione `subtopics` aos seus próprios roadmaps

## 💡 Dicas

- Use subtópicos para **conceitos relacionados** que não precisam de nós separados
- Mantenha **3-5 subtópicos** por nó para não sobrecarregar
- Subtópicos são ideais para **introduções rápidas** ou **tópicos complementares**
- Nós filhos (`children`) continuam funcionando normalmente

## 🔄 Compatibilidade

- ✅ Funciona com nós centrais e filhos
- ✅ Compatível com modo de edição
- ✅ Mantém progresso e streak
- ✅ Integrado com sistema de quiz
- ✅ Responsivo e acessível
