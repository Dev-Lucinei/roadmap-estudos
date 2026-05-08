const roadmapData = {
    title: "Fundamentos de Programação e Python",
    nodes: [
        // --- SEÇÃO: LÓGICA DE PROGRAMAÇÃO ---
        {
            id: "logica-prog",
            title: "Lógica de Programação",
            type: "central",
            group: "Fundamentos",
            children: [
                "var-tipos", "operadores", "condicionais", "repeticao",
                "funcoes-escopo", "recursividade", "strings-arrays", "io-arquivos"
            ],
            content: "Base fundamental para qualquer linguagem de programação."
        },
        { id: "var-tipos", title: "Variáveis e Tipos de Dados", type: "subtopic", side: "left" },
        { id: "operadores", title: "Operadores (Aritméticos, Relacionais, Lógicos)", type: "subtopic", side: "left" },
        { id: "condicionais", title: "Estruturas Condicionais (if/else, switch)", type: "subtopic", side: "left" },
        { id: "repeticao", title: "Estruturas de Repetição (for, while, do-while)", type: "subtopic", side: "left" },
        { id: "funcoes-escopo", title: "Funções e Escopo", type: "subtopic", side: "right" },
        { id: "recursividade", title: "Recursividade Básica", type: "subtopic", side: "right" },
        { id: "strings-arrays", title: "Manipulação de Strings e Arrays", type: "subtopic", side: "right" },
        { id: "io-arquivos", title: "Manipulação de Arquivos I/O", type: "subtopic", side: "right" },

        // --- SEÇÃO: PARADIGMAS DE PROGRAMAÇÃO ---
        {
            id: "paradigmas",
            title: "Paradigmas de Programação",
            type: "central",
            group: "Python para Desenvolvimento",
            children: [
                "estruturada", "poo", "funcional", "eventos",
                "reativa", "concorrente", "assincrona"
            ],
            content: "Diferentes formas e estilos de estruturar o seu código."
        },
        { id: "estruturada", title: "Programação Estruturada", type: "subtopic", side: "left" },
        { id: "poo", title: "Programação Orientada a Objetos (POO)", type: "subtopic", side: "left" },
        { id: "funcional", title: "Programação Funcional (Conceitos Básicos)", type: "subtopic", side: "left" },
        { id: "eventos", title: "Programação Orientada a Eventos", type: "subtopic", side: "left" },
        { id: "reativa", title: "Programação Reativa", type: "subtopic", side: "right" },
        { id: "concorrente", title: "Programação Concorrente", type: "subtopic", side: "right" },
        { id: "assincrona", title: "Programação Assíncrona", type: "subtopic", side: "right" },

        // --- SEÇÃO: SINTAXE E ESTRUTURAS ---
        {
            id: "sintaxe-estruturas",
            title: "Sintaxe e Estruturas",
            type: "central",
            group: "Python para Desenvolvimento",
            children: [
                "dados-nativos", "funcoes-modulos", "arq-manipulacao", "excecoes",
                "comprehensions", "decorators-generators", "asyncio"
            ],
            content: "Recursos específicos e avançados da linguagem Python."
        },
        { id: "dados-nativos", title: "Tipos de Dados Nativos (Listas, Tuplas, Dicionários, Sets)", type: "subtopic", side: "left" },
        { id: "funcoes-modulos", title: "Funções e Módulos", type: "subtopic", side: "left" },
        { id: "arq-manipulacao", title: "Manipulação de Arquivos", type: "subtopic", side: "left" },
        { id: "excecoes", title: "Tratamento de Exceções", type: "subtopic", side: "left" },
        { id: "comprehensions", title: "Compreensões de Lista/Dicionário", type: "subtopic", side: "right" },
        { id: "decorators-generators", title: "Decoradores e Geradores", type: "subtopic", side: "right" },
        { id: "asyncio", title: "Programação Assíncrona com `asyncio`", type: "subtopic", side: "right" }
    ]
};

export default roadmapData;
