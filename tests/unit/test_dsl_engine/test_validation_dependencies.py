# roadmap-estudos/tests/unit/test_dsl_engine/test_validation_dependencies.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.services.dsl.engine import DSLExecutionEngine

class TestDSLExecutionEngineDependencies:
    """Test cases for DSLExecutionEngine dependency validation."""

    def test_validate_duplicate_id(self):
        """Testa que IDs duplicados são detectados."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "step-1", "type": "lesson", "params": {"topic": "A"}},
                {"id": "step-1", "type": "lesson", "params": {"topic": "B"}},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("duplicado" in e["message"] for e in result["errors"])

    def test_validate_dependency_nonexistent_id(self):
        """Testa que dependência para id inexistente é detectada."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}},
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "B"},
                    "depends_on": ["nonexistent"],
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("inexistente" in e["message"] for e in result["errors"])

    def test_validate_dependency_cycle(self):
        """Testa que ciclo de dependência é detectado."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {
                    "id": "s1",
                    "type": "lesson",
                    "params": {"topic": "A"},
                    "depends_on": ["s2"],
                },
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "B"},
                    "depends_on": ["s1"],
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("Ciclo" in e["message"] for e in result["errors"])

    def test_validate_self_dependency_cycle(self):
        """Testa que self-dependency é detectada como ciclo."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {
                    "id": "s1",
                    "type": "lesson",
                    "params": {"topic": "A"},
                    "depends_on": ["s1"],
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("Ciclo" in e["message"] for e in result["errors"])

    def test_validate_depends_on_invalid_type(self):
        """Testa que depends_on deve ser lista."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}},
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "B"},
                    "depends_on": "s1",
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("deve ser uma lista" in e["message"] for e in result["errors"])

    def test_validate_depends_on_future(self):
        """Testa que dependencia para step em posicao posterior eh detectada."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}},
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "B"},
                    "depends_on": ["s3"],
                },
                {"id": "s3", "type": "lesson", "params": {"topic": "C"}},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("inexistente" in e["message"] for e in result["errors"])

    def test_validate_depends_on_duplicate(self):
        """Testa depends_on com ids duplicados."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}},
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "B"},
                    "depends_on": ["s1", "s1"],
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is True

    def test_validate_complex_nested_deps(self):
        """Testa cadeia longa de dependencias (5 niveis)."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Complex chain",
            "steps": [
                {"id": "nivel-1", "type": "lesson", "params": {"topic": "A"}},
                {
                    "id": "nivel-2",
                    "type": "lesson",
                    "params": {"topic": "B"},
                    "depends_on": ["nivel-1"],
                },
                {
                    "id": "nivel-3",
                    "type": "lesson",
                    "params": {"topic": "C"},
                    "depends_on": ["nivel-2"],
                },
                {
                    "id": "nivel-4",
                    "type": "lesson",
                    "params": {"topic": "D"},
                    "depends_on": ["nivel-3"],
                },
                {
                    "id": "nivel-5",
                    "type": "lesson",
                    "params": {"topic": "E"},
                    "depends_on": ["nivel-4"],
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is True
