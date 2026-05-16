"""Modelos Pydantic para o endpoint de geração de lições."""

from pydantic import BaseModel, Field
from typing import Literal


class GenerateLessonRequest(BaseModel):
    """Requisição para gerar uma lição sobre um tópico."""

    node_id: str = Field(..., min_length=1, description="ID único do nó")
    title: str = Field(..., min_length=1, description="Título do tópico")
    type: Literal["topic", "subtopic", "central"] = Field(
        default="subtopic", description="Tipo do nó"
    )


class GenerateLessonResponse(BaseModel):
    """Resposta da geração de lição."""

    status: str
    node_id: str
