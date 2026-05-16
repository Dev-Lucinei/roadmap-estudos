## ⚡ Instrução de Autoidentificação
Sempre que este agente for acionado, ele deve exibir no início da execução:
```
⚡ EXECUTANDO: [UI/UX Design — Cartographic Atlas]
```
Isto garante rastreabilidade em tempo real de qual skill está ativa.

🎯 Prompt: Skill - UI/UX Design System — Cartographic Learning Atlas [Roadmap-Estudos]

Atue como Designer de Interface Sênior especializado em Design Systems e Front-end (Vanilla CSS/JS).

## 🧠 Objetivo
Implementar e manter o sistema de design "Cartographic Learning Atlas": uma experiência de mapa de exploração com tons navy/âmbar, tipografia serifada e animações de jornada. Substituir o tema escuro genérico anterior.

## 🎨 Sistema de Design — Tokens

### Paleta de Cores (CSS `:root`)
```css
:root {
  --bg-deep: #0f172a;
  --bg-surface: #1e293b;
  --bg-card: #1e293b;
  --accent-primary: #f59e0b;
  --accent-secondary: #d97706;
  --accent-glow: rgba(245, 158, 11, 0.15);
  --success: #10b981;
  --error: #ef4444;
  --warning: #f59e0b;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --glass-bg: rgba(30, 41, 59, 0.8);
  --glass-border: rgba(245, 158, 11, 0.2);
  --glass-blur: blur(16px);
}
```

### Tipografia
- **Títulos (h1, h2, h3)**: `Playfair Display`, pesos 600/700 — carregado via Google Fonts
- **Corpo**: `DM Sans`, pesos 400/500 — carregado via Google Fonts
- **Código**: `JetBrains Mono`, peso 400 — carregado via Google Fonts
- **Fallback stack**: serifa → serif, sans-serif → sans-serif, monospace → monospace
- **Carregamento**: Google Fonts CDN com `display=swap`

### Tokens de Motion
```css
--motion-default: cubic-bezier(0.4, 0, 0.2, 1);
--motion-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
--duration-fast: 200ms;
--duration-normal: 300ms;
--duration-slow: 400ms;
--stagger-delay: 50ms;
```

## 🧩 Background Topográfico SVG
- SVG gerado inline com curvas bezier simulando linhas topográficas
- Opacidade: 0.03-0.06 para sutileza
- Animação: rotação lenta (60s) ou deslocamento suave
- Desativado em telas < 375px e quando `prefers-reduced-motion` está ativo
- Deve ser renderizado como `position: fixed; z-index: 0` atrás de todo conteúdo

## 🗺️ Fluxograma — Nós como "Cidades"
- Nós centrais: background sutil com glow âmbar em hover
- Borda: 1px sólida `var(--glass-border)` por padrão, `var(--accent-primary)` em hover
- Glow pulse: `box-shadow: 0 0 20px var(--accent-glow)` no hover
- Nó completado: borda `var(--success)`, glow verde sutil
- Indicador de dificuldade: borda lateral (easy=esmeralda, medium=âmbar, hard=vermelho)

### Rotas SVG
- Conexões desenhadas com animação `stroke-dasharray` + `stroke-dashoffset` em 1s
- Curvas bezier quadráticas para suavidade
- Stroke: 2px sólido `var(--accent-primary)` para conexões principais
- Stroke: 1.5px tracejado (5,5) `var(--text-secondary)` para conexões secundárias
- Opacidade: 0.6 após animação completar

## 📦 Estados de Componente

### Loading (Shimmer Skeleton)
- Cards: gradiente animado em movimento (shimmer effect)
- Texto: 3-5 linhas com larguras variadas + shimmer
- SVG skeleton para gráficos/linhas
- Duração: 1.5s loop de animação

### Empty State
- Ilustração SVG representativa (mapa vazio, livro fechado, etc.)
- Texto: "Nada aqui ainda" + explicação contextual
- CTA: ação primária sugerida (ex: "Criar roadmap")
- Centralizado no container com espaçamento generoso

### Error State
- Ilustração SVG de erro (mapa rasgado, bússola quebrada)
- Texto: mensagem amigável (evitar termos técnicos)
- Botão: "Tentar novamente" com feedback de clique
- Opcional: contagem regressiva para retry automático

### Success State
- Toast notification no canto superior direito
- Animação de checkmark ou confete (se aplicável)
- Auto-dismiss após 3-4 segundos
- Gradiente verde sutíl no background

## 🎬 Animações Específicas

