from pydantic import BaseModel, Field


class CreateRoadmapRequest(BaseModel):
    tema: str = Field(..., min_length=1, description="Tema do roadmap")


class CreateRoadmapResponse(BaseModel):
    status: str
    tema: str | None = None
    data: dict | None = None