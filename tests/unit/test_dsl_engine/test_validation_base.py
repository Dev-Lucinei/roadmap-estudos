# roadmap-estudos/tests/unit/test_dsl_engine/test_validation_base.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.services.dsl.engine import DSLExecutionEngine
from . import VALID_DSL

class TestDSLExecutionEngineValidationBase:
    """Test cases for DSLExecutionEngine basic validation."""

    def test_validate_valid_dsl(self):
        """Testa validate() com DSL estruturalmente válido."""
        engine = DSLExecutionEngine()
        result = engine.validate(VALID_DSL)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_invalid_type_string(self):
        """Testa validate() com string (inválido)."""
        engine = DSLExecutionEngine()
        result = engine.validate("string")
        assert result["valid"] is False

    def test_validate_invalid_type_list(self):
        """Testa validate() com list (inválido)."""
        engine = DSLExecutionEngine()
        result = engine.validate(["item1", "item2"])
        assert result["valid"] is False

    def test_validate_invalid_type_none(self):
        """Testa validate() com None (inválido)."""
        engine = DSLExecutionEngine()
        result = engine.validate(None)
        assert result["valid"] is False

    def test_validate_invalid_type_int(self):
        """Testa validate() com int (inválido)."""
        engine = DSLExecutionEngine()
        result = engine.validate(123)
        assert result["valid"] is False

    def test_validate_invalid_type_bool(self):
        """Testa validate() com bool (inválido)."""
        engine = DSLExecutionEngine()
        result = engine.validate(True)
        assert result["valid"] is False

    def test_validate_missing_version(self):
        """Testa que version é obrigatório."""
        engine = DSLExecutionEngine()
        dsl = {
            "name": "test",
            "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "X"}}],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        errors = [e["path"] for e in result["errors"]]
        assert "version" in errors

    def test_validate_invalid_version_format(self):
        """Testa que version deve ser X.Y."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "abc",
            "name": "test",
            "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "X"}}],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        version_errors = [e for e in result["errors"] if "version" in e["path"]]
        assert len(version_errors) > 0
        assert "X.Y" in version_errors[0]["message"]

    def test_validate_empty_steps(self):
        """Testa que steps não pode ser vazio."""
        engine = DSLExecutionEngine()
        dsl = {"version": "1.0", "name": "test", "steps": []}
        result = engine.validate(dsl)
        assert result["valid"] is False
        steps_errors = [e for e in result["errors"] if "steps" in e["path"]]
        assert len(steps_errors) > 0

    def test_validate_missing_steps(self):
        """Testa que steps é obrigatório."""
        engine = DSLExecutionEngine()
        dsl = {"version": "1.0", "name": "test"}
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("steps" in e["path"] for e in result["errors"])

    def test_validate_invalid_type(self):
        """Testa que tipo inválido é detectado."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [{"id": "s1", "type": "invalid_type", "params": {"topic": "X"}}],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("Tipo inválido" in e["message"] for e in result["errors"])

    def test_validate_version_format_invalid(self):
        """Testa version com formatos invalidos: '1.2.3.4', '', '1.'."""
        engine = DSLExecutionEngine()
        for bad_version in ["1.2.3.4", "", "1.", ".1", "v1.0"]:
            dsl = {
                "version": bad_version,
                "name": "test",
                "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "X"}}],
            }
            result = engine.validate(dsl)
            assert result["valid"] is False
            version_errors = [e for e in result["errors"] if "version" in e["path"]]
            assert len(version_errors) > 0

    def test_validate_version_non_string(self):
        """Testa version como tipo nao string (int, list)."""
        engine = DSLExecutionEngine()
        for bad_version in [123, ["1.0"], {"v": "1.0"}]:
            dsl = {
                "version": bad_version,
                "name": "test",
                "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "X"}}],
            }
            result = engine.validate(dsl)
            assert result["valid"] is False
            version_errors = [e for e in result["errors"] if "version" in e["path"]]
            assert len(version_errors) > 0
