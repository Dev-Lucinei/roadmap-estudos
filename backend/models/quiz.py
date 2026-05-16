"""Modelos Pydantic para o sistema de quizzes."""

from pydantic import BaseModel, Field
from typing import Any


class GenerateQuizRequest(BaseModel):
    """Requisição para gerar um quiz."""

    node_id: str = Field(..., min_length=1, description="ID do nó")
    title: str = Field(..., min_length=1, description="Título da lição")


class GenerateQuizResponse(BaseModel):
    """Resposta da geração de quiz."""

    status: str
    quiz: list[dict[str, Any]] | None = None
    message: str | None = None


class EvaluateQuizRequest(BaseModel):
    """Requisição para avaliar respostas de um quiz."""

    node_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    quiz_data: list[dict[str, Any]] = Field(..., min_length=1)
    user_answers: dict[str, int] = Field(..., description="Respostas {indice: opcao}")


class EvaluateQuizResponse(BaseModel):
    """Resposta da avaliação de quiz."""

    status: str
    evaluation: dict[str, Any] | None = None
    message: str | None = None
