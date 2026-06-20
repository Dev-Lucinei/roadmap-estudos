# roadmap-estudos/tests/unit/test_dsl_engine/test_execution_base.py

import os
import sys
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.services.dsl.engine import DSLExecutionEngine
from . import VALID_DSL

class TestDSLExecutionEngineExecutionBase:
    """Test cases for DSLExecutionEngine basic execution."""

    def test_init_empty_context(self):
        """Testa que engine inicializa com context vazio."""
        engine = DSLExecutionEngine()
        assert engine.context == {}

    def test_execute_returns_completed_status(self):
        """Testa que execute() retorna status 'completed'."""
        engine = DSLExecutionEngine()
        result = engine.execute(VALID_DSL)
        assert result["status"] == "completed"

    def test_execute_returns_executed_steps(self):
        """Testa que execute() retorna executed_steps."""
        engine = DSLExecutionEngine()
        result = engine.execute(VALID_DSL)
        assert result["status"] == "completed"
        assert len(result["executed_steps"]) == 2

    def test_execute_returns_steps_count(self):
        """Testa que execute() retorna steps_count."""
        engine = DSLExecutionEngine()
        result = engine.execute(VALID_DSL)
        assert result["steps_count"] == 2
        assert len(result["executed_steps"]) == 2

    def test_execute_invalid_dsl_returns_validation_err(self):
        """Testa que execute() com DSL inválido retorna validation_error."""
        engine = DSLExecutionEngine()
        result = engine.execute({})
        assert result["status"] == "validation_error"
        assert "errors" in result

    def test_multiple_executions_independent(self):
        """Testa que múltiplas execuções são independentes."""
        engine = DSLExecutionEngine()
        dsl1 = {
            "version": "1.0",
            "name": "Flow A",
            "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "A"}}],
        }
        dsl2 = {
            "version": "1.0",
            "name": "Flow B",
            "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "B"}}],
        }
        result1 = engine.execute(dsl1)
        result2 = engine.execute(dsl2)
        assert result1["status"] == "completed"
        assert result2["status"] == "completed"
        assert result1["executed_steps"][0]["result"]["topic"] == "A"
        assert result2["executed_steps"][0]["result"]["topic"] == "B"

    def test_context_initially_empty(self):
        """Testa que context é um dict vazio ao iniciar."""
        engine = DSLExecutionEngine()
        assert isinstance(engine.context, dict)
        assert len(engine.context) == 0

    def test_execute_invalid_dsl_structure_returns_validation_err(self):
        """Testa execução de DSL estruturalmente inválida."""
        engine = DSLExecutionEngine()
        result = engine.execute(42)
        assert result["status"] == "validation_error"
        assert "errors" in result

    def test_execute_empty_steps_returns_validation_err(self):
        """Testa execução de DSL com steps vazio."""
        engine = DSLExecutionEngine()
        dsl = {"version": "1.0", "name": "Empty", "steps": []}
        result = engine.execute(dsl)
        assert result["status"] == "validation_error"
        assert "errors" in result

    def test_execute_valid_flow_result_structure(self):
        """Testa que execute retorna todas as chaves esperadas no resultado."""
        engine = DSLExecutionEngine()
        result = engine.execute(VALID_DSL)
        assert set(result.keys()) == {
            "status",
            "steps_count",
            "executed_steps",
            "failed_steps",
            "context",
        }
