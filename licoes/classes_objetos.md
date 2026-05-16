# Classes e Objetos

## 🎯 Resumo Executivo
Classes e Objetos são os pilares fundamentais da Programação Orientada a Objetos, funcionando como o "molde" e o "produto final", respectivamente. Eles permitem que desenvolvedores organizem o código agrupando dados (atributos) e comportamentos (métodos) em unidades lógicas que representam entidades do mundo real.

## 📚 Conceitos-Chave

1.  **A Classe como Molde (Blueprint):** Uma classe é uma estrutura abstrata que define quais dados um objeto terá e o que ele poderá fazer. Ela não ocupa espaço na memória para dados reais, apenas define a estrutura.
    *   *Exemplo:* Uma classe `Carro` define que todo carro tem `cor` e `modelo`, e pode `acelerar()`.
2.  **O Objeto como Instância:** O objeto é a realização concreta de uma classe. Quando você cria um objeto, está "instanciando" a classe, alocando memória para armazenar valores específicos.
    *   *Exemplo:* O `meuCarro` é um objeto da classe `Carro` com `cor="Azul"` e `modelo="Sedan"`.
3.  **Atributos (Estado):** São as características ou variáveis pertencentes à classe. Eles definem o estado de um objeto em um determinado momento.
4.  **Métodos (Comportamento):** São as funções definidas dentro da classe que operam sobre os atributos ou realizam ações específicas daquela entidade.

## 💡 Aplicação Prática

Imagine um sistema de e-commerce. A **Classe** seria a definição de um `Produto`:

```python
class Produto:
    def __init__(self, nome, preco):
        self.nome = nome    # Atributo
        self.preco = preco  # Atributo

    def aplicar_desconto(self, porcentagem): # Método
        self.preco -= (self.preco * porcentagem / 100)
```

A **Aplicação** ocorre quando instanciamos objetos diferentes a partir dessa mesma base:
*   `laptop = Produto("MacBook", 10000)`
*   `mouse = Produto("Mouse Gamer", 200)`

Cada objeto mantém seus próprios valores de `nome` e `preco` de forma independente.

## ⚠️ Erros Comuns

*   **Confundir Classe com Objeto:** Tentar acessar ou modificar atributos diretamente na classe (ex: `Carro.cor = "Verde"`) em vez de fazê-lo na instância específica (`meuCarro.cor = "Verde"`).
*   **Estado Compartilhado Indesejado:** Definir atributos que deveriam ser de instância (únicos para cada objeto) como atributos de classe (estáticos), fazendo com que a alteração em um objeto afete todos os outros.

## ✅ Checklist de Domínio

*   [ ] Consigo explicar a diferença entre uma classe e uma instância (objeto)?
*   [ ] Sei como definir atributos para armazenar o estado de um objeto?
*   [ ] Sou capaz de criar métodos que representem as ações que um objeto pode realizar?
*   [ ] Entendo que múltiplos objetos da mesma classe possuem identidades e dados independentes?

```json
[
  {
    "question": "Qual é a relação fundamental entre Classe e Objeto?",
    "options": [
      "A Classe é uma instância em execução de um Objeto.",
      "O Objeto é um modelo abstrato, enquanto a Classe é a aplicação prática.",
      "A Classe funciona como um molde (blueprint) e o Objeto é uma instância real baseada nesse molde.",
      "Não há diferença técnica, são sinônimos na Engenharia de Software."
    ],
    "answer": 2
  },
  {
    "question": "O que define o 'estado' de um objeto em um determinado momento?",
    "options": [
      "Os nomes dos métodos definidos na classe.",
      "Os valores atribuídos aos seus atributos.",
      "A quantidade de memória RAM total do sistema.",
      "O histórico de classes das quais ele herdou características."
    ],
    "answer": 1
  },
  {
    "question": "Se criarmos dois objetos 'A' e 'B' a partir da mesma classe 'Usuario', o que acontece se alterarmos um atributo de instância no objeto 'A'?",
    "options": [
      "O objeto 'B' terá seu atributo alterado automaticamente para manter a sincronia.",
      "A classe 'Usuario' será modificada permanentemente.",
      "O sistema emitirá um erro, pois objetos da mesma classe devem ser idênticos.",
      "Apenas o objeto 'A' sofrerá a alteração, pois cada objeto possui seu próprio estado."
    ],
    "answer": 3
  }
]
```