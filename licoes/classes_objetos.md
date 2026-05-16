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
