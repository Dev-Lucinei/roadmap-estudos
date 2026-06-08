# ADR-002: Integração com OpenRouter para IA

**Status**: Aceito
**Data**: 2026-05-11 (documentado em 2026-06-08)
**Decidido por**: Desenvolvedor pessoal

---

## Contexto

O projeto Roadmap-Estudos necessita de **Inteligência Artificial** para:
1. Gerar lições estruturadas em Markdown a partir de tópicos de roadmap.
2. Criar quizzes educacionais de múltipla escolha.
3. Avaliar respostas de usuários com feedback detalhado.
4. Diagnosticar gaps de conhecimento cruzando respostas com mapa de dependências.

A questão central era: **qual provedor de IA usar?** e **como integrar de forma flexível?**

### Opções Avaliadas

| Provedor | Custo | Flexibilidade | Setup |
|----------|-------|---------------|-------|
| OpenAI direto | Pago por token | 1 modelo | API key simples |
| OpenRouter | Pago por token (multi-modelo) | N+ modelos | API key compatível com OpenAI |
| Ollama (local) | Gratuito | Limitado | Requer GPU potente |
| Azure OpenAI | Pago (enterprise) | 1 modelo | Conta enterprise |

## Decisão

Utilizar **OpenRouter** como provedor de IA, acessado via SDK `openai` (compatibilidade de API).

### Justificativas

1. **Multi-modelo**: OpenRouter roteia automaticamente entre modelos (GPT-4, Claude, Llama, etc.) via `openrouter/auto`.
2. **Custo-benefício**: Preços competitivos com roteamento inteligente para modelos mais baratos.
3. **Compatibilidade**: Usa SDK `openai` padrão — migração mínima de código.
4. **Flexibilidade**: Pode trocar modelo via prompt sem mudar código.
5. **Simplicidade**: Uma API key funciona para todos os modelos.

### Configuração Técnica

```python
# backend/core/config.py
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Uso em services
client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

completion = client.chat.completions.create(
    model="openrouter/auto",  # Roteamento automático
    messages=[...],
    max_tokens=800,
    temperature=0.7,
)
```

### Padrão de Segurança
- **API key**: Armazenada em `.env`, nunca em código.
- **Validação**: `check_api_key()` verifica presença antes de cada chamada.
- **Lazy evaluation**: `get_api_key()` lê `os.getenv()` em tempo de execução (não cacheia).

## Consequências

### Positivas
- **Flexibilidade**: Pode trocar modelo (GPT-4 → Claude → Llama) sem mudar código.
- **Custo controlável**: `max_tokens` e `temperature` ajustados por endpoint.
- **Padrão da indústria**: SDK `openai` é amplamente suportado e documentado.
- **Escalabilidade**: Fácil adicionar novos endpoints que usam IA.

### Negativas
- **Dependência externa**: Se OpenRouter cair, funcionalidades de IA ficam indisponíveis.
- **Custo variável**: Preços mudam entre modelos; pode surpreender.
- **Latência**: Chamadas à API externa adicionam latência (mitigada por async).
- **Qualidade variável**: `openrouter/auto` pode rotear para modelos de qualidade inferior.

### Riscos Mitigados
- **Risco de custo**: `max_tokens` limitado por endpoint (150-2000 tokens).
- **Risco de qualidade**: Prompts restritivos com formato de resposta JSON estrito.
- **Risco de disponibilidade**: Fallback para erro amigável quando API falha.

## Referências
- PRD: US-004 (pydantic-settings para configuração)
- CHANGELOG: v2.9.0 (sistema de quiz), v3.0.0 (migração FastAPI)
- ADR-001 (migração FastAPI — contexto de async)
