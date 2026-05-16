"""Modelos Pydantic para validação de dados da API."""

from .lesson import GenerateLessonRequest, GenerateLessonResponse
from .quiz import (
    GenerateQuizRequest,
    GenerateQuizResponse,
    EvaluateQuizRequest,
    EvaluateQuizResponse,
)
from .roadmap import CreateRoadmapRequest, CreateRoadmapResponse
from .diagnosis import DiagnoseRequest, DiagnoseResponse

__all__ = [
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
