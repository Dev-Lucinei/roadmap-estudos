# roadmap-estudos/tests/unit/test_dsl_engine/test_validation_details.py

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.services.dsl.engine import DSLExecutionEngine

class TestDSLExecutionEngineValidationDetails:
    """Test cases for DSLExecutionEngine detailed validation."""

    def test_validate_missing_params_by_type(self):
        """Testa que params obrigatórios por tipo são validados."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {}},
                {"id": "s2", "type": "quiz", "params": {"topic": "X"}},
                {"id": "s3", "type": "roadmap", "params": {"theme": "DevOps"}},
                {"id": "s4", "type": "project", "params": {"description": "desc"}},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        messages = [e["message"] for e in result["errors"]]
        assert any("não pode ser vazio" in m for m in messages)
        assert any("'question_count' ausente" in m for m in messages)
        assert any("'depth' ausente" in m for m in messages)
        assert any("'title' ausente" in m for m in messages)

    def test_validate_invalid_id_format(self):
        """Testa que ID fora do padrão kebab-case é detectado."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "Invalid_ID", "type": "lesson", "params": {"topic": "X"}},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("kebab-case" in e["message"] for e in result["errors"])

    def test_validate_invalid_depth(self):
        """Testa que profundidade inválida é detectada."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {
                    "id": "s1",
                    "type": "roadmap",
                    "params": {"theme": "DevOps", "depth": "ultra"},
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("Profundidade inválida" in e["message"] for e in result["errors"])

    def test_validate_quiz_question_count_range(self):
        """Testa que question_count deve estar entre 1 e 20."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {
                    "id": "s1",
                    "type": "quiz",
                    "params": {"topic": "X", "question_count": 0},
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("entre 1 e 20" in e["message"] for e in result["errors"])

    def test_validate_quiz_pass_score_range(self):
        """Testa que pass_score deve estar entre 0 e 100."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {
                    "id": "s1",
                    "type": "quiz",
                    "params": {"topic": "X", "question_count": 5, "pass_score": -1},
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("entre 0 e 100" in e["message"] for e in result["errors"])

    def test_validate_id_format_valid(self):
        """Testa que _validate_id_format aceita kebab-case válido."""
        assert DSLExecutionEngine._validate_id_format("step-1") is True
        assert DSLExecutionEngine._validate_id_format("abc") is True
        assert DSLExecutionEngine._validate_id_format("a-b-c") is True
        assert DSLExecutionEngine._validate_id_format("a1") is True
        assert DSLExecutionEngine._validate_id_format("a") is True

    def test_validate_id_format_invalid(self):
        """Testa que _validate_id_format rejeita formatos inválidos."""
        assert DSLExecutionEngine._validate_id_format("-abc") is False
        assert DSLExecutionEngine._validate_id_format("ABC") is False
        assert DSLExecutionEngine._validate_id_format("") is False
        assert DSLExecutionEngine._validate_id_format("step_1") is False
        assert DSLExecutionEngine._validate_id_format("step 1") is False

    def test_validate_all_types(self):
        """Testa validação de todos os tipos válidos de step."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "All types",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {
                    "id": "s2",
                    "type": "quiz",
                    "params": {"topic": "Python", "question_count": 5},
                },
                {"id": "s3", "type": "diagnosis", "params": {"topic": "Python"}},
                {
                    "id": "s4",
                    "type": "roadmap",
                    "params": {"theme": "DevOps", "depth": "beginner"},
                },
                {"id": "s5", "type": "review", "params": {"topic": "Python"}},
                {"id": "s6", "type": "project", "params": {"title": "Meu Projeto"}},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is True

    def test_validate_project_with_description(self):
        """Testa que project aceita description opcional."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {
                    "id": "s1",
                    "type": "project",
                    "params": {"title": "Projeto", "description": "Descrição"},
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is True

    def test_validate_project_invalid_description(self):
        """Testa que description do project deve ser string."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {
                    "id": "s1",
                    "type": "project",
                    "params": {"title": "Projeto", "description": 123},
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False

    def test_validate_id_invalid_chars(self):
        """Testa id com caracteres especiais (_ ou digitos no inicio)."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "step_1", "type": "lesson", "params": {"topic": "X"}},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("kebab-case" in e["message"] for e in result["errors"])

    def test_validate_params_extra_fields(self):
        """Testa que campos extras em params nao quebram a validacao."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {
                    "id": "s1",
                    "type": "lesson",
                    "params": {
                        "topic": "Python",
                        "extra_field": "inesperado",
                        "outro_campo": 42,
                    },
                },
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is True
