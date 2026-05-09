window.roadmapData = {
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
            content: "Base fundamental para qualquer linguagem de programação.",
            difficulty: "easy"
        },
        { id: "var-tipos", title: "Variáveis e Tipos de Dados", type: "subtopic", side: "left", difficulty: "easy" },
        { id: "operadores", title: "Operadores (Aritméticos, Relacionais, Lógicos)", type: "subtopic", side: "left", difficulty: "easy" },
        { id: "condicionais", title: "Estruturas Condicionais (if/else, switch)", type: "subtopic", side: "left", difficulty: "easy" },
        { id: "repeticao", title: "Estruturas de Repetição (for, while, do-while)", type: "subtopic", side: "left", difficulty: "easy" },
        { id: "funcoes-escopo", title: "Funções e Escopo", type: "subtopic", side: "right", difficulty: "medium" },
        { id: "recursividade", title: "Recursividade Básica", type: "subtopic", side: "right", difficulty: "hard" },
        { id: "strings-arrays", title: "Manipulação de Strings e Arrays", type: "subtopic", side: "right", difficulty: "medium" },
        { id: "io-arquivos", title: "Manipulação de Arquivos I/O", type: "subtopic", side: "right", difficulty: "medium" },

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
            content: "Diferentes formas e estilos de estruturar o seu código.",
            difficulty: "medium"
        },
        { id: "estruturada", title: "Programação Estruturada", type: "subtopic", side: "left", difficulty: "easy" },
        { id: "poo", title: "Programação Orientada a Objetos (POO)", type: "subtopic", side: "left", difficulty: "medium" },
        { id: "funcional", title: "Programação Funcional (Conceitos Básicos)", type: "subtopic", side: "left", difficulty: "medium" },
        { id: "eventos", title: "Programação Orientada a Eventos", type: "subtopic", side: "left", difficulty: "medium" },
        { id: "reativa", title: "Programação Reativa", type: "subtopic", side: "right", difficulty: "hard" },
        { id: "concorrente", title: "Programação Concorrente", type: "subtopic", side: "right", difficulty: "hard" },
        { id: "assincrona", title: "Programação Assíncrona", type: "subtopic", side: "right", difficulty: "hard" },

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
            content: "Recursos específicos e avançados da linguagem Python.",
            difficulty: "medium"
        },
        { id: "dados-nativos", title: "Tipos de Dados Nativos (Listas, Tuplas, Dicionários, Sets)", type: "subtopic", side: "left", difficulty: "easy" },
        { id: "funcoes-modulos", title: "Funções e Módulos", type: "subtopic", side: "left", difficulty: "easy" },
        { id: "arq-manipulacao", title: "Manipulação de Arquivos", type: "subtopic", side: "left", difficulty: "easy" },
        { id: "excecoes", title: "Tratamento de Exceções", type: "subtopic", side: "left", difficulty: "medium" },
        { id: "comprehensions", title: "Compreensões de Lista/Dicionário", type: "subtopic", side: "right", difficulty: "medium" },
        { id: "decorators-generators", title: "Decoradores e Geradores", type: "subtopic", side: "right", difficulty: "hard" },
        { id: "asyncio", title: "Programação Assíncrona com `asyncio`", type: "subtopic", side: "right", difficulty: "hard" }
    ]
};
