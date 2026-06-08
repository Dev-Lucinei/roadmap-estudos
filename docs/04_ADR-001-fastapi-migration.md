# ADR-001: Migração de http.server para FastAPI

**Status**: Aceito
**Data**: 2026-05-11 (documentado em 2026-06-08)
**Decidido por**: Desenvolvedor pessoal

---

## Contexto

O projeto Roadmap-Estudos utilizava `http.server` do Python (módulo padrão) como servidor web para servir o frontend e expor endpoints de API. Essa abordagem apresentava limitações significativas:

1. **Servidor síncrono**: Cada requisição bloqueava o thread; chamadas à API de IA (OpenRouter) eram um gargalo para requisições simultâneas.
2. **Sem validação automática**: Bodies de requisição precisavam ser parseados manualmente, sem validação de schema.
3. **Sem documentação de API**: Não havia Swagger/OpenAPI gerado automaticamente.
4. **CORS manual**: Headers CORS precisavam ser adicionados em cada resposta.
5. **Tratamento de erros繁琐**: Cada endpoint exigia try-except manual com construção de response.

## Decisão

Migrar de `http.server` (`SimpleHTTPRequestHandler`) para **FastAPI** com `uvicorn` como servidor ASGI.

### Justificativas

| Critério | http.server | FastAPI |
|----------|-------------|---------|
| Async | Não (síncrono) | Sim (`async def`) |
| Validação | Manual | Automática (Pydantic v2) |
| Documentação | Nenhuma | Swagger UI em `/docs` |
| CORS | Manual (headers) | Middleware integrado |
| Performance | Bloqueante | Não bloqueante |
| Tipagem | Nenhuma | Type hints + Pydantic |

### Alternativas Consideradas

1. **Flask**: Mais leve, mas síncrono por padrão; exigiria `async` com `asgiref`.
2. **Starlette**: Base do FastAPI, mas menos features out-of-the-box.
3. **Manter http.server**: Rejeitado devido às limitações de performance e validação.

## Consequências

### Positivas
- **Performance**: Endpoints de IA não bloqueiam mais o servidor inteiro.
- **Validação automática**: Pydantic retorna 422 para inputs inválidos sem código manual.
- **Swagger UI**: Documentação interativa disponível em `http://localhost:8000/docs`.
- **Manutenção**: Código mais limpo e organizado (separation of concerns).

### Negativas
- **Dependência adicional**: `fastapi`, `uvicorn`, `pydantic` no `pyproject.toml`.
- **Curva de aprendizado**: Funcionalidade `lifespan`取代了 `startup_event` deprecated.
- **Complexidade**: Mais abstrações para aprender (APIRouter, Depends, etc.).

### Riscos Mitigados
- **Risco de regressão**: Testes automatizados (`tests/integration/test_api.py`) validam endpoints.
- **Risco de configuração**: `uvicorn` configuração simples via `backend/main.py`.

## Referências
- PRD: US-004 (pydantic-settings)
- CHANGELOG: v3.0.0 (migração para FastAPI)
- ADR-002 (integração OpenRouter)
