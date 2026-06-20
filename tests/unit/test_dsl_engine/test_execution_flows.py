# roadmap-estudos/tests/unit/test_dsl_engine/test_execution_flows.py

import os
import sys
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.services.dsl.engine import DSLExecutionEngine
from . import VALID_DSL

class TestDSLExecutionEngineFlows:
    """Test cases for DSLExecutionEngine flow execution."""

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

    def test_execute_complete_flow_all_types(self):
        """Testa execução com todos os 6 tipos de step."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Complete Flow",
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
                {
                    "id": "s2",
                    "type": "quiz",
                    "params": {"topic": "Python", "question_count": 5},
                    "depends_on": ["s1"],
                },
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert len(result["executed_steps"]) == 2
        assert len(result["failed_steps"]) == 0

    def test_execute_with_unsatisfied_dependency(self):
        """Testa que step é skipped quando dependência não foi executada."""
        engine = DSLExecutionEngine()
        step = {
            "id": "s2",
            "type": "lesson",
            "params": {"topic": "Python"},
            "depends_on": ["s1"],
        }
        result = engine._execute_step(step, [])
        assert result["status"] == "skipped"
        assert "não foi executada" in result["reason"]

    def test_execute_unknown_type_returns_validation_err(self):
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
        with patch.object(engine, "_execute_lesson", side_effect=Exception("Simulated error")):
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
                {
                    "id": "s2",
                    "type": "quiz",
                    "params": {"topic": "Python", "question_count": 5},
                },
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert "s1_result" in result["context"]
        assert "s2_result" in result["context"]
        assert result["context"]["last_topic"] == "Python"

    def test_execute_dependency_chain(self):
        """Testa execucao de cadeia A->B->C->D."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Chain",
            "steps": [
                {"id": "s1", "type": "lesson", "params": {"topic": "Python"}},
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "Django"},
                    "depends_on": ["s1"],
                },
                {
                    "id": "s3",
                    "type": "lesson",
                    "params": {"topic": "Flask"},
                    "depends_on": ["s2"],
                },
                {
                    "id": "s4",
                    "type": "lesson",
                    "params": {"topic": "API"},
                    "depends_on": ["s3"],
                },
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
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "B"},
                    "depends_on": ["s1"],
                },
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
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "B"},
                    "depends_on": ["s1"],
                },
                {
                    "id": "s3",
                    "type": "lesson",
                    "params": {"topic": "C"},
                    "depends_on": ["s2"],
                },
            ],
        }
        with patch.object(
            engine,
            "_execute_lesson",
            side_effect=[
                {
                    "topic": "A",
                    "difficulty": "medium",
                    "duration_minutes": 30,
                    "content_generated": False,
                    "note": "",
                },
                Exception("Step B failed"),
            ],
        ):
            result = engine.execute(dsl)
        assert result["status"] == "partial"
        assert len(result["executed_steps"]) == 1
        assert len(result["failed_steps"]) == 1
        assert result["executed_steps"][0]["id"] == "s1"
        assert result["failed_steps"][0]["id"] == "s2"
        assert "Step B failed" in result["failed_steps"][0]["error"]

    def test_execute_empty_depends_on_allowed(self):
        """Testa que depends_on vazio [] funciona como sem dependencia."""
        engine = DSLExecutionEngine()
        dsl = {
            "version": "1.0",
            "name": "Empty dep",
            "steps": [
                {
                    "id": "s1",
                    "type": "lesson",
                    "params": {"topic": "Python"},
                    "depends_on": [],
                },
                {
                    "id": "s2",
                    "type": "lesson",
                    "params": {"topic": "Django"},
                    "depends_on": [],
                },
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
                {
                    "id": "step-b",
                    "type": "lesson",
                    "params": {"topic": "Django"},
                    "depends_on": ["step-a"],
                },
            ],
        }
        result = engine.execute(dsl)
        assert result["status"] == "completed"
        assert "step-a_result" in result["context"]
        assert "step-b_result" in result["context"]
        assert result["context"]["last_topic"] == "Django"
