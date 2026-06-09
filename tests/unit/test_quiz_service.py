"""Tests for QuizService."""

import json
import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from backend.services.quiz.quiz_service import QuizService


@pytest.fixture
def quiz_service():
    """Create a QuizService with temp directory."""
    tmp = tempfile.mkdtemp()
    svc = QuizService(licoes_dir=tmp)
    yield svc
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def lesson_file(quiz_service):
    """Create a lesson file for testing."""
    content = """# Python Basics

## Conteudo

Variaveis armazenam dados.

```json
[
  {"question": "Q1?", "options": ["A", "B"], "answer": 0}
]
```
"""
    path = os.path.join(str(quiz_service.licoes_dir), "test-node.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


class TestGenerateQuiz:
    """Tests for generate_quiz method."""

    def test_lesson_not_found(self, quiz_service):
        with pytest.raises(FileNotFoundError, match="não encontrada"):
            quiz_service.generate_quiz("nonexistent", "T")

    def test_successful_generation(self, quiz_service, lesson_file, mock_openai_client):
        quiz_json = json.dumps(
            [
                {
                    "question": "Q1?",
                    "options": ["A", "B", "C", "D"],
                    "answer": 0,
                    "explanation": "Because",
                },
                {
                    "question": "Q2?",
                    "options": ["A", "B", "C", "D"],
                    "answer": 1,
                },
                {
                    "question": "Q3?",
                    "options": ["A", "B", "C", "D"],
                    "answer": 2,
                },
            ]
        )
        mock_client = mock_openai_client(quiz_json)

        with patch.object(quiz_service, "get_client", return_value=mock_client):
            result = quiz_service.generate_quiz("test-node", "Python")
            assert len(result) == 3
            assert result[0]["question"] == "Q1?"

    def test_invalid_json_response(self, quiz_service, lesson_file, mock_openai_client):
        mock_client = mock_openai_client("not json")

        with patch.object(quiz_service, "get_client", return_value=mock_client):
            with pytest.raises(ValueError, match="JSON válido"):
                quiz_service.generate_quiz("test-node", "Python")

    def test_too_few_questions(self, quiz_service, lesson_file, mock_openai_client):
        quiz_json = json.dumps(
            [
                {
                    "question": "Q1?",
                    "options": ["A", "B"],
                    "answer": 0,
                }
            ]
        )
        mock_client = mock_openai_client(quiz_json)

        with patch.object(quiz_service, "get_client", return_value=mock_client):
            with pytest.raises(ValueError, match="pelo menos 3"):
                quiz_service.generate_quiz("test-node", "Python")


class TestEvaluateQuiz:
    """Tests for evaluate_quiz method."""

    def test_successful_evaluation(self, quiz_service, lesson_file, mock_openai_client):
        eval_json = json.dumps(
            {
                "score": 80,
                "passed": True,
                "feedback": "Good job",
                "details": [],
            }
        )
        mock_client = mock_openai_client(eval_json)

        quiz_data = [
            {
                "question": "Q1?",
                "options": ["A", "B", "C", "D"],
                "answer": 0,
                "explanation": "Because",
            }
        ]

        with patch.object(quiz_service, "get_client", return_value=mock_client):
            result = quiz_service.evaluate_quiz(
                "test-node",
                "Python",
                quiz_data,
                {"0": 0},
            )
            assert result["score"] == 80
            assert result["passed"] is True

    def test_evaluation_without_lesson(self, quiz_service, mock_openai_client):
        eval_json = json.dumps({"score": 50, "passed": False, "feedback": "ok"})
        mock_client = mock_openai_client(eval_json)

        quiz_data = [
            {
                "question": "Q1?",
                "options": ["A", "B"],
                "answer": 0,
            }
        ]

        with patch.object(quiz_service, "get_client", return_value=mock_client):
            result = quiz_service.evaluate_quiz(
                "nonexistent",
                "T",
                quiz_data,
                {"0": 0},
            )
            assert result["score"] == 50

    def test_evaluation_skips_unanswered(self, quiz_service, lesson_file, mock_openai_client):
        eval_json = json.dumps({"score": 0, "passed": False, "feedback": "none"})
        mock_client = mock_openai_client(eval_json)

        quiz_data = [
            {
                "question": "Q1?",
                "options": ["A", "B"],
                "answer": 0,
            },
            {
                "question": "Q2?",
                "options": ["C", "D"],
                "answer": 1,
            },
        ]

        with patch.object(quiz_service, "get_client", return_value=mock_client):
            result = quiz_service.evaluate_quiz(
                "test-node",
                "Python",
                quiz_data,
                {"0": 0},
            )
            assert "score" in result

    def test_evaluation_invalid_json(self, quiz_service, lesson_file, mock_openai_client):
        mock_client = mock_openai_client("not json")

        quiz_data = [
            {
                "question": "Q1?",
                "options": ["A", "B"],
                "answer": 0,
            }
        ]

        with patch.object(quiz_service, "get_client", return_value=mock_client):
            with pytest.raises(ValueError, match="JSON válido"):
                quiz_service.evaluate_quiz(
                    "test-node",
                    "Python",
                    quiz_data,
                    {"0": 0},
                )

    def test_evaluation_empty_lesson_content(self, quiz_service, mock_openai_client):
        path = os.path.join(str(quiz_service.licoes_dir), "empty.md")
        with open(path, "w") as f:
            f.write("Simple content without json")

        eval_json = json.dumps({"score": 100, "passed": True, "feedback": "Great"})
        mock_client = mock_openai_client(eval_json)

        quiz_data = [
            {
                "question": "Q?",
                "options": ["A", "B"],
                "answer": 0,
            }
        ]

        with patch.object(quiz_service, "get_client", return_value=mock_client):
            result = quiz_service.evaluate_quiz(
                "empty",
                "T",
                quiz_data,
                {"0": 0},
            )
            assert result["score"] == 100
