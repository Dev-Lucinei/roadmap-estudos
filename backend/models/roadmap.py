"""Modelos Pydantic para o endpoint de roadmaps."""

from typing import Any

from pydantic import BaseModel, Field


class CreateRoadmapRequest(BaseModel):
    """Requisição para criar um novo roadmap."""

    tema: str = Field(..., min_length=1, description="Tema do roadmap")


class CreateRoadmapResponse(BaseModel):
    """Resposta da criação de roadmap."""

    status: str
    tema: str | None = None
    data: dict[str, Any] | None = None
