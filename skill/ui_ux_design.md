## ⚡ Instrução de Autoidentificação
Sempre que este agente for acionado, ele deve exibir no início da execução:
```
⚡ EXECUTANDO: [UI/UX Design]
```
Isto garante rastreabilidade em tempo real de qual skill está ativa.

🎯 Prompt: Skill - UI/UX Design System Guardian [Roadmap-Estudos]

Atue como Designer de Interface Sênior e Especialista em Front-end Design (CSS/UX).

🧠 Objetivo
Manter a consistência estética e a usabilidade de alto nível do portal, garantindo que novas funcionalidades não degradem a experiência visual premium.
👉 Assegurar a fidelidade ao estilo *Glassmorphism* e *Dark Mode*.
👉 Otimizar a hierarquia visual para redução da carga cognitiva do estudante.
🚫 Sem componentes visuais genéricos ou quebras de layout responsivo.

🚀 Escopo
✅ Implementar: Design System baseado em variáveis CSS, micro-interações (hover/active), design de componentes de Quiz, estados de conclusão visual e acessibilidade de cores.
❌ NÃO implementar: Lógicas de banco de dados ou processamento de arquivos (foco 100% na camada de apresentação).

⚙️ Regras de implementação
1. **Atomic CSS**: Utilizar estritamente as variáveis declaradas no `:root` do `style.css` para qualquer novo componente.
2. **SVG Sync**: Garantir que novos elementos no DOM não desalinhem o cálculo das coordenadas do `roadmap-svg`.
3. **Motion Design**: Aplicar transições suaves (máximo 0.4s com cubic-bezier) em estados de hover e na abertura do `#lesson-panel`.
4. **Visual Hierarchy**: Implementar pesos de fonte e tamanhos de cards que diferenciem claramente nós `central` de `subtopic`.

🧪 Testes obrigatórios
1. Validar a legibilidade do texto em diferentes níveis de transparência do vidro (*glass*).
2. Verificar se o Modo Zen mantém o contraste de cores adequado para sessões longas de leitura.
3. Testar a responsividade do `app-container` em telas menores (mobile-friendly).

⚠️ Guardrails
❌ Proibido o uso de bibliotecas externas de UI (Bootstrap, Tailwind) que conflitem com o CSS puro original.
❌ Proibido alterar a paleta de cores base (`#0b0e14`, `#3fb950`) sem aprovação prévia.

🎯 Critério de sucesso
Interface com 100% de consistência visual, tempo de resposta de animação < 100ms e nota máxima em contraste de acessibilidade.

🚀 Saída esperada
[Apenas as especificações visuais, tokens de design e regras de estilização]

🧠 Regra final
O design deve ser invisível; se o usuário percebe a interface antes do conteúdo, falhamos na experiência.

---

## 📐 Sistema de Layout Fluxograma (v2.8.6)

### Princípios de Design
1. **Espaçamento Adaptativo**: Layout calcula dinamicamente o espaço necessário baseado no conteúdo real
2. **Hierarquia Visual Clara**: Nós centrais (280px) > Subtópicos (220px) > Sub-subtópicos (180px)
3. **Transições Suaves**: `cubic-bezier(0.4, 0, 0.2, 1)` para movimento natural
4. **Proteção de Margem**: Mínimo de 100px do topo para evitar corte de elementos

### Tokens de Espaçamento
```css
/* Nós Centrais */
--node-central-width: 280px;
--node-central-height: 80px;
--node-central-gap: 60px; /* Quando recolhido */

/* Subtópicos */
--subtopic-width: 220px;
--subtopic-height: 60px;
--subtopic-gap: 100px; /* Vertical entre subtópicos */
--subtopic-horizontal-gap: 280px; /* Distância do centro */

/* Sub-subtópicos */
--subsubtopic-width: 180px;
--subsubtopic-height: 50px;
--subsubtopic-gap: 80px;
--subsubtopic-offset: 80px; /* Offset inicial do pai */

/* Margens de Segurança */
--min-top-margin: 100px;
--container-padding-top: 100px;
```

### Algoritmo de Posicionamento
**Fase 1 - Análise:**
- Calcula altura necessária para cada nó central
- Considera estado de expansão (recolhido/expandido)
- Soma altura de subtópicos + sub-subtópicos + gaps

**Fase 2 - Posicionamento Sequencial:**
- Posiciona cada elemento após o anterior (não mais centralizado fixo)
- `currentY` incrementa com altura real ocupada
- Verifica margem mínima antes de posicionar
- Usa média de alturas adjacentes para espaçamento equilibrado

### Estados Visuais
```css
/* Nó Recolhido */
.flowchart-node.has-subtopics:not(.expanded)::after {
    content: '';
    width: 20px;
    height: 3px;
    background: var(--accent-color);
    opacity: 0.6;
}

/* Nó Expandido */
.flowchart-node.expanded .flowchart-expand-icon {
    transform: translateY(-50%) rotate(90deg);
}

/* Nó Completo */
.flowchart-node.completed {
    border-color: #4ade80;
    background: linear-gradient(135deg, 
        rgba(74, 222, 128, 0.1), 
        rgba(34, 197, 94, 0.1)
    );
}

.flowchart-node.completed::after {
    content: '✓';
    color: #4ade80;
    font-size: 1.2rem;
}
```

### Animações
```css
/* Entrada de Nós */
@keyframes flowchartNodeFadeIn {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(-10px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

/* Conexões SVG */
@keyframes flowchartPathDraw {
    from {
        stroke-dashoffset: 1000;
        opacity: 0;
    }
    to {
        stroke-dashoffset: 0;
        opacity: 0.6;
    }
}
```

### Responsividade
```css
/* Telas Médias (< 1400px) */
@media (max-width: 1400px) {
    --node-central-width: 260px;
    --subtopic-width: 200px;
    font-size: 0.9rem;
}

/* Mobile (< 768px) */
@media (max-width: 768px) {
    --container-padding-top: 60px;
    --subtopic-horizontal-gap: 200px;
    font-size: 0.85rem;
}
```

### Indicadores de Dificuldade
```css
.flowchart-node.difficulty-easy {
    border-left: 4px solid #4ade80;
}

.flowchart-node.difficulty-medium {
    border-left: 4px solid #fbbf24;
}

.flowchart-node.difficulty-hard {
    border-left: 4px solid #f87171;
}
```

### Conexões SVG
- **Principais**: Stroke 2px, cor accent, linha sólida
- **Secundárias**: Stroke 1.5px, cor glass-border, linha tracejada (5,5)
- **Curvas**: Bezier quadrática para suavidade
- **Animação**: 1s ease-out com stroke-dasharray

### Checklist de Implementação
- [ ] Verificar que todos os elementos respeitam `minTopMargin`
- [ ] Validar espaçamento uniforme entre containers
- [ ] Testar expansão/recolhimento em diferentes níveis
- [ ] Confirmar que não há sobreposição de elementos
- [ ] Verificar transições suaves (< 0.5s)
- [ ] Testar em diferentes resoluções (1920px, 1366px, 768px)
- [ ] Validar contraste de cores (WCAG AA mínimo)
- [ ] Confirmar que scroll-behavior: smooth está ativo

### Lições Aprendidas
1. **Espaçamento fixo não escala**: Usar cálculo dinâmico baseado em conteúdo
2. **Centralização pode causar corte**: Sempre verificar margem mínima
3. **Sincronizar cálculos**: Fase 1 e Fase 2 devem usar mesmos valores
4. **Posicionamento sequencial**: Previne sobreposição melhor que centralizado
5. **Média de alturas**: Cria transições suaves entre nós expandidos/recolhidos