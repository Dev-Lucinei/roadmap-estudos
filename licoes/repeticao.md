## 📋 Metadados
- **Título:** Estruturas de Repetição (for, while, do-while)
- **Fonte:** Antigravity Learning Path
- **Data:** 08/05/2026
- **Tags:** #logica #loops #for #while #repeticao

## 🎯 Resumo Executivo
Estruturas de repetição (ou loops) permitem executar um bloco de código múltiplas vezes. Isso é essencial para processar listas de dados, realizar automações ou manter um programa rodando até uma ação de parada.

## 📚 Conteúdo Detalhado

### 1. Loop `for`
- **Conceito Chave:** Usado para iterar sobre uma sequência (lista, string, range).
- **Exemplo:**
  ```python
  for i in range(5):
      print(f"Repetição {i}")
  ```

### 2. Loop `while`
- **Mecanismo:** Executa enquanto uma condição for verdadeira.
- **Exemplo:**
  ```python
  contador = 0
  while contador < 5:
      print(contador)
      contador += 1
  ```

### 3. Controle de Fluxo
- `break`: Interrompe o loop imediatamente.
- `continue`: Pula para a próxima iteração do loop.

## 💡 Insights e Conexões
- **Por que importa:** Automatização é, em grande parte, o uso inteligente de loops para processar grandes volumes de tarefas repetitivas.
- **Conexões:** Fundamental para manipular **Listas e Dicionários** (Sintaxe Python).
- **Limitações:** Cuidado com "Loops Infinitos" no `while` (sempre garanta que a condição mude).

## ✅ Checklist de Revisão
- [ ] Sei quando usar `for` em vez de `while`?
- [ ] Entendo como usar a função `range()`?
- [ ] Sei para que serve o `break`?
- [ ] Consigo iterar sobre uma string usando `for`?
