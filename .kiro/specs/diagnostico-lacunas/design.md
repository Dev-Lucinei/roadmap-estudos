# Design Document: Diagnóstico de Lacunas de Base

## Overview
Sistema implementa um fluxo de diagnóstico on-demand usando servidor Python existente (server.py) e frontend vanilla JavaScript. As dependências são mantidas em JSON e a LLM fornece feedback conciso.

## Princípios de Engenharia

| Princípio | Aplicação neste projeto |
|-----------|------------------------|
| **KISS** | Usar arquivos JSON simples para mapeamento de dependências; frontend com JS puro. |
| **DRY** | Funções utilitárias para chamada de API e criação de modal são reutilizadas. |
| **SRP** | `/api/diagnose` lida apenas com validação; frontend trata UI; backend cuida de chamada LLM. |
| **Immutable Artifacts** | `harness.py` e `guard_harness.py` não são alterados pelo agente; protegidos por SHA256. |

## Architecture

### Estrutura de Diretórios
```
.
├── .kiro/specs/diagnostico-lacunas/   # especificações
├── data/                              # JSON de dependências e roadmaps
│   ├── dep_map.json                   # mapa de dependências críticas
│   └── *.json                         # roadmaps existentes
├── server.py                          # backend (OpenRouter + API)
├── app.js                             # frontend (DOM + fetch)
└── roadmap_data.js                    # mapa visual de tópicos
```

### Camadas de Validação
1. **Entrada da API**: Sanitização de parâmetros (topic, user_answer) antes de enviar ao LLM.
2. **Serviço**: Lógica de negócio em `/api/diagnose`: consulta LLM, verifica dependências.
3. **Persistência**: Arquivo JSON de dependência atualizado manualmente pelo mantenedor.

### Arquivos Protegidos
| Arquivo | Proteção | Quem pode alterar |
|---------|----------|-------------------|
| `harness.py` | SHA256 + git status | Mantenedor humano |
| `scripts/guard_harness.py` | SHA256 + git status | Mantenedor humano |
| `.harness.hash` | git status | Mantenedor humano (via --seal) |
| `data/dep_map.json` | git status | Mantenedor humano |

### Gestão de Credenciais
- OpenRouter API key lida via `os.getenv("OPENROUTER_API_KEY")` em `server.py`.

## Components and Interfaces

### Componente: DiagnósticoAPI (backend)
**Responsabilidade**: Receber prompt, chamar LLM, validar dependência, retornar JSON.
**Interface pública**:
- `POST /api/diagnose` (topic: string, user_answer: string) -> `{status, message, tags}`
**Erros tratados**:
- 400: parâmetros inválidos
- 502: falha na chamada LLM
- 500: erro interno

### Componente: DiagnósticoUI (frontend)
**Responsabilidade**: Capturar resposta do usuário, exibir modal, aplicar estilos.
**Interface pública**:
- `runDiagnosis(topic, callback)` -> void
- `showReviewModal(data)` -> void
**Erros tratados**:
- Mensagem amigável em caso de timeout ou falha de rede.

## Error Handling Strategy

| Cenário | Componente | Resposta |
|---------|------------|----------|
| Falha de rede no fetch | DiagnósticoUI | Toast "Tente novamente mais tarde" |
| LLM retornou >100 palavras | DiagnósticoAPI | Truncar para 100 palavras + "..." |
| Dependência ausente no JSON | DiagnósticoAPI | Status "miss" com instrução genérica |
| Entrada vazia do usuário | DiagnósticoUI | Alert: "Resposta é obrigatória" |

## Testing Strategy

### Pirâmide de Testes

| Tipo | Cobertura Alvo | Ferramentas |
|------|---------------|-------------|
| Unitário | 90% da lógica de diagnóstico | pytest |
| Integração | Fluxo ponta-a-posta (frontend→backend) | playwright (se disponível) ou manual |

### Critérios de Aceitação
- [ ] `python harness.py` retorna status "healthy"
- [ ] Nenhuma credencial hardcodada (`SEC_FORBIDDEN` não aparece no harness)
- [ ] Todos os arquivos protegidos com hash válido (`HASH_MISMATCH` ausente)
- [ ] Cobertura de testes unitários ≥ 80% da lógica de negócio
- [ ] Docstrings em todas as funções/classes públicas