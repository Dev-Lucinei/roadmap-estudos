# Design: Test Coverage Implementation

## Overview

Implementar suite de testes para atingir 85-90% de cobertura, mantendo os testes existentes e adicionando novos para módulos não testados.

## Arquitetura de Testes

```
tests/
├── conftest.py              # Fixtures compartilhadas
├── test_api.py              # DiagnosisService (existente, manter)
├── test_diagnosis.py        # Lógica de diagnóstico (existente, manter)
├── test_diagnosis_logic.py  # [REMOVER] Duplicado
├── test_endpoints.py        # [NOVO] Endpoints HTTP server.py
├── test_generate_roadmap.py # [NOVO] generate_roadmap.py
├── test_generate_lessons.py# [NOVO] generate_lessons.py
└── test_dsl_engine.py       # [NOVO] DSL engine
```

## Conftest.py — Fixtures Compartilhadas

### Fixtures Obrigatórias

```python
# tests/conftest.py

import pytest
import os
import sys
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock

@pytest.fixture
def temp_data_dir():
    """Diretório temporário para testes."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)

@pytest.fixture
def mock_openai_response(content="Test response"):
    """Mock de resposta OpenAI."""
    mock = Mock()
    mock.choices = [Mock(message=Mock(content=content))]
    return mock

@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock completo do cliente OpenAI."""
    with patch('openai.OpenAI') as mock_class:
        client = Mock()
        client.chat.completions.create.return_value = mock_openai_response
        mock_class.return_value = client
        yield client

@pytest.fixture
def sample_roadmap():
    """Roadmap de exemplo para testes."""
    return {
        "title": "Test Roadmap",
        "nodes": [
            {"id": "node1", "title": "Central", "type": "central", "children": ["node2"]},
            {"id": "node2", "title": "Subtopic", "type": "subtopic"}
        ]
    }

@pytest.fixture
def sample_dep_map():
    """dep_map de exemplo."""
    return {
        "Python Fundamentos": [],
        "Análise de Dados": ["Python Fundamentos"],
        "Machine Learning": ["Python Fundamentos", "Análise de Dados"]
    }
```

## Testes de Endpoints (test_endpoints.py)

### Estratégia: HTTP Handler Testing

```python
# Abordagem: Mockar servidor e testar handlers diretamente
# via chamada de métodos com Request simulada

class MockRequest:
    def __init__(self, path, data=None, method='GET'):
        self.path = path
        self._data = data or {}
        self.method = method

    def read(self, size=None):
        return json.dumps(self._data).encode()
```

### Estrutura dos Testes

```python
class TestListRoadmaps:
    """Test GET /api/roadmaps"""

    def test_list_roadmaps_empty(self, temp_data_dir):
        # Setup: diretório vazio
        # Action: list_roadmaps()
        # Assert: retorna lista vazia []

    def test_list_roadmaps_with_files(self, temp_data_dir):
        # Setup: criar roadmap_*.json
        # Action: list_roadmaps()
        # Assert: lista contém arquivos, exclui dep_map.json
```

## Testes de Geração (test_generate_*.py)

### Estratégia: Mock OpenAI + tmp directory

```python
def test_salvar_roadmap_new_file(sample_roadmap, temp_data_dir):
    """Testa criação de arquivo de roadmap."""
    # given
    expected_file = os.path.join(temp_data_dir, "roadmap_test.json")

    # when
    result = salvar_roadmap("test", sample_roadmap)

    # then
    assert os.path.exists(expected_file)
    assert "test" in result  # ou filepath completo
```

## Testes DSL Engine (test_dsl_engine.py)

### Estratégia: Teste unitário direto

```python
def test_execute_returns_executed_status():
    """Testa que execute() retorna status correto."""
    engine = DSLExecutionEngine()
    result = engine.execute({"action": "test"})
    assert result["status"] == "executed"

def test_validate_valid_dict():
    """Testa validate() com dict válido."""
    engine = DSLExecutionEngine()
    assert engine.validate({"key": "value"}) is True

def test_validate_invalid_type():
    """Testa validate() com tipo inválido."""
    engine = DSLExecutionEngine()
    assert engine.validate("string") is False
    assert engine.validate(None) is False
```

## Abordagem de Mocking

### OpenAI Mock (consistente)

```python
def create_mock_openai(content="response"):
    """Factory para mock do OpenAI."""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=content))]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client
```

### Patch Points

| Módulo | Patch Point | O que Mockar |
|--------|-------------|---------------|
| server.py | `server.OpenAI` | Classe OpenAI inteira |
| generate_roadmap.py | `generate_roadmap.client` | Instância client |
| generate_lessons.py | `generate_lessons.client` | Instância client |

## Error Cases

### Cenários de Erro a Testar

| Erro | Endpoint | Mock | Assert |
|------|----------|------|--------|
| Arquivo não existe | GET /api/roadmap/* | - | 404 |
| dep_map não existe | GET /api/dep-map | - | 404 |
| Params inválidos | POST /api/diagnose | - | 400 |
| API key missing | POST /api/diagnose | - | PermissionError |
| Falha LLM | POST /api/diagnose | Exceção | 502 |
| Erro interno | POST /api/* | Exceção | 500 |

## Performance

- Meta: todos os testes executam em < 5s
- Fixtures com cleanup em teardown
- tmpdir para isolamento
- Sem dependência de rede real

## Manutenção

- Fixtures em conftest.py para DRY
- Nomenclatura: `test_<module>_<function>_<scenario>`
- Docstrings em cada teste descrevendo o cenário
- Comments explicando mocks complexos