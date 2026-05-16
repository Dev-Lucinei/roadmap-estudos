# Atributos e Métodos

## 🎯 Resumo Executivo
Atributos e métodos são os constituintes fundamentais que definem a estrutura e o comportamento de um objeto. Enquanto os atributos representam o **estado** (dados), os métodos representam o **comportamento** (ações), permitindo a organização lógica e a manipulação controlada de informações dentro de um sistema.

## 📚 Conceitos-Chave

1.  **Atributos (Variáveis de Instância):** São as características que descrevem um objeto. Eles armazenam os dados que diferenciam uma instância de outra.
    *   *Exemplo:* Em um sistema bancário, um objeto `Conta` possui atributos como `saldo`, `numero` e `titular`.
2.  **Métodos (Funções de Membro):** São as funções que definem o que o objeto pode fazer. Eles operam sobre os atributos do próprio objeto ou processam dados externos para retornar um resultado.
    *   *Exemplo:* O objeto `Conta` possui métodos como `depositar(valor)` e `sacar(valor)`.
3.  **Estado do Objeto:** É o conjunto de valores atuais de todos os seus atributos em um determinado momento. Métodos são as ferramentas que alteram esse estado.
4.  **Assinatura do Método:** Composta pelo nome do método e seus parâmetros. Define como o mundo externo interage com o comportamento do objeto.

## 💡 Aplicação Prática

Imagine a modelagem de um **Controle Remoto**:

*   **Atributos:** `volumeAtual` (inteiro), `canalAtual` (inteiro), `estaLigado` (booleano).
*   **Métodos:** 
    *   `aumentarVolume()`: Incrementa o atributo `volumeAtual`.
    *   `trocarCanal(novoCanal)`: Altera o valor de `canalAtual`.
    *   `ligarDesligar()`: Inverte o valor booleano de `estaLigado`.

No código (exemplo conceitual):
```python
class ControleRemoto:
    def __init__(self):
        self.volume = 10 # Atributo

    def aumentar_volume(self): # Método
        self.volume += 1
```

## ⚠️ Erros Comuns

*   **Atributos Públicos Expostos:** Permitir que qualquer parte do sistema altere um atributo diretamente (ex: `conta.saldo = -500`) sem passar por um método que valide a regra de negócio.
*   **Métodos com Responsabilidade Excessiva:** Criar métodos que realizam tarefas que não pertencem ao objeto, ferindo a coesão (ex: um método `gerarRelatorioPDF()` dentro do objeto `Conta`).
*   **Confusão entre Variáveis Locais e Atributos:** Declarar variáveis dentro de métodos e esperar que elas persistam como estado do objeto.

## ✅ Checklist de Domínio

*   [ ] Consigo identificar quais dados devem ser atributos e quais ações devem ser métodos em um requisito?
*   [ ] Entendo que métodos são a única forma recomendada de alterar o estado (atributos) de um objeto?
*   [ ] Sei distinguir a definição de um atributo na classe do valor que ele assume em uma instância específica?
