"""Modelos Pydantic para validação de dados da API."""

from .diagnosis import DiagnoseRequest, DiagnoseResponse
from .lesson import GenerateLessonRequest, GenerateLessonResponse
from .quiz import (
    EvaluateQuizRequest,
    EvaluateQuizResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
)
from .roadmap import CreateRoadmapRequest, CreateRoadmapResponse

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
