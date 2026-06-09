"""Tests for FastAPI routes."""

import json
import os
import shutil
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client (shared per module)."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def temp_data():
    """Temp data directory for tests."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


class TestListRoadmapsEndpoint:
    """Tests for GET /api/roadmaps."""

    def test_empty(self, client):
        response = client.get("/api/roadmaps")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_with_data(self, client, temp_data):
        path = os.path.join(temp_data, "roadmap_python.json")
        with open(path, "w") as f:
            json.dump({"title": "Python"}, f)
        with patch(
            "backend.core.config.DATA_DIR",
            temp_data,
        ):
            response = client.get("/api/roadmaps")
            assert response.status_code == 200
            assert "python" in response.json()


class TestLoadRoadmapEndpoint:
    """Tests for GET /api/roadmap/{roadmap_id}."""

    def test_not_found(self, client):
        response = client.get("/api/roadmap/nonexistent")
        assert response.status_code == 404

    def test_invalid_id(self, client):
        response = client.get("/api/roadmap/INVALID ID!")
        assert response.status_code == 400

    def test_valid_load(self, client, temp_data):
        data = {"title": "Test", "nodes": []}
        path = os.path.join(temp_data, "roadmap_test.json")
        with open(path, "w") as f:
            json.dump(data, f)
        with patch(
            "backend.core.config.DATA_DIR",
            temp_data,
        ):
            response = client.get("/api/roadmap/test")
            assert response.status_code == 200
            assert response.json()["title"] == "Test"


class TestDepMapEndpoint:
    """Tests for GET /api/dep-map."""

    def test_empty(self, client, temp_data):
        with patch(
            "backend.core.config.DATA_DIR",
            temp_data,
        ):
            response = client.get("/api/dep-map")
            assert response.status_code == 200
            assert response.json() == {}

    def test_with_data(self, client, temp_data):
        dep_map = {"A": ["B"]}
        path = os.path.join(temp_data, "dep_map.json")
        with open(path, "w") as f:
            json.dump(dep_map, f)
        with patch(
            "backend.core.config.DATA_DIR",
            temp_data,
        ):
            response = client.get("/api/dep-map")
            assert response.status_code == 200
            assert response.json() == {"A": ["B"]}


class TestGenerateLessonEndpoint:
    """Tests for POST /api/generate-lesson."""

    def test_success(self, client):
        with patch("backend.api.routes_fastapi.processar_node"):
            response = client.post(
                "/api/generate-lesson",
                json={
                    "node_id": "n1",
                    "title": "Python",
                    "type": "subtopic",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["node_id"] == "n1"

    def test_validation_error(self, client):
        response = client.post(
            "/api/generate-lesson",
            json={"node_id": "", "title": "T"},
        )
        assert response.status_code == 422


class TestGenerateRoadmapEndpoint:
    """Tests for POST /api/generate-roadmap."""

    def test_success(self, client):
        roadmap_data = {"title": "Test", "nodes": []}
        with (
            patch(
                "backend.api.routes_fastapi.gerar_roadmap_ia",
                return_value=roadmap_data,
            ),
            patch("backend.api.routes_fastapi.salvar_roadmap"),
        ):
            response = client.post(
                "/api/generate-roadmap",
                json={"tema": "Python"},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "success"

    def test_ia_failure(self, client):
        with patch(
            "backend.api.routes_fastapi.gerar_roadmap_ia",
            return_value=None,
        ):
            response = client.post(
                "/api/generate-roadmap",
                json={"tema": "Python"},
            )
            assert response.status_code == 500


class TestQuizEndpoints:
    """Tests for quiz generate and evaluate endpoints."""

    def test_generate_quiz_success(self, client):
        quiz_data = [
            {
                "question": "Q1",
                "options": ["A", "B"],
                "answer": 0,
            }
        ]
        with patch("backend.api.routes_fastapi.quiz_service") as mock_svc:
            mock_svc.generate_quiz.return_value = quiz_data
            response = client.post(
                "/api/quiz/generate",
                json={"node_id": "n1", "title": "T"},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "success"

    def test_generate_quiz_not_found(self, client):
        with patch("backend.api.routes_fastapi.quiz_service") as mock_svc:
            mock_svc.generate_quiz.side_effect = FileNotFoundError("not found")
            response = client.post(
                "/api/quiz/generate",
                json={"node_id": "n1", "title": "T"},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "error"

    def test_generate_quiz_value_error(self, client):
        with patch("backend.api.routes_fastapi.quiz_service") as mock_svc:
            mock_svc.generate_quiz.side_effect = ValueError("bad data")
            response = client.post(
                "/api/quiz/generate",
                json={"node_id": "n1", "title": "T"},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "error"

    def test_evaluate_quiz_success(self, client):
        eval_result = {"score": 80, "passed": True}
        with patch("backend.api.routes_fastapi.quiz_service") as mock_svc:
            mock_svc.evaluate_quiz.return_value = eval_result
            response = client.post(
                "/api/quiz/evaluate",
                json={
                    "node_id": "n1",
                    "title": "T",
                    "quiz_data": [
                        {
                            "question": "Q",
                            "options": ["A", "B"],
                            "answer": 0,
                        }
                    ],
                    "user_answers": {"0": 0},
                },
            )
            assert response.status_code == 200
            assert response.json()["status"] == "success"

    def test_evaluate_quiz_value_error(self, client):
        from backend.api.routes_fastapi import quiz_service

        with patch.object(
            quiz_service,
            "evaluate_quiz",
            side_effect=ValueError("bad data"),
        ):
            response = client.post(
                "/api/quiz/evaluate",
                json={
                    "node_id": "n1",
                    "title": "T",
                    "quiz_data": [
                        {
                            "question": "Q",
                            "options": ["A"],
                            "answer": 0,
                        }
                    ],
                    "user_answers": {"0": 0},
                },
            )
            assert response.status_code == 200
            assert response.json()["status"] == "error"

    def test_evaluate_quiz_file_not_found(self, client):
        from backend.api.routes_fastapi import quiz_service

        with patch.object(
            quiz_service,
            "evaluate_quiz",
            side_effect=FileNotFoundError("not found"),
        ):
            response = client.post(
                "/api/quiz/evaluate",
                json={
                    "node_id": "n1",
                    "title": "T",
                    "quiz_data": [
                        {
                            "question": "Q",
                            "options": ["A"],
                            "answer": 0,
                        }
                    ],
                    "user_answers": {"0": 0},
                },
            )
            assert response.status_code == 200
            assert response.json()["status"] == "error"


class TestDiagnoseEndpoint:
    """Tests for POST /api/diagnose."""

    def test_success(self, client):
        diag_result = {
            "status": "hit",
            "message": "OK",
            "has_gap": False,
        }
        with patch("backend.api.routes_fastapi.diagnosis_service") as mock_svc:
            mock_svc.diagnose.return_value = diag_result
            response = client.post(
                "/api/diagnose",
                json={
                    "topic": "Python",
                    "user_answer": "Resposta",
                },
            )
            assert response.status_code == 200
            assert response.json()["status"] == "success"


class TestGetLessonEndpoint:
    """Tests for GET /licoes/{lesson_file}."""

    def test_not_found(self, client):
        response = client.get("/licoes/nonexistent.md")
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]
