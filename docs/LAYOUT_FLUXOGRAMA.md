# Layout de Fluxograma - Documentação

## Visão Geral

O sistema de layout de fluxograma oferece uma visualização alternativa dos roadmaps, apresentando os tópicos como um mindmap/fluxograma profissional com conexões visuais entre os nós.

## Características

### 1. Distribuição Espacial Inteligente

- **Nós Centrais**: Posicionados verticalmente no centro da tela
- **Subtópicos Nível 1**: Distribuídos alternadamente em colunas esquerda/direita
- **Subtópicos Nível 2**: Expandem para as laterais externas (mais à esquerda ou mais à direita)

### 2. Conexões Visuais

- **Linhas SVG**: Conexões desenhadas com curvas bezier suaves
- **Tipos de Conexão**:
  - Linhas sólidas para conexões principais (nó central → subtópico)
  - Linhas tracejadas para sub-conexões (subtópico → sub-subtópico)
- **Cores**: Baseadas no tema (accent-color para principais, glass-border para secundárias)

### 3. Estilização Profissional

- **Glass Morphism**: Mantém o design atual com backdrop-filter e transparências
- **Indicadores de Dificuldade**: Borda colorida à esquerda (verde/amarelo/vermelho)
- **Badges**: Etiquetas de dificuldade no canto superior direito
- **Estados Visuais**:
  - Hover: Elevação e destaque da borda
  - Completo: Borda verde e ícone de check
  - Animações suaves de entrada

## Arquivos do Sistema

### `flowchart_layout.js`

Classe principal `FlowchartLayout` com métodos:

- `calculateLayout(roadmapData)`: Calcula posições dos nós
- `drawConnections()`: Desenha linhas SVG entre nós
- `renderNodes()`: Renderiza elementos DOM dos nós
- `render(roadmapData)`: Método principal de renderização

### `flowchart_layout.css`

Estilos específicos para o layout de fluxograma:

- `.flowchart-container`: Container principal com scroll
- `.flowchart-svg`: Camada SVG para conexões
- `.flowchart-node`: Estilo dos nós com variações por nível
- `.flowchart-node-badge`: Badges de dificuldade
- Animações de entrada e transições

### `test_flowchart.html`

Arquivo de demonstração standalone para testar o layout sem o sistema completo.

## Uso

### Alternância de Layout

No sistema principal, use o botão "🔀 Layout" no header para alternar entre:

- **Modo Árvore**: Layout hierárquico expansível (padrão)
- **Modo Fluxograma**: Layout de mindmap com conexões visuais

### Integração no Código

```javascript
// Criar instância
const flowchart = new FlowchartLayout('container-id', 'svg-id');

// Renderizar roadmap
flowchart.render(roadmapData);

// Customizar click handler
flowchart.onNodeClick = function(node) {
    // Sua lógica aqui
};
```

## Algoritmo de Posicionamento

### Cálculo de Posições

```
Para cada nó central (índice i):
  - X = centro da tela
  - Y = 100 + (i × 600)
  
  Para cada subtópico (índice j):
    - Se j é par: X = centro - 280px (esquerda)
    - Se j é ímpar: X = centro + 280px (direita)
    - Y = Y_central + (j × 120) - offset
    
    Para cada sub-subtópico (índice k):
      - Se pai está à esquerda: X = centro - 560px
      - Se pai está à direita: X = centro + 560px
      - Y = Y_pai + (k × 80) - offset
```

### Gaps e Espaçamentos

- **Vertical entre centrais**: 600px
- **Horizontal nível 1**: 280px do centro
- **Horizontal nível 2**: 560px do centro (2× o nível 1)
- **Vertical entre subtópicos**: 120px
- **Vertical entre sub-subtópicos**: 80px

## Responsividade

Em telas menores (< 1400px):
- Redução de fonte
- Ajuste de padding

Em telas mobile (< 768px):
- Fonte ainda menor
- Padding reduzido
- Scroll horizontal habilitado

## Extensibilidade

### Adicionar Novos Níveis

Para suportar níveis 3+, adicione lógica em `calculateLayout()`:

```javascript
// Nível 3
if (subsubtopic.subtopics) {
    subsubtopic.subtopics.forEach((level3, idx) => {
        positions.set(level3.id, {
            x: centerX + (horizontalGap * 3), // Mais distante
            y: subsubY + (idx * 60),
            level: 3,
            // ...
        });
    });
}
```

### Customizar Conexões

Modifique `drawConnections()` para alterar estilo das linhas:

```javascript
path.setAttribute('stroke-width', '3'); // Linhas mais grossas
path.setAttribute('stroke-dasharray', '10,5'); // Padrão diferente
```

### Adicionar Interatividade

```javascript
nodeEl.ondblclick = () => {
    // Ação no duplo clique
};

nodeEl.oncontextmenu = (e) => {
    e.preventDefault();
    // Menu de contexto
};
```

## Performance

- **Renderização**: O(n) onde n = número total de nós
- **Conexões SVG**: O(c) onde c = número de conexões
- **Otimizações**:
  - Uso de `Map` para lookup rápido de posições
  - Animações via CSS (GPU-accelerated)
  - Lazy rendering de sub-níveis

## Comparação com Layout de Árvore

| Aspecto | Árvore | Fluxograma |
|---------|--------|------------|
| Espaço Horizontal | Subutilizado | Bem aproveitado |
| Hierarquia Visual | Clara (indentação) | Clara (posicionamento) |
| Conexões | Linhas simples | Curvas bezier |
| Expansão | Interativa (click) | Sempre expandido |
| Melhor Para | Navegação profunda | Visão geral |

## Troubleshooting

### Nós Sobrepostos

Ajuste os gaps em `calculateLayout()`:
```javascript
const verticalGap = 250; // Aumentar
const horizontalGap = 320; // Aumentar
```

### Conexões Não Aparecem

Verifique se o SVG tem altura suficiente:
```javascript
this.svg.style.height = `${maxY + 300}px`; // Aumentar margem
```

### Performance Lenta

Para roadmaps muito grandes (100+ nós):
- Implemente virtualização
- Renderize apenas nós visíveis no viewport
- Use `requestAnimationFrame` para animações

## Roadmap Futuro

- [ ] Zoom e pan no canvas
- [ ] Minimap para navegação
- [ ] Exportar como imagem (PNG/SVG)
- [ ] Layout automático com algoritmo de força
- [ ] Agrupamento visual por categoria
- [ ] Filtros por dificuldade/status
