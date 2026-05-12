# Pilares da POO

## 🎯 Resumo Executivo
Os quatro pilares da Programação Orientada a Objetos (Abstração, Encapsulamento, Herança e Polimorfismo) são os fundamentos para a criação de sistemas modulares e escaláveis. Eles permitem que desenvolvedores gerenciem a complexidade do software, promovendo o reuso de código e a proteção da integridade dos dados.

## 📚 Conceitos-Chave

1.  **Abstração**: Consiste em isolar os aspectos essenciais de um objeto, ignorando detalhes irrelevantes para o contexto.
    *   *Exemplo*: Em um sistema bancário, a abstração de uma `Conta` foca em `saldo` e `titular`, ignorando a cor dos olhos do cliente.
2.  **Encapsulamento**: Protege o estado interno de um objeto, ocultando detalhes de implementação e expondo apenas o necessário através de interfaces públicas (métodos).
    *   *Exemplo*: O uso de modificadores `private` para atributos e métodos `get/set` ou métodos de negócio para alterar o saldo.
3.  **Herança**: Permite que uma classe (filha) herde atributos e comportamentos de outra classe (pai), estabelecendo uma relação de "é um".
    *   *Exemplo*: Uma classe `ContaCorrente` herda de `Conta`, aproveitando a lógica de depósitos e saques já existente.
4.  **Polimorfismo**: Capacidade de um objeto ser tratado de diferentes formas. Permite que classes diferentes respondam à mesma mensagem de maneiras distintas.
    *   *Exemplo*: Tanto `ContaCorrente` quanto `ContaPoupanca` possuem o método `calcularJuros()`, mas cada uma implementa uma regra de cálculo diferente.

## 💡 Aplicação Prática

*   **Sistemas de Pagamento**: Uma classe abstrata `MeioPagamento` define o método `processar()`. As classes `CartaoCredito` e `Boleto` herdam dessa base, mas cada uma implementa seu próprio fluxo de processamento (**Polimorfismo**). O número do cartão é mantido privado (**Encapsulamento**), expondo apenas se a transação foi aprovada.

## ⚠️ Erros Comuns

*   **Uso excessivo de Herança**: Tentar usar herança para reaproveitar código quando a relação não é de "é um". Nesses casos, a composição é preferível.
*   **Encapsulamento "Vazado"**: Criar métodos `get` e `set` para todos os atributos sem critério, o que anula a proteção dos dados e expõe a implementação interna.

## ✅ Checklist de Domínio

*   [ ] Consigo identificar qual pilar aplicar para reduzir a duplicação de código?
*   [ ] Sei quando usar uma interface ou classe abstrata para garantir o polimorfismo?
*   [ ] Entendo a diferença entre ocultar dados (private) e prover comportamento (public)?
*   [ ] Consigo explicar a relação de hierarquia entre classes sem confundir com associação?

```json
[
  {
    "question": "Qual pilar da POO é responsável por esconder os detalhes internos de funcionamento de um objeto e expor apenas o necessário?",
    "options": ["Abstração", "Polimorfismo", "Encapsulamento", "Herança"],
    "answer": 2
  },
  {
    "question": "O conceito de que uma classe filha pode sobrescrever um método da classe pai para fornecer uma implementação específica é um exemplo de:",
    "options": ["Abstração", "Polimorfismo", "Encapsulamento", "Acoplamento"],
    "answer": 1
  },
  {
    "question": "Ao criar uma classe 'Veiculo' com atributos genéricos para que 'Carro' e 'Moto' os utilizem, qual pilar está sendo aplicado prioritariamente?",
    "options": ["Encapsulamento", "Modularização", "Herança", "Composição"],
    "answer": 2
  }
]
```