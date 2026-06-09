"""Tests for legacy ApiRoutes."""

import json
import os
from unittest.mock import patch

from backend.api.routes import ApiRoutes


class TestListRoadmaps:
    """Tests for ApiRoutes.list_roadmaps."""

    def test_empty_dir(self, temp_data_dir):
        with patch("backend.api.routes.DATA_DIR", temp_data_dir):
            result = ApiRoutes.list_roadmaps()
            assert result == []

    def test_with_roadmaps(self, temp_data_dir):
        for name in ["python", "java"]:
            path = os.path.join(temp_data_dir, f"roadmap_{name}.json")
            with open(path, "w") as f:
                json.dump({"title": name}, f)
        with patch("backend.api.routes.DATA_DIR", temp_data_dir):
            result = ApiRoutes.list_roadmaps()
            assert sorted(result) == ["java", "python"]

    def test_ignores_non_roadmap_files(self, temp_data_dir):
        with open(os.path.join(temp_data_dir, "other.json"), "w") as f:
            json.dump({}, f)
        with open(os.path.join(temp_data_dir, "roadmap_test.json"), "w") as f:
            json.dump({}, f)
        with patch("backend.api.routes.DATA_DIR", temp_data_dir):
            result = ApiRoutes.list_roadmaps()
            assert result == ["test"]

    def test_nonexistent_dir(self):
        with patch("backend.api.routes.DATA_DIR", "/nonexistent/path"):
            result = ApiRoutes.list_roadmaps()
            assert result == []


class TestLoadRoadmap:
    """Tests for ApiRoutes.load_roadmap."""

    def test_load_existing(self, temp_data_dir):
        data = {"title": "Test", "nodes": []}
        path = os.path.join(temp_data_dir, "roadmap_test.json")
        with open(path, "w") as f:
            json.dump(data, f)
        with patch("backend.api.routes.DATA_DIR", temp_data_dir):
            result = ApiRoutes.load_roadmap("test")
            assert result["title"] == "Test"

    def test_load_nonexistent(self, temp_data_dir):
        with patch("backend.api.routes.DATA_DIR", temp_data_dir):
            result = ApiRoutes.load_roadmap("nonexistent")
            assert result is None


class TestGetDepMap:
    """Tests for ApiRoutes.get_dep_map."""

    def test_existing_dep_map(self, temp_data_dir):
        dep_map = {"A": ["B"]}
        path = os.path.join(temp_data_dir, "dep_map.json")
        with open(path, "w") as f:
            json.dump(dep_map, f)
        with patch("backend.api.routes.DATA_DIR", temp_data_dir):
            result = ApiRoutes.get_dep_map()
            assert result == {"A": ["B"]}

    def test_missing_dep_map(self, temp_data_dir):
        with patch("backend.api.routes.DATA_DIR", temp_data_dir):
            result = ApiRoutes.get_dep_map()
            assert result == {}


class TestGenerateLesson:
    """Tests for ApiRoutes.generate_lesson."""

    def test_valid_data(self):
        data = {"node_id": "n1", "title": "Python"}
        with patch("backend.api.routes.processar_node") as mock:
            result = ApiRoutes.generate_lesson(data)
            assert result["status"] == "success"
            assert result["node_id"] == "n1"
            mock.assert_called_once_with(
                "n1",
                "Python",
                "subtopic",
                content=None,
                group=None,
                difficulty=None,
                roadmap_title=None,
                subtopics=None,
            )

    def test_with_type(self):
        data = {
            "node_id": "n1",
            "title": "T",
            "type": "central",
        }
        with patch("backend.api.routes.processar_node"):
            result = ApiRoutes.generate_lesson(data)
            assert result["status"] == "success"

    def test_missing_node_id(self):
        result = ApiRoutes.generate_lesson({"title": "T"})
        assert result is None

    def test_missing_title(self):
        result = ApiRoutes.generate_lesson({"node_id": "n1"})
        assert result is None


class TestCreateRoadmap:
    """Tests for ApiRoutes.create_roadmap."""

    def test_valid_create(self, temp_data_dir):
        roadmap_data = {"title": "Test", "nodes": []}
        with (
            patch(
                "backend.api.routes.gerar_roadmap_ia",
                return_value=roadmap_data,
            ),
            patch("backend.api.routes.salvar_roadmap") as mock_save,
        ):
            result = ApiRoutes.create_roadmap({"tema": "Python"})
            assert result["status"] == "success"
            assert result["tema"] == "Python"
            mock_save.assert_called_once()

    def test_no_tema(self):
        result = ApiRoutes.create_roadmap({})
        assert result is None

    def test_ia_returns_none(self):
        with patch(
            "backend.api.routes.gerar_roadmap_ia",
            return_value=None,
        ):
            result = ApiRoutes.create_roadmap({"tema": "T"})
            assert result is None


class TestHandleQuizGenerate:
    """Tests for ApiRoutes.handle_quiz_generate."""

    def test_valid_generate(self):
        quiz_data = [{"question": "Q1", "options": ["A"], "answer": 0}]
        with patch("backend.api.routes.quiz_service") as mock_qs:
            mock_qs.generate_quiz.return_value = quiz_data
            result = ApiRoutes.handle_quiz_generate({"node_id": "n1", "title": "T"})
            assert result["status"] == "success"
            assert result["quiz"] == quiz_data
            mock_qs.generate_quiz.assert_called_once_with("n1", "T")

    def test_missing_params(self):
        result = ApiRoutes.handle_quiz_generate({})
        assert result["status"] == "error"
        assert "obrigatórios" in result["message"]


class TestHandleDiagnose:
    """Tests for ApiRoutes.handle_diagnose."""

    def test_valid_diagnose(self):
        diagnosis_result = {
            "status": "hit",
            "message": "OK",
        }
        with patch("backend.api.routes.diagnosis_service") as mock_diag:
            mock_diag.diagnose.return_value = diagnosis_result
            result = ApiRoutes.handle_diagnose({"topic": "T", "user_answer": "A"})
            assert result["status"] == "hit"
            mock_diag.diagnose.assert_called_once_with("T", "A")

    def test_missing_params(self):
        result = ApiRoutes.handle_diagnose({})
        assert result is None
