"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from backend.models import (
    CreateRoadmapRequest,
    CreateRoadmapResponse,
    DiagnoseRequest,
    DiagnoseResponse,
    EvaluateQuizRequest,
    EvaluateQuizResponse,
    GenerateLessonRequest,
    GenerateLessonResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
)


class TestGenerateLessonRequest:
    """Tests for GenerateLessonRequest model."""

    def test_valid_request(self):
        req = GenerateLessonRequest(node_id="n1", title="Python")
        assert req.node_id == "n1"
        assert req.title == "Python"
        assert req.type == "subtopic"

    def test_custom_type(self):
        req = GenerateLessonRequest(node_id="n1", title="T", type="central")
        assert req.type == "central"

    def test_topic_type(self):
        req = GenerateLessonRequest(node_id="n1", title="T", type="topic")
        assert req.type == "topic"

    def test_empty_node_id_fails(self):
        with pytest.raises(ValidationError):
            GenerateLessonRequest(node_id="", title="T")

    def test_empty_title_fails(self):
        with pytest.raises(ValidationError):
            GenerateLessonRequest(node_id="n1", title="")

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            GenerateLessonRequest()

    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            GenerateLessonRequest(node_id="n1", title="T", type="invalid")


class TestGenerateLessonResponse:
    """Tests for GenerateLessonResponse model."""

    def test_valid_response(self):
        resp = GenerateLessonResponse(status="success", node_id="n1")
        assert resp.status == "success"
        assert resp.node_id == "n1"


class TestGenerateQuizRequest:
    """Tests for GenerateQuizRequest model."""

    def test_valid_request(self):
        req = GenerateQuizRequest(node_id="n1", title="Python")
        assert req.node_id == "n1"
        assert req.title == "Python"

    def test_empty_fields_fail(self):
        with pytest.raises(ValidationError):
            GenerateQuizRequest(node_id="", title="T")
        with pytest.raises(ValidationError):
            GenerateQuizRequest(node_id="n1", title="")


class TestGenerateQuizResponse:
    """Tests for GenerateQuizResponse model."""

    def test_with_quiz(self):
        quiz = [{"question": "Q1", "options": ["A", "B"], "answer": 0}]
        resp = GenerateQuizResponse(status="success", quiz=quiz)
        assert resp.status == "success"
        assert len(resp.quiz) == 1

    def test_with_message(self):
        resp = GenerateQuizResponse(status="error", message="fail")
        assert resp.message == "fail"
        assert resp.quiz is None


class TestEvaluateQuizRequest:
    """Tests for EvaluateQuizRequest model."""

    def test_valid_request(self):
        quiz_data = [{"question": "Q", "options": ["A", "B"], "answer": 0}]
        req = EvaluateQuizRequest(
            node_id="n1",
            title="T",
            quiz_data=quiz_data,
            user_answers={"0": 0},
        )
        assert req.node_id == "n1"
        assert len(req.quiz_data) == 1

    def test_empty_quiz_data_fails(self):
        with pytest.raises(ValidationError):
            EvaluateQuizRequest(
                node_id="n1",
                title="T",
                quiz_data=[],
                user_answers={},
            )


class TestEvaluateQuizResponse:
    """Tests for EvaluateQuizResponse model."""

    def test_valid_response(self):
        resp = EvaluateQuizResponse(
            status="success",
            evaluation={"score": 80},
        )
        assert resp.status == "success"
        assert resp.evaluation["score"] == 80

    def test_error_response(self):
        resp = EvaluateQuizResponse(status="error", message="fail")
        assert resp.evaluation is None


class TestCreateRoadmapRequest:
    """Tests for CreateRoadmapRequest model."""

    def test_valid_request(self):
        req = CreateRoadmapRequest(tema="Python")
        assert req.tema == "Python"

    def test_empty_tema_fails(self):
        with pytest.raises(ValidationError):
            CreateRoadmapRequest(tema="")


class TestCreateRoadmapResponse:
    """Tests for CreateRoadmapResponse model."""

    def test_valid_response(self):
        resp = CreateRoadmapResponse(status="success", tema="Python", data={"nodes": []})
        assert resp.tema == "Python"
        assert resp.data == {"nodes": []}

    def test_minimal_response(self):
        resp = CreateRoadmapResponse(status="error")
        assert resp.tema is None
        assert resp.data is None


class TestDiagnoseRequest:
    """Tests for DiagnoseRequest model."""

    def test_valid_request(self):
        req = DiagnoseRequest(topic="Python", user_answer="Resposta")
        assert req.topic == "Python"
        assert req.user_answer == "Resposta"

    def test_empty_fields_fail(self):
        with pytest.raises(ValidationError):
            DiagnoseRequest(topic="", user_answer="R")
        with pytest.raises(ValidationError):
            DiagnoseRequest(topic="T", user_answer="")


class TestDiagnoseResponse:
    """Tests for DiagnoseResponse model."""

    def test_valid_response(self):
        resp = DiagnoseResponse(status="success", result={"score": 90})
        assert resp.result["score"] == 90

    def test_minimal_response(self):
        resp = DiagnoseResponse(status="error")
        assert resp.result is None


class TestModelsInit:
    """Tests for models __init__ exports."""

    def test_all_exports_exist(self):
        from backend.models import __all__

        expected = [
            "GenerateLessonRequest",
            "GenerateLessonResponse",
            "GenerateQuizRequest",
            "GenerateQuizResponse",
            "EvaluateQuizRequest",
            "EvaluateQuizResponse",
            "CreateRoadmapRequest",
            "CreateRoadmapResponse",
            "DiagnoseRequest",
            "DiagnoseResponse",
        ]
        for name in expected:
            assert name in __all__
