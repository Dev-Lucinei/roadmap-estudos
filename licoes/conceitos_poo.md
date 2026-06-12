# Pilares da Programação Orientada a Objetos em Python: Abstração, Encapsulamento, Herança e Polimorfismo

## 1. Introdução e Fundamentos
A Programação Orientada a Objetos (POO) é o modelo que permite organizar código em torno de **objetos** que representam entidades do mundo real ou conceitual. Os quatro pilares — **Abstração**, **Encapsulamento**, **Herança** e **Polimorfismo** — formam a base estrutural que garante reutilização, manutenção e extensibilidade dos sistemas. Dominar esses conceitos em Python é essencial para construir aplicações robustas, legíveis e escaláveis.

## 2. Imersão Técnica
### 2.1 Abstração
Abstração consiste em **identificar e modelar os aspectos essenciais** de um problema, ignorando detalhes irrelevantes. Em Python, usamos classes como “contratos” que descrevem comportamentos esperados sem expor a implementação interna.

- **Classe abstrata**: pode ser declarada com `abc.ABC` e `@abstractmethod`, forçando subclasses a implementar métodos críticos.
```python
from abc import ABC, abstractmethod

class Figura(ABC):
    @abstractmethod
    def area(self) -> float:
        pass
```

### 2.2 Encapsulamento
Encapsulamento protege o estado interno de um objeto, expondo apenas uma interface controlada. Em Python, a convenção de prefixo `_` (protegido) e `__` (privado) controla a visibilidade, enquanto **properties** permitem leitura/escrita segura.

```python
class ContaBancaria:
    def __init__(self, saldo_inicial: float):
        self.__saldo = saldo_inicial  # atributo privado

    @property
    def saldo(self) -> float:
        return self.__saldo

    def depositar(self, valor: float):
        if valor > 0:
            self.__saldo += valor
```

### 2.3 Herança
Herança permite que uma **classe filha** reutilize atributos e métodos da **classe pai**, promovendo **reuso de código** e hierarquias lógicas.

- **Herança simples**: `class Subclasse(Pai):`
- **Herança múltipla**: Python permite múltiplas superclasses, porém deve‑se observar o **Method Resolution Order (MRO)**.

```python
class Animal:
    def __init__(self, nome: str):
        self.nome = nome

    def falar(self):
        raise NotImplementedError

class Cachorro(Animal):
    def falar(self):
        return "Au Au"
```

### 2.4 Polimorfismo
Polimorfismo permite que objetos de diferentes classes respondam ao **mesmo método** de forma distinta. Em Python, isso ocorre naturalmente (duck typing), mas pode ser reforçado com **interfaces** ou **classes abstratas**.

```python
def emitir_som(animal: Animal):
    print(animal.falar())

emitir_som(Cachorro("Rex"))   # Saída: Au Au
```

O método `emitir_som` aceita qualquer objeto que implemente `falar()`, independentemente da sua classe concreta.

## 3. Aplicação Prática
### Cenário: Sistema de Gerenciamento de Veículos

1. **Abstração** – Criamos uma classe abstrata `Veiculo` que define a interface comum.
2. **Encapsulamento** – Mantemos o atributo `__velocidade` privado e controlamos seu acesso via propriedades.
3. **Herança** – `Carro` e `Moto` herdam de `Veiculo` e implementam comportamentos específicos.
4. **Polimorfismo** – Função `acelerar_veiculo` aceita qualquer `Veiculo` e invoca seu método `acelerar`.

```python
from abc import ABC, abstractmethod

class Veiculo(ABC):
    def __init__(self, marca: str):
        self.marca = marca
        self.__velocidade = 0

    @property
    def velocidade(self) -> int:
        return self.__velocidade

    def _set_velocidade(self, nova: int):
        self.__velocidade = max(0, nova)

    @abstractmethod
    def acelerar(self, incremento: int):
        pass

    @abstractmethod
    def frear(self, decremento: int):
        pass


class Carro(Veiculo):
    def acelerar(self, incremento: int = 10):
        self._set_velocidade(self.velocidade + incremento)

    def frear(self, decremento: int = 5):
        self._set_velocidade(self.velocidade - decremento)


class Moto(Veiculo):
    def acelerar(self, incremento: int = 15):
        self._set_velocidade(self.velocidade + incremento)

    def frear(self, decremento: int = 7):
        self._set_velocidade(self.velocidade - decremento)


def acelerar_veiculo(veiculo: Veiculo, inc: int):
    veiculo.acelerar(inc)
    print(f"{veiculo.__class__.__name__} da marca {veiculo.marca} agora está a {veiculo.velocidade} km/h")


# Uso
c1 = Carro("Toyota")
m1 = Moto("Honda")

acelerar_veiculo(c1, 20)   # Carro → 20 km/h
acelerar_veiculo(m1, 20)   # Moto → 20 km/h (incremento interno de 15 + 5 extra)
```

> **Observação:** A função `acelerar_veiculo` demonstra **polimorfismo** ao tratar `Carro` e `Moto` como `Veiculo` sem saber detalhes de implementação.

## 4. Conexão Modo Zen
> • **Micro‑pausas**: a cada 25 minutos de estudo, levante, respire fundo e faça um alongamento de 30 segundos.  
> • **Visualização**: imagine mentalmente um objeto real (ex.: um carro) antes de escrever sua classe — isso fixa a abstração.  
> • **Código consciente**: escreva cada método como se fosse uma pequena história