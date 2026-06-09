"""Fixtures compartilhadas para os testes."""

import os
import shutil
import sys
import tempfile
from unittest.mock import Mock

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_data_dir():
    """Diretório temporário para testes de dados."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def temp_output_dir():
    """Diretório temporário para saída de lições."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def sample_roadmap():
    """Roadmap de exemplo para testes."""
    return {
        "title": "Test Roadmap",
        "nodes": [
            {
                "id": "node1",
                "title": "Central Node",
                "type": "central",
                "group": "Fundamentos",
                "children": ["node2", "node3"],
            },
            {
                "id": "node2",
                "title": "Subtopic Left",
                "type": "subtopic",
                "side": "left",
            },
            {
                "id": "node3",
                "title": "Subtopic Right",
                "type": "subtopic",
                "side": "right",
            },
        ],
    }


@pytest.fixture
def sample_dep_map():
    """dep_map de exemplo para testes."""
    return {
        "Python Fundamentos": [],
        "Análise de Dados": ["Python Fundamentos"],
        "Machine Learning": ["Python Fundamentos", "Análise de Dados"],
    }


@pytest.fixture
def sample_lesson_content():
    """Conteúdo de lição de exemplo com quiz."""
    return """# Variáveis em Python

## 📋 Metadados
- Título: Variáveis
- Tags: python, basics

## 🎯 Resumo
Variáveis armazenam dados para uso posterior.

## 📚 Conteúdo Detalhado

Variáveis em Python são dinâmicas e não requerem declaração de tipo.

## ✅ Checklist
- [ ] Entender declaração de variáveis
- [ ] Conhecer tipos básicos

```json
[
  {"question": "Qual o tipo de x = 5?", "options": ["int", "str", "list", "dict"], "answer": 0},
  {"question": "Python é fortemente tipado?",
   "options": ["Sim", "Não", "Talvez", "Depende"], "answer": 0}
]
```
"""


def create_mock_openai_response(content: str = "Test response") -> Mock:
    """Factory para criar mock de resposta OpenAI."""
    mock = Mock()
    mock.choices = [Mock(message=Mock(content=content))]
    return mock


def create_mock_openai_client(content: str = "Test response") -> Mock:
    """Factory para criar mock completo do cliente OpenAI."""
    mock_response = create_mock_openai_response(content)

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_openai_client():
    """Fixture que retorna factory de mock client OpenAI.

    Uso: mock_openai_client("conteúdo personalizado") retorna um mock client.
    """
    return create_mock_openai_client
