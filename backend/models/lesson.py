"""Modelos Pydantic para o endpoint de geração de lições."""

from typing import Literal

from pydantic import BaseModel, Field


class GenerateLessonRequest(BaseModel):
    """Requisição para gerar uma lição sobre um tópico."""

    node_id: str = Field(..., min_length=1, description="ID único do nó")
    title: str = Field(..., min_length=1, description="Título do tópico")
    type: Literal["topic", "subtopic", "central"] = Field(
        default="subtopic", description="Tipo do nó"
    )
    content: str | None = Field(default=None, description="Descrição/conteúdo do nó no roadmap")
    group: str | None = Field(default=None, description="Seção/grupo do roadmap ao qual pertence")
    difficulty: Literal["easy", "medium", "hard"] | None = Field(
        default=None, description="Nível de dificuldade do tópico"
    )
    roadmap_title: str | None = Field(
        default=None, description="Título da trilha de estudos (roadmap)"
    )
    subtopics: list[str] | None = Field(
        default=None, description="Títulos dos subtópicos relacionados"
    )


class GenerateLessonResponse(BaseModel):
    """Resposta da geração de lição."""

    status: str
    node_id: str
