# Guia Rápido - Layout de Fluxograma com Expansão

## Como Usar

### Navegação Básica

1. **Visualizar Roadmap**: Os nós centrais aparecem no centro da tela
2. **Expandir Nó**: Click em um nó com ícone ▶ para ver seus subtópicos
3. **Recolher Nó**: Click novamente para ocultar os subtópicos
4. **Abrir Lição**: 
   - Nós sem subtópicos: Single click
   - Nós com subtópicos: Double click

### Controles Globais

- **📂 Expandir**: Expande todos os nós do roadmap
- **📁 Recolher**: Recolhe todos os nós, mostrando apenas centrais
- **+ Novo Tema**: Gera novo roadmap com IA
- **✏️ Modo Edição**: Ativa ferramentas de edição

## Indicadores Visuais

### Ícones
- **▶**: Nó recolhido (tem subtópicos ocultos)
- **▼**: Nó expandido (subtópicos visíveis)
- **✓**: Nó completo (lição concluída)

### Cores de Dificuldade
- **Verde**: Easy (fácil)
- **Amarelo**: Medium (médio)
- **Vermelho**: Hard (difícil)

### Estados do Nó
- **Borda normal**: Nó não visitado
- **Borda verde**: Nó completo
- **Barra inferior**: Nó recolhido com conteúdo oculto
- **Hover**: Elevação e destaque

## Estrutura Visual

```
                    [Nó Central] ▶
                         |
        +----------------+----------------+
        |                                 |
   [Subtópico 1] ▶                  [Subtópico 2]
        |
   +----+----+
   |         |
[Sub 1.1] [Sub 1.2]
```

## Dicas de Uso

1. **Comece Recolhido**: Inicie com todos os nós recolhidos para visão geral
2. **Expanda Progressivamente**: Abra apenas o que está estudando
3. **Use Double-Click**: Para abrir lições de nós com subtópicos
4. **Aproveite o Espaço**: Layout horizontal aproveita telas largas

## Atalhos e Comportamentos

- **Click**: Expandir/recolher (se tiver subtópicos) ou abrir lição
- **Double-click**: Sempre abre lição
- **Scroll**: Navegue verticalmente pelo roadmap
- **Zoom do navegador**: Ctrl + / Ctrl - para ajustar visualização

## Troubleshooting

### Nós não aparecem
- Verifique se o servidor está rodando (`python server.py`)
- Confirme que o arquivo JSON está em `data/`

### Conexões não aparecem
- Aguarde a renderização completa (animação de 1.5s)
- Verifique console do navegador para erros

### Layout quebrado
- Recarregue a página (F5)
- Limpe o cache do navegador
- Verifique se `flowchart_layout.css` está carregado

## Personalização

### Ajustar Espaçamento

Edite `flowchart_layout.js`:

```javascript
const verticalGap = 200;    // Espaço vertical entre nós centrais
const horizontalGap = 280;  // Distância horizontal dos subtópicos
```

### Mudar Cores

Edite `flowchart_layout.css`:

```css
.flowchart-node.difficulty-easy {
    border-left: 4px solid #4ade80; /* Verde */
}
```

### Adicionar Animações

```css
.flowchart-node {
    transition: all 0.3s ease;
}
```

## Próximos Passos

- [ ] Zoom e pan no canvas
- [ ] Busca de nós
- [ ] Filtros por dificuldade
- [ ] Exportar como imagem
- [ ] Modo apresentação
