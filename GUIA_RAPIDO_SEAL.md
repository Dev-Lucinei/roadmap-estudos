# 🔒 Guia Rápido - Sistema de Proteção

## ✅ Uso Normal (Você Modificando Arquivos)

```bash
# 1. Desbloqueie (será pedida sua senha)
python scripts/guard_harness.py --unlock

# 2. Edite o que precisar
vim harness.py

# 3. Sele as alterações (será pedida sua senha - isso aprova as mudanças)
python scripts/guard_harness.py --seal

# 4. Commit normalmente (será permitido pois arquivos estão selados)
git add harness.py
git commit -m "fix: correção"
```

## 📊 Verificar Status

```bash
# Ver quais arquivos estão selados/desbloqueados
python scripts/guard_harness.py --status

# Verificar integridade completa
python scripts/guard_harness.py
```

## 🤖 Proteção Contra Agentes

**Arquivos selados** (`chattr +i`):
- ❌ Agentes **não conseguem** modificar
- ❌ Agentes **não conseguem** deletar  
- ❌ Agentes **não conseguem** renomear
- ✅ Apenas **você com sua senha** pode desbloquear
- ✅ **Commit permitido** (selo = aprovação com senha)

**Arquivos desbloqueados**:
- ⚠️ Podem ser modificados por agentes
- ❌ **Commit bloqueado** pelo hook (proteção contra modificação não autorizada)

## 🎯 Arquivos Protegidos

- `harness.py` - Sistema de validação
- `scripts/guard_harness.py` - Guard de integridade
- `.harness.hash` - Hashes de verificação

## 🔧 Comandos Disponíveis

```bash
# Verificar integridade
python scripts/guard_harness.py

# Verificar status de bloqueio
python scripts/guard_harness.py --status

# Desbloquear para edição (requer senha)
python scripts/guard_harness.py --unlock

# Selar após modificações (requer senha)
python scripts/guard_harness.py --seal

# Saída JSON para automação
python scripts/guard_harness.py --json
```

## ⚡ Workflow Completo

```bash
# Desbloquear → Editar → Selar (aprovar) → Commit
python scripts/guard_harness.py --unlock && \
vim harness.py && \
python scripts/guard_harness.py --seal && \
git add harness.py && \
git commit -m "fix: correção"
```

## 🔐 Como Funciona

O sistema usa **imutabilidade no nível do kernel Linux** (`chattr +i`):
- Impede qualquer modificação, mesmo para o dono do arquivo
- Requer `sudo` (sua senha) para desbloquear/selar
- **Selar = Aprovar**: Quando você sela com `--seal`, está aprovando as mudanças com sua senha
- **Hook valida selo**: Commit só é permitido se arquivos modificados estiverem selados
- Não pode ser contornado por agentes IA (requer senha interativa)

## ⚠️ Importante

- Sempre verifique o status antes de editar: `--status`
- **Sele ANTES de commitar**: `--seal` (isso aprova suas mudanças)
- Nunca compartilhe sua senha com agentes
- O hook valida que arquivos modificados estejam selados (aprovados)
