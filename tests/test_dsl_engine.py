"""Tests para o DSL Engine."""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.dsl.engine import DSLExecutionEngine

VALID_DSL = {
    "version": "1.0",
    "name": "Test Flow",
    "steps": [
        {"id": "step-1", "type": "lesson", "params": {"topic": "Python"}},
        {"id": "step-2", "type": "quiz", "params": {"topic": "Python", "question_count": 5}},
    ],
}


class TestDSLExecutionEngine:
    """Test cases for DSLExecutionEngine."""

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

    def test_execute_invalid_dsl_returns_validation_error(self):
        """Testa que execute() com DSL inválido retorna validation_error."""
        engine = DSLExecutionEngine()
        result = engine.execute({})
        assert result["status"] == "validation_error"
        assert "errors" in result

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

    def test_validate_dependency_nonexistent_id(self):
        """Testa que dependência para id inexistente é detectada."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}},
                {"id": "s2", "type": "lesson", "params": {"topic": "B"}, "depends_on": ["nonexistent"]},
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
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}, "depends_on": ["s2"]},
                {"id": "s2", "type": "lesson", "params": {"topic": "B"}, "depends_on": ["s1"]},
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
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}, "depends_on": ["s1"]},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("Ciclo" in e["message"] for e in result["errors"])

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
                {"id": "s1", "type": "roadmap", "params": {"theme": "DevOps", "depth": "ultra"}},
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
                {"id": "s1", "type": "quiz", "params": {"topic": "X", "question_count": 0}},
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
                {"id": "s1", "type": "quiz", "params": {"topic": "X", "question_count": 5, "pass_score": -1}},
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
                {"id": "s2", "type": "quiz", "params": {"topic": "Python", "question_count": 5}},
                {"id": "s3", "type": "diagnosis", "params": {"topic": "Python"}},
                {"id": "s4", "type": "roadmap", "params": {"theme": "DevOps", "depth": "beginner"}},
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
                {"id": "s1", "type": "project", "params": {"title": "Projeto", "description": "Descrição"}},
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
                {"id": "s1", "type": "project", "params": {"title": "Projeto", "description": 123}},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False

    def test_execute_valid_flow_details(self):
        """Testa detalhes da execução de um fluxo válido."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Detailed Flow",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {"id": "s2", "type": "lesson", "params": {"topic": "Django"}},
                {"id": "s3", "type": "lesson", "params": {"topic": "APIs"}},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert result["steps_count"] == 3

    def test_validate_depends_on_invalid_type(self):
        """Testa que depends_on deve ser lista."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}},
                {"id": "s2", "type": "lesson", "params": {"topic": "B"}, "depends_on": "s1"},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is False
        assert any("deve ser uma lista" in e["message"] for e in result["errors"])


    def test_execute_complete_flow_all_types(self):
        """Testa execução com todos os 6 tipos de step."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Complete Flow",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {"id": "s2", "type": "quiz", "params": {"topic": "Python", "question_count": 5}},
                {"id": "s3", "type": "diagnosis", "params": {"topic": "Python"}},
                {"id": "s4", "type": "roadmap", "params": {"theme": "DevOps", "depth": "beginner"}},
                {"id": "s5", "type": "review", "params": {"topic": "Python"}},
                {"id": "s6", "type": "project", "params": {"title": "Projeto"}},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert result["steps_count"] == 6
        assert len(result["executed_steps"]) == 6
        assert len(result["failed_steps"]) == 0
        types = [s["type"] for s in result["executed_steps"]]
        assert types == ["lesson", "quiz", "diagnosis", "roadmap", "review", "project"]

    def test_execute_with_satisfied_dependencies(self):
        """Testa execução com dependências satisfeitas."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Dependencies",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {"id": "s2", "type": "quiz", "params": {"topic": "Python", "question_count": 5}, "depends_on": ["s1"]},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert len(result["executed_steps"]) == 2
        assert len(result["failed_steps"]) == 0

    def test_execute_with_unsatisfied_dependency(self):
        """Testa que step é skipped quando dependência não foi executada."""
        engine = DSLExecutionEngine()
        step = {"id": "s2", "type": "lesson", "params": {"topic": "Python"}, "depends_on": ["s1"]}
        result = engine._execute_step(step, [])
        assert result["status"] == "skipped"
        assert "não foi executada" in result["reason"]

    def test_execute_unknown_type_returns_validation_error(self):
        """Testa execução com tipo de step desconhecido retorna validation_error."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Unknown type",
            "steps": [
                {"id": "s1", "type": "unknown_type", "params": {"topic": "X"}},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "validation_error"

    def test_execute_step_raises_exception(self):
        """Testa execução quando um handler lança exceção."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Exception test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
            ],
        }
        with patch.object(engine, '_execute_lesson', side_effect=Exception("Simulated error")):
            result = engine.execute(dsl)
        assert result["status"] == "partial"
        assert len(result["failed_steps"]) == 1
        assert result["failed_steps"][0]["status"] == "failed"
        assert "Simulated error" in result["failed_steps"][0]["error"]

    def test_execute_shared_context(self):
        """Testa contexto compartilhado entre steps."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Shared context",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {"id": "s2", "type": "quiz", "params": {"topic": "Python", "question_count": 5}},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert "s1_result" in result["context"]
        assert "s2_result" in result["context"]
        assert result["context"]["last_topic"] == "Python"

    def test_execute_invalid_dsl_structure_returns_validation_error(self):
        """Testa execução de DSL estruturalmente inválida."""
        engine = DSLExecutionEngine()
        result = engine.execute(42)
        assert result["status"] == "validation_error"
        assert "errors" in result

    def test_execute_empty_steps_returns_validation_error(self):
        """Testa execução de DSL com steps vazio."""
        engine = DSLExecutionEngine()
        dsl = {"version": "1.0", "name": "Empty", "steps": []}
        result = engine.execute(dsl)
        assert result["status"] == "validation_error"
        assert "errors" in result


    # ------------------------------------------------------------------ #
    # NOVOS TESTES - TASK-7.3: Edge Cases para Validacao (8)            #
    # ------------------------------------------------------------------ #

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

    def test_validate_name_empty(self):
        """Testa name vazio ou so espacos."""
        engine = DSLExecutionEngine()
        for bad_name in ["", "   "]:
            dsl = {
                "version": "1.0",
                "name": bad_name,
                "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "X"}}],
            }
            result = engine.validate(dsl)
            assert result["valid"] is False
            name_errors = [e for e in result["errors"] if "name" in e["path"]]
            assert len(name_errors) > 0

    def test_validate_name_not_string(self):
        """Testa name como tipo nao string (int, list, dict)."""
        engine = DSLExecutionEngine()
        for bad_name in [123, ["a"], {"n": "v"}]:
            dsl = {
                "version": "1.0",
                "name": bad_name,
                "steps": [{"id": "s1", "type": "lesson", "params": {"topic": "X"}}],
            }
            result = engine.validate(dsl)
            assert result["valid"] is False
            name_errors = [e for e in result["errors"] if "name" in e["path"]]
            assert len(name_errors) > 0

    def test_validate_depends_on_future(self):
        """Testa que dependencia para step em posicao posterior eh detectada."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "test",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}},
                {"id": "s2", "type": "lesson", "params": {"topic": "B"}, "depends_on": ["s3"]},
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
                {"id": "s2", "type": "lesson", "params": {"topic": "B"}, "depends_on": ["s1", "s1"]},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is True

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

    def test_validate_complex_nested_deps(self):
        """Testa cadeia longa de dependencias (5 niveis)."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Complex chain",
            "steps": [
                {"id": "nivel-1", "type": "lesson", "params": {"topic": "A"}},
                {"id": "nivel-2", "type": "lesson", "params": {"topic": "B"}, "depends_on": ["nivel-1"]},
                {"id": "nivel-3", "type": "lesson", "params": {"topic": "C"}, "depends_on": ["nivel-2"]},
                {"id": "nivel-4", "type": "lesson", "params": {"topic": "D"}, "depends_on": ["nivel-3"]},
                {"id": "nivel-5", "type": "lesson", "params": {"topic": "E"}, "depends_on": ["nivel-4"]},
            ],
        }
        result = engine.validate(dsl)
        assert result["valid"] is True

    # ------------------------------------------------------------------ #
    # NOVOS TESTES - TASK-7.3: Edge Cases para Execucao (7)             #
    # ------------------------------------------------------------------ #

    def test_execute_dependency_chain(self):
        """Testa execucao de cadeia A->B->C->D."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Chain",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {"id": "s2", "type": "lesson", "params": {"topic": "Django"}, "depends_on": ["s1"]},
                {"id": "s3", "type": "lesson", "params": {"topic": "Flask"}, "depends_on": ["s2"]},
                {"id": "s4", "type": "lesson", "params": {"topic": "API"}, "depends_on": ["s3"]},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert len(result["executed_steps"]) == 4
        assert len(result["failed_steps"]) == 0

    def test_execute_missing_dependency_skips(self):
        """Testa que B nao executa quando A nao esta no fluxo (validation_error)."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Missing dep",
            "steps": [
                {"id": "s2", "type": "lesson", "params": {"topic": "B"}, "depends_on": ["s1"]},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "validation_error"
        assert any("inexistente" in e["message"] for e in result["errors"])

    def test_execute_failed_step_stops_chain(self):
        """Testa que B falha e C nao executa (depende de B)."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Fail chain",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "A"}},
                {"id": "s2", "type": "lesson", "params": {"topic": "B"}, "depends_on": ["s1"]},
                {"id": "s3", "type": "lesson", "params": {"topic": "C"}, "depends_on": ["s2"]},
            ],
        }
        with patch.object(engine, '_execute_lesson', side_effect=[
            {"topic": "A", "difficulty": "medium", "duration_minutes": 30, "content_generated": False, "note": ""},
            Exception("Step B failed"),
        ]):
            result = engine.execute(dsl)
        assert result["status"] == "partial"
        assert len(result["executed_steps"]) == 1
        assert len(result["failed_steps"]) == 1
        assert result["executed_steps"][0]["id"] == "s1"
        assert result["failed_steps"][0]["id"] == "s2"
        assert "Step B failed" in result["failed_steps"][0]["error"]

    def test_execute_valid_flow_result_structure(self):
        """Testa que execute retorna todas as chaves esperadas no resultado."""
        engine = DSLExecutionEngine()
        result = engine.execute(VALID_DSL)
        assert set(result.keys()) == {"status", "steps_count", "executed_steps", "failed_steps", "context"}

    def test_execute_empty_depends_on_allowed(self):
        """Testa que depends_on vazio [] funciona como sem dependencia."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Empty dep",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}, "depends_on": []},
                {"id": "s2", "type": "lesson", "params": {"topic": "Django"}, "depends_on": []},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert len(result["executed_steps"]) == 2

    def test_execute_chain_preserves_context(self):
        """Testa que contexto eh populado apos execucao de cadeia."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Context chain",
            "steps": [
                {"id": "step-a", "type": "lesson", "params": {"topic": "Python"}},
                {"id": "step-b", "type": "lesson", "params": {"topic": "Django"}, "depends_on": ["step-a"]},
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert "step-a_result" in result["context"]
        assert "step-b_result" in result["context"]
        assert result["context"]["last_topic"] == "Django"

    # ------------------------------------------------------------------ #
    # NOVOS TESTES - TASK-7.3: Edge Cases para Integracao (2)           #
    # ------------------------------------------------------------------ #

    def test_validate_then_execute_flow(self):
        """Testa validate + execute de DSL valida -> completed."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Validate then execute",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {"id": "s2", "type": "quiz", "params": {"topic": "Python", "question_count": 5}},
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


if __name__ == "__main__":
    import unittest

    unittest.main()
