# Programação Funcional (Conceitos Básicos)

## 🎯 Resumo Executivo
A Programação Funcional (PF) é um paradigma que trata a computação como a avaliação de funções matemáticas, evitando estados mutáveis e dados variáveis. Sua importância reside na criação de código mais previsível, fácil de testar e livre de efeitos colaterais indesejados.

## 📚 Conceitos-Chave

1.  **Funções Puras:** Uma função é pura se, para os mesmos argumentos, ela sempre retorna o mesmo resultado e não causa efeitos colaterais (como alterar uma variável global ou escrever no disco).
    *   *Exemplo:* `f(x) = x + 2` é pura. `f(x) = x + valor_externo` não é.
2.  **Imutabilidade:** Uma vez que um dado é criado, ele não pode ser alterado. Em vez de modificar um objeto, cria-se uma nova instância com as alterações necessárias.
    *   *Exemplo:* Em vez de `lista.push(item)`, utiliza-se `novaLista = [...lista, item]`.
3.  **Funções de Primeira Classe e Alta Ordem:** Funções são tratadas como variáveis. Elas podem ser passadas como argumentos para outras funções ou retornadas por elas.
    *   *Exemplo:* A função `map` recebe uma função como parâmetro para transformar elementos de uma lista.
4.  **Transparência Referencial:** Você pode substituir uma chamada de função pelo seu valor resultante sem alterar o comportamento do programa. Isso facilita o raciocínio lógico sobre o código.

## 💡 Aplicação Prática

No desenvolvimento moderno, a Programação Funcional é amplamente aplicada no processamento de coleções de dados:

*   **Transformação de Dados:** Utilizar `filter` para remover itens inválidos de uma lista e `map` para formatar os itens restantes, garantindo que a lista original permaneça intacta.
*   **Gerenciamento de Estado:** Bibliotecas de front-end utilizam o conceito de "Redutores" (funções puras que recebem o estado atual e uma ação, retornando um novo estado) para garantir previsibilidade na interface.

## ⚠️ Erros Comuns

*   **Tentar mutar argumentos:** Alterar diretamente um objeto ou array recebido como parâmetro quebra a pureza da função e gera bugs difíceis de rastrear.
*   **Confundir Iteração com Transformação:** Usar `forEach` para alterar elementos de uma lista externa em vez de usar `map` para gerar uma nova lista.
*   **Efeitos Colaterais Escondidos:** Inserir um `console.log` ou uma chamada de API dentro de uma função que deveria ser puramente matemática.

## ✅ Checklist de Domínio

*   [ ] Consigo identificar se uma função é pura ou impura analisando seus efeitos colaterais?
*   [ ] Sei como transformar um dado sem alterar a fonte original (imutabilidade)?
*   [ ] Compreendo como passar funções como argumentos para outras funções?
*   [ ] Consigo prever o resultado de uma função baseando-me apenas em seus parâmetros de entrada?

```json
[
  {
    "question": "Qual é a principal característica de uma 'Função Pura'?",
    "options": [
      "Ela deve obrigatoriamente utilizar variáveis globais.",
      "Ela sempre retorna o mesmo resultado para os mesmos argumentos e não possui efeitos colaterais.",
      "Ela altera o valor dos parâmetros passados por referência para economizar memória.",
      "Ela só pode ser executada uma única vez durante o ciclo de vida do programa."
    ],
    "answer": 1
  },
  {
    "question": "O conceito de imutabilidade na Programação Funcional sugere que:",
    "options": [
      "Variáveis devem ser atualizadas constantemente para refletir o estado real.",
      "Objetos não podem ser criados após a inicialização do sistema.",
      "Dados não devem ser alterados após criados; em vez disso, criam-se novas estruturas de dados.",
      "O uso de constantes é proibido para permitir flexibilidade."
    ],
    "answer": 2
  },
  {
    "question": "O que define uma 'Função de Alta Ordem' (Higher-Order Function)?",
    "options": [
      "Uma função que possui mais de 100 linhas de código.",
      "Uma função que é executada com prioridade pelo processador.",
      "Uma função que não aceita argumentos e não retorna valores.",
      "Uma função que recebe outra função como argumento ou retorna uma função."
    ],
    "answer": 3
  }
]
```