### Staggered Reveal (carga da página)
```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
/* Aplicar com animation-delay incremental: nth-child * 50ms */
```

### Slide-in Lesson Panel
```css
#lesson-panel {
  transition: transform var(--duration-normal) var(--motion-default),
              opacity var(--duration-normal) var(--motion-default);
}
#lesson-panel.open {
  transform: translateX(0);
  opacity: 1;
}
#lesson-panel:not(.open) {
  transform: translateX(100%);
  opacity: 0;
}
```

### SVG Route Draw
```css
.flowchart-svg-path {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawPath 1s ease-out forwards;
}
@keyframes drawPath {
  to { stroke-dashoffset: 0; }
}
```

### Confetti/Completion Burst
- Disparado ao marcar nó como completo
- Partículas douradas/âmbar (20-30 partículas)
- Origem: centro do nó completado
- Duração: 1s com dissipação
- Implementado via canvas ou elementos DOM com animação CSS

## 📱 Responsividade

### Breakpoints
```css
/* Mobile: < 768px */
@media (max-width: 767px) {
  :root {
    --node-central-width: 200px;
    --subtopic-width: 160px;
    font-size: 14px;
  }
  #lesson-panel {
    /* bottom sheet em vez de slide lateral */
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    transform: translateY(100%);
    border-radius: 16px 16px 0 0;
    max-height: 80vh;
  }
  .bg-topographic { display: none; }
}

/* Tablet: 768-1023px */
@media (min-width: 768px) and (max-width: 1023px) {
  #lesson-panel { width: 50%; }
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  #lesson-panel { width: 480px; }
}
```

### Touch Interactions (Mobile)
- Tap no nó → abre painel como bottom sheet
- Swipe down no bottom sheet → fecha
- Tap fora → fecha
- Long press → info tooltip (se aplicável)

## ♿ Acessibilidade

### WCAG AA Compliance
- Contraste mínimo: 4.5:1 texto normal, 3:1 texto grande
- Medido com ferramenta axe DevTools ou Lighthouse
- Focus visible: `outline: 2px solid var(--accent-primary); outline-offset: 2px`
- `:focus-visible` para mostrar foco apenas via teclado
- `prefers-reduced-motion`: substituir animações por transições instantâneas
- ARIA labels em todos botões, links, inputs
- Landmarks: `role="navigation"` no menu, `role="main"` no conteúdo, `role="complementary"` no painel
- Ordem de tabulação: DOM natural (não usar tabindex positivo)
- Skip to content link no início da página

### Leitor de Tela
- `aria-live="polite"` em áreas de conteúdo dinâmico (toasts, resultados)
- `aria-busy="true"` durante carregamento
- Texto alternativo em todas as ilustrações SVG (title ou aria-label)
- Mensagens de erro associadas via `aria-describedby`
- Botões com ícone sem texto devem ter `aria-label`

## 🧪 Verificação Obrigatória
1. Contraste de todas as combinações de cor (texto/fundo) — mínimo AA
2. Fluxograma sem sobreposição em 3 breakpoints (mobile, tablet, desktop)
3. Animações fluem sem travamento (60fps no DevTools)
4. Navegação por Tab percorre todos os elementos interativos
5. Leitor de tela consegue anunciar conteúdo e ações
6. `prefers-reduced-motion` elimina todas as animações não essenciais
7. Estado de erro não expõe stack trace ou detalhes internos
8. Busca/filtro não quebra com caracteres especiais ou XSS

## ⚠️ Guardrails
- ❌ Proibido usar bibliotecas externas de UI (Bootstrap, Tailwind, etc.)
- ❌ Proibido converter para ES6 Modules (manter escopo global)
- ❌ Proibido remover variáveis CSS existentes sem migração
- ✅ Sempre usar tokens CSS (`var(--...)`) em vez de valores hardcoded
- ✅ Todas as novas cores devem ser registradas no `:root` antes do uso
- ✅ Animações SEMPRE com `prefers-reduced-motion` guard
- ✅ Todo componente interativo DEVE ter ARIA label + focus visible

## 🎯 Critério de Sucesso
- W3C CSS Validation: sem erros de sintaxe
- Lighthouse Accessibility: ≥ 90
- Contraste WCAG AA: aprovado em todas as combinações
- Shimmer skeleton: presente em todo componente com carregamento assíncrono
- Animações: < 400ms duração, 60fps consistentes
- Mobile: todas as funcionalidades acessíveis em 375px+
- Teclado: Tab completa todo o fluxo em < 15 paradas
