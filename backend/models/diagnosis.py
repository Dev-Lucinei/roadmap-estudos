"""Modelos Pydantic para o endpoint de diagnóstico."""

from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    """Requisição de diagnóstico de conhecimento."""

    topic: str = Field(..., min_length=1, description="Tópico a diagnosticar")
    user_answer: str = Field(..., min_length=1, description="Resposta do usuário")


class DiagnoseResponse(BaseModel):
    """Resposta do diagnóstico de conhecimento."""

    status: str
    result: dict | None = None
