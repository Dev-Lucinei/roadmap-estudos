# AGENTS.md

Este documento é a **fonte da verdade** para qualquer agente que colabore neste projeto. Leia-o integralmente antes de iniciar qualquer alteração.

## 🛠️ Stack Técnica & Arquitetura
- **Backend**: Python 3.11+ (Servidor Bridge via `server.py`)
- **Frontend**: HTML5, Vanilla CSS, JavaScript (ES6+ porém utilizando **escopo global** para compatibilidade com `http.server`)
- **IA**: Integração via OpenRouter API
- **Persistência**: Arquivos JSON em `/data` e Markdown em `/licoes`

## 🔄 Workflow de Orquestração
Sempre que detectar uma nova funcionalidade, alteração estrutural ou bug, acione o protocolo de orquestração para garantir a sincronia entre Dados, IA e Interface:
👉 **[@skills/workflown-agents.md](./skills/workflown-agents.md)**

## 🐍 Boas Práticas Python
- **Tipagem**: Use *type hints* em todas as funções para facilitar a manutenção.
- **Caminhos**: Utilize `os.path.join` e `BASE_DIR` para garantir portabilidade entre SOs.
- **Tratamento de Erros**: Implemente blocos `try-except` específicos em endpoints da API para evitar que o servidor caia.
- **Performance**: Para operações de arquivo, prefira `with open(...)` para garantir o fechamento dos descritores.

## 📝 Fluxo de Evolução & Commits
Siga rigorosamente a sequência: **Modificação -> Registro no Changelog -> Commit**.

### 1. Alimentação do CHANGELOG.md
Antes de cada commit, registre a evolução no `CHANGELOG.md`:
- **Versão**: Seguindo SemVer (ex: `[v2.2.0]`).
- **Data**: Data da alteração.
- **Seções**: `### Adicionado`, `### Corrigido` ou `### Alterado`.
- **Memória Técnica**: Documente problemas enfrentados e a solução aplicada para mitigar erros futuros (evitar regressões).

### 2. Conventional Commits (PT-BR)
As mensagens devem ser detalhadas e seguir o formato: `[tipo]([escopo]): [descrição detalhada]`

**Tipos permitidos:**
- `feat`: Nova funcionalidade.
- `fix`: Correção de bug.
- `docs`: Alterações em documentação.
- `style`: Formatação, faltando ponto e vírgula, etc (não altera lógica).
- `refactor`: Refatoração de código que não corrige bug nem adiciona feature.
- `perf`: Melhoria de performance.
- `chore`: Atualizações de build, dependências, etc.

**Exemplo:** `feat(api): implementa endpoint de salvamento de roadmap com validação de JSON`

## ⚠️ Notas de Atenção (Não Ignore)
- **Escopo JS**: Não converta o frontend para ES6 Modules (`import/export`) a menos que a infraestrutura de servidor mude, para evitar erros de CORS/MIME.
- **Parser de Quiz**: O quiz é extraído via Regex de blocos ` ```json ` no final dos arquivos `.md`. Alterar esse formato quebrará o frontend.
- **Porta 8000**: Se encontrar `Address already in use`, use `fuser -k 8000/tcp` ou verifique a flag `allow_reuse_address` no `server.py`.

## 🚦 Verificação de Ambiente
- Servidor local: `http://localhost:8000`
- Teste rápido de API: `curl http://localhost:8000/api/roadmaps`
