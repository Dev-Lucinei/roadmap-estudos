# Herança

## 🎯 Resumo Executivo
A herança é um mecanismo fundamental que permite que uma classe (subclasse) adquira atributos e comportamentos de outra classe (superclasse). Sua principal importância reside na promoção do reuso de código e no estabelecimento de uma hierarquia semântica do tipo "é um", facilitando a manutenção e a extensão de sistemas.

## 📚 Conceitos-Chave

*   **Superclasse (Classe Pai/Base):** É a classe genérica que contém as características comuns. Exemplo: Uma classe `Veiculo` que possui o atributo `velocidade` e o método `mover()`.
*   **Subclasse (Classe Filha/Derivada):** É a classe especializada que herda da superclasse e pode adicionar novos membros ou modificar os existentes. Exemplo: Uma classe `Carro` que estende `Veiculo` e adiciona o atributo `numeroDePortas`.
*   **Reuso de Código:** A subclasse não precisa reescrever o código já presente na superclasse. Se `Animal` tem o método `respirar()`, as classes `Cachorro` e `Gato` herdam essa funcionalidade automaticamente.
*   **Especialização:** A herança permite que você refine comportamentos. Enquanto a superclasse define o "o quê", a subclasse pode definir "como" de forma específica.
*   **Relacionamento "É UM":** A regra de ouro da herança. Se você pode dizer logicamente que "um Carro **é um** Veículo" ou "um Gerente **é um** Funcionário", a herança é candidata a ser aplicada.

## 💡 Aplicação Prática

**Cenário: Sistema de Processamento de Pagamentos**
Imagine um sistema que lida com diferentes métodos de pagamento. Todos compartilham propriedades básicas, mas cada um tem sua especificidade.

1.  **Superclasse `Pagamento`**: Contém `valor`, `data` e o método `processar()`.
2.  **Subclasse `PagamentoCartao`**: Herda de `Pagamento` e adiciona `numeroCartao` e `bandeira`.
3.  **Subclasse `PagamentoBoleto`**: Herda de `Pagamento` e adiciona `codigoBarras` e `dataVencimento`.

Neste caso, o motor de regras do sistema pode tratar qualquer objeto que herde de `Pagamento` de forma genérica para fins de relatório, enquanto as subclasses tratam as regras específicas de cada transação.

## ⚠️ Erros Comuns

*   **Herança para Reuso de Código sem Relação Semântica:** Usar herança apenas para "copiar" métodos de uma classe que não possui relação lógica com a nova. Se a relação não for "é um", a herança criará um acoplamento frágil e confuso.
*   **Hierarquias Muito Profundas:** Criar cadeias de herança excessivas (ex: A -> B -> C -> D -> E). Isso torna o código difícil de rastrear, depurar e entender, pois o comportamento está espalhado por muitos níveis.
*   **Violação da Substituição:** Alterar drasticamente o comportamento de um método herdado a ponto de ele quebrar a expectativa de quem usa a superclasse (ex: uma subclasse que lança uma exceção em um método que a superclasse garante que sempre funcionará).

## ✅ Checklist de Domínio

- [ ] Consigo identificar em um diagrama de classes qual é a superclasse e qual é a subclasse?
- [ ] Sei explicar a diferença entre herdar um atributo e herdar um método?
- [ ] Consigo aplicar a regra do "é um" para validar se a herança é a ferramenta correta para o problema?
- [ ] Entendo que uma alteração na superclasse afetará automaticamente todas as suas subclasses?