# Abstração

## 🎯 Resumo Executivo
Abstração é o processo de simplificar a complexidade ocultando detalhes irrelevantes e expondo apenas as características essenciais de um objeto ou sistema. Na Engenharia de Software, ela é fundamental para gerenciar a carga cognitiva, permitindo que desenvolvedores foquem no "o quê" uma entidade faz, em vez de "como" ela faz internamente.

## 📚 Conceitos-Chave

*   **Identificação de Atributos Essenciais:** Consiste em selecionar apenas as propriedades necessárias para o contexto atual.
    *   *Exemplo:* Em um sistema de RH, a abstração de um "Funcionário" foca em `cargo` e `salário`. Em um sistema de saúde, a mesma entidade foca em `tipo sanguíneo` e `alergias`.
*   **Contratos e Interfaces:** A abstração define um contrato de comportamento. Você define a assinatura de um método (entrada e saída) sem se preocupar com a lógica interna.
    *   *Exemplo:* Um botão de "Play" em um player de vídeo é uma abstração; você sabe que ele inicia a mídia, mas não precisa entender como o codec de vídeo processa os bits.
*   **Níveis de Hierarquia:** Criar modelos que representam conceitos genéricos que podem se especializar conforme a necessidade.
    *   *Exemplo:* Uma classe abstrata `Pagamento` define que todo pagamento deve ter um `valor` e um método `processar()`, independentemente se é via Boleto ou Cartão.
*   **Redução de Acoplamento:** Ao depender de abstrações em vez de implementações concretas, o sistema torna-se mais flexível a mudanças.

## 💡 Aplicação Prática

1.  **APIs (Application Programming Interfaces):** Quando você utiliza uma biblioteca para enviar e-mails, você interage com uma abstração como `EmailService.send(destinatario, mensagem)`. Você não precisa gerenciar protocolos SMTP, sockets de rede ou autenticação TLS manualmente; a abstração cuida disso.
2.  **Modelagem de Domínio:** Ao projetar um sistema de e-commerce, o conceito de "Produto" é uma abstração. Ele ignora detalhes físicos irrelevantes para o código (como o material da embalagem) e foca no que importa para o negócio (preço, estoque, SKU).

## ⚠️ Erros Comuns

*   **Abstração Prematura:** Tentar criar modelos genéricos antes de entender completamente os requisitos, resultando em uma complexidade desnecessária (conhecido como *Overengineering*).
*   **Vazamento de Abstração (Leaky Abstraction):** Quando detalhes da implementação "vazam" para quem está usando a abstração, forçando o usuário a entender o que deveria estar oculto para conseguir resolver um problema.
*   **Abstração "Tudo ou Nada":** Criar abstrações tão genéricas que perdem o sentido semântico, tornando o código difícil de ler e manter.

## ✅ Checklist de Domínio

- [ ] Consigo identificar quais detalhes de um objeto são irrelevantes para um determinado contexto de software?
- [ ] Sei diferenciar uma interface (o contrato) da sua implementação técnica?
- [ ] Consigo explicar como a abstração ajuda a isolar mudanças em uma parte do código sem afetar o sistema inteiro?
- [ ] Sou capaz de revisar um código e identificar se uma classe está expondo detalhes internos que deveriam estar ocultos?