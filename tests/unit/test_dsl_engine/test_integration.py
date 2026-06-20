# roadmap-estudos/tests/unit/test_dsl_engine/test_integration.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.services.dsl.engine import DSLExecutionEngine

class TestDSLExecutionEngineIntegration:
    """Test cases for DSLExecutionEngine integration."""

    def test_validate_then_execute_flow(self):
        """Testa validate + execute de DSL valida -> completed."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Validate then execute",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {
                    "id": "s2",
                    "type": "quiz",
                    "params": {"topic": "Python", "question_count": 5},
                },
            ],
        }
        validation = engine.validate(dsl)
        assert validation["valid"] is True
        execution = engine.execute(dsl)
        assert execution["status"] == "completed"
        assert len(execution["executed_steps"]) == 2

    def test_validate_then_execute_invalid(self):
        """Testa validate + execute de DSL invalida -> validation_error."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "abc",
            "name": "",
            "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "X"}}],
        }
        validation = engine.validate(dsl)
        assert validation["valid"] is False
        execution = engine.execute(dsl)
        assert execution["status"] == "validation_error"
        assert "errors" in execution
