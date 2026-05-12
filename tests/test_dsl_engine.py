"""Tests para o DSL Engine."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.dsl.engine import DSLExecutionEngine


class TestDSLExecutionEngine:
    """Test cases for DSLExecutionEngine."""

    def test_init_empty_context(self):
        """Testa que engine inicializa com context vazio."""
        engine = DSLExecutionEngine()
        assert engine.context == {}

    def test_execute_returns_executed_status(self):
        """Testa que execute() retorna status 'executed'."""
        engine = DSLExecutionEngine()
        result = engine.execute({"action": "test"})
        assert result["status"] == "executed"

    def test_execute_preserves_dsl(self):
        """Testa que execute() preserva o DSL no retorno."""
        engine = DSLExecutionEngine()
        dsl = {"action": "custom", "params": {"key": "value"}}
        result = engine.execute(dsl)
        assert result["dsl"] == dsl

    def test_execute_empty_dsl(self):
        """Testa que execute() funciona com DSL vazio."""
        engine = DSLExecutionEngine()
        result = engine.execute({})
        assert result["status"] == "executed"
        assert result["dsl"] == {}

    def test_validate_valid_dict(self):
        """Testa validate() com dict válido."""
        engine = DSLExecutionEngine()
        assert engine.validate({"key": "value"}) is True

    def test_validate_invalid_type_string(self):
        """Testa validate() com string (inválido)."""
        engine = DSLExecutionEngine()
        assert engine.validate("string") is False

    def test_validate_invalid_type_list(self):
        """Testa validate() com list (inválido)."""
        engine = DSLExecutionEngine()
        assert engine.validate(["item1", "item2"]) is False

    def test_validate_invalid_type_none(self):
        """Testa validate() com None (inválido)."""
        engine = DSLExecutionEngine()
        assert engine.validate(None) is False

    def test_validate_invalid_type_int(self):
        """Testa validate() com int (inválido)."""
        engine = DSLExecutionEngine()
        assert engine.validate(123) is False

    def test_validate_invalid_type_bool(self):
        """Testa validate() com bool (inválido)."""
        engine = DSLExecutionEngine()
        assert engine.validate(True) is False

    def test_multiple_executions_independent(self):
        """Testa que múltiplas execuções são independentes."""
        engine = DSLExecutionEngine()
        result1 = engine.execute({"id": 1})
        result2 = engine.execute({"id": 2})
        assert result1["dsl"]["id"] == 1
        assert result2["dsl"]["id"] == 2

    def test_context_initially_empty(self):
        """Testa que context é um dict vazio ao iniciar."""
        engine = DSLExecutionEngine()
        assert isinstance(engine.context, dict)
        assert len(engine.context) == 0


if __name__ == "__main__":
    import unittest

    unittest.main()
