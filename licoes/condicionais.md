## 📋 Metadados
- **Título:** Estruturas Condicionais (if/else, switch)
- **Fonte:** Antigravity Learning Path
- **Data:** 08/05/2026
- **Tags:** #logica #condicionais #if-else #fluxo

## 🎯 Resumo Executivo
Estruturas condicionais permitem que o programa tome caminhos diferentes baseados em condições lógicas. É o coração da inteligência de um software, permitindo que ele responda a diferentes entradas.

## 📚 Conteúdo Detalhado

### 1. O Bloco if...elif...else
- **Mecanismo:** O Python avalia a expressão; se for `True`, executa o bloco indentado.
- **Exemplo:**
  ```python
  idade = 18
  if idade >= 18:
      print("Maior de idade")
  elif idade > 12:
      print("Adolescente")
  else:
      print("Criança")
  ```

### 2. Match Case (O "Switch" do Python)
- **Definição:** Introduzido no Python 3.10, permite comparar um valor contra vários padrões de forma limpa.
- **Exemplo:**
  ```python
  status = 404
  match status:
      case 200: print("Sucesso")
      case 404: print("Não encontrado")
      case _: print("Erro desconhecido")
  ```

## 💡 Insights e Conexões
- **Por que importa:** Sem condicionais, programas seriam lineares e incapazes de lidar com imprevistos ou escolhas do usuário.
- **Conexões:** Depende totalmente dos **Operadores Relacionais**.
- **Limitações:** Evite "Nesting" excessivo (ifs dentro de ifs), pois torna o código difícil de ler (prefira "Early Return").

## ✅ Checklist de Revisão
- [ ] Entendo o propósito do `elif`?
- [ ] Sei usar o `match case` para múltiplas opções?
- [ ] Lembro que a indentação é obrigatória em Python para definir o bloco?
- [ ] Sei usar o operador ternário (`valor if condicao else outro`)?
