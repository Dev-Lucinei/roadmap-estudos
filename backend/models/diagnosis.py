from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Tópico a diagnosticar")
    user_answer: str = Field(..., min_length=1, description="Resposta do usuário")


class DiagnoseResponse(BaseModel):
    status: str
    result: dict | None = None
