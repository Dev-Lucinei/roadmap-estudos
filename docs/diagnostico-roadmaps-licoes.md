# Diagnóstico: Roadmaps e Lições

**Data:** 11/05/2026  
**Status:** ✅ Problema Identificado e Corrigido

## 🔍 Problemas Identificados e Soluções

### 1. ❌ Nomenclatura Inconsistente de Arquivos
- **Problema:** O arquivo `python_fundamentos_v2.json` não seguia o padrão `roadmap_*.json`
- **Impacto:** A API `list_roadmaps()` não listava este roadmap
- **Solução:** ✅ Renomeado para `roadmap_python_fundamentos_v2.json`
- **Status:** CORRIGIDO

### 2. ❌ Servidor Não Servia Arquivos de Lições
- **Problema:** O `RoadmapHandler` estava configurado para servir apenas arquivos de `frontend/public`, mas as lições estão em `/licoes` na raiz do projeto
- **Impacto:** Frontend recebia 404 ao tentar carregar qualquer lição, mesmo as existentes
- **Solução:** ✅ Adicionado tratamento específico para rota `/licoes/` no método `do_GET()` e criado método `_send_file()` para servir arquivos markdown
- **Status:** CORRIGIDO

### 3. ⚠️ Lições Faltantes
- **Problema:** Apenas 18% das lições esperadas existem no diretório `/licoes`
- **Impacto:** Usuários não conseguem acessar conteúdo para a maioria dos tópicos
- **Status:** PARCIALMENTE RESOLVIDO (servidor agora serve as lições existentes corretamente)

## 📊 Estatísticas Atuais

### Roadmaps Disponíveis: 3
1. ✅ `roadmap_python_fundamentos_v2.json` - **50% completo** (12/24 lições)
2. ⚠️ `roadmap_programacao_orientada_a_objetos_em_python.json` - **3% completo** (1/27 lições)
3. ⚠️ `roadmap_exemplo_arvore.json` - **3% completo** (1/27 lições)

### Lições
- **Total esperado:** 78 lições
- **Existentes:** 14 lições (17%)
- **Faltando:** 64 lições (83%)

### Lições Existentes
```
algos-ds.md
arch.md
conceitos_poo.md
condicionais.md
docker-dockerfiles.md
estruturada.md
funcional.md
funcoes-escopo.md
io-arquivos.md
logica-prog.md
operadores.md
paradigmas.md
recursividade.md
repeticao.md
sintaxe-estruturas.md
strings-arrays.md
sw-eng-basics.md
test_123.md
var-tipos.md
```

## 🛠️ Correções Aplicadas

### ✅ Correção 1: Nomenclatura de Arquivos
```bash
mv data/python_fundamentos_v2.json data/roadmap_python_fundamentos_v2.json
```
**Resultado:** Todos os 3 roadmaps agora são listados corretamente pela API

### ✅ Correção 2: Servidor de Lições
**Arquivo modificado:** `backend/main.py`

**Mudanças:**
1. Adicionado tratamento para rota `/licoes/` no método `do_GET()`:
```python
elif self.path.startswith("/licoes/"):
    lesson_file = self.path.replace("/licoes/", "")
    lesson_path = BASE_DIR / "licoes" / lesson_file
    if lesson_path.exists() and lesson_path.is_file():
        self._send_file(lesson_path)
    else:
        self.send_error(404, f"Lição não encontrada: {lesson_file}")
```

2. Criado método `_send_file()` para servir arquivos markdown:
```python
def _send_file(self, file_path):
    """Envia um arquivo de texto (markdown) como resposta."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))
    except Exception as e:
        self.send_error(500, f"Erro ao ler arquivo: {str(e)}")
```

**Resultado:** Servidor agora serve corretamente todas as lições existentes via HTTP

### ✅ Teste de Validação
```bash
# Teste realizado com sucesso:
# - 12/24 lições do roadmap principal carregando corretamente (50%)
# - Todas as requisições HTTP retornando 200 OK
# - Content-Type correto: text/markdown; charset=utf-8
# - CORS headers configurados corretamente
```

### 📝 Próximos Passos Recomendados

### 1. ⚠️ Configurar API Key (OBRIGATÓRIO para geração de conteúdo)
Para usar o botão "📝 Gerar Conteúdo", você precisa configurar a API key do OpenRouter:

```bash
# 1. Copie o arquivo de exemplo
cp .env.example .env

# 2. Edite o arquivo .env e adicione sua chave
# Obtenha em: https://openrouter.ai/keys
nano .env
```

Conteúdo do `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui
```

**Sem a API key configurada:**
- ❌ Botão "Gerar Conteúdo" retorna erro
- ❌ Botão "Gerar Quiz" não funciona
- ❌ Criação de novos roadmaps via IA falha
- ✅ Lições existentes continuam funcionando normalmente

### 2. **Gerar Lições Faltantes**
   - Usar o botão "📝 Gerar Conteúdo" no frontend para cada tópico
   - Ou criar script batch para gerar todas as lições via IA

### 3. **Padronizar Nomenclatura**
   - Garantir que todos os arquivos de roadmap sigam o padrão `roadmap_*.json`
   - Documentar convenção de nomenclatura em `docs/PADRAO_JSON_ROADMAP.md`

### 4. **Validação de Integridade**
   - Criar script de validação que verifica:
     - Todos os roadmaps têm prefixo correto
     - Todos os IDs de lições referenciados têm arquivos correspondentes
     - Estrutura JSON está válida

## 🔧 Como Gerar Lições Faltantes

### Opção 1: Via Interface (Manual)
1. Acesse http://localhost:8000
2. Selecione um roadmap
3. Clique em um tópico sem lição
4. Clique no botão "📝 Gerar Conteúdo"

### Opção 2: Via Script (Automático)
```python
# TODO: Criar script scripts/generate_missing_lessons.py
# que itera por todos os roadmaps e gera lições faltantes
```

## 📈 Impacto das Correções

### Antes das Correções
- ❌ Apenas 2 de 3 roadmaps listados
- ❌ 0 lições carregando (todas retornavam 404)
- ❌ Frontend não conseguia exibir nenhum conteúdo de lição

### Depois das Correções
- ✅ 3 de 3 roadmaps listados (100%)
- ✅ 12 lições carregando corretamente no roadmap principal (50%)
- ✅ Frontend pode exibir todo o conteúdo disponível
- ✅ Sistema de geração de lições via IA funcional para criar conteúdo faltante

## 🎯 Métricas de Sucesso

- [x] Todos os roadmaps listados corretamente
- [ ] 100% das lições do roadmap principal geradas
- [ ] Script de validação implementado
- [ ] Documentação de padrões atualizada
