"""Rotas FastAPI do Roadmap-Estudos (APIRouter)."""

import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.core.config import LICOES_DIR
from backend.models import (
    CreateRoadmapRequest,
    CreateRoadmapResponse,
    DiagnoseRequest,
    DiagnoseResponse,
    EvaluateQuizRequest,
    EvaluateQuizResponse,
    GenerateLessonRequest,
    GenerateLessonResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
)
from backend.services.ai_content.lesson_generator import processar_node
from backend.services.ai_content.roadmap_generator import (
    gerar_roadmap_ia,
    salvar_roadmap,
)
from backend.services.diagnosis.diagnosis_service import DiagnosisService
from backend.services.quiz.quiz_service import QuizService

router = APIRouter()
quiz_service = QuizService()
diagnosis_service = DiagnosisService()


@router.get("/api/roadmaps")
async def list_roadmaps() -> list[str]:
    """Lista todos os roadmaps disponíveis."""
    import os

    from backend.core.config import DATA_DIR

    roadmaps = []
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.startswith("roadmap_") and f.endswith(".json"):
                roadmaps.append(f.replace("roadmap_", "").replace(".json", ""))
    return roadmaps


@router.get("/api/roadmap/{roadmap_id}")
async def load_roadmap(roadmap_id: str) -> dict[str, object]:
    """Carrega um roadmap pelo ID."""
    import json
    import os

    from backend.core.config import DATA_DIR

    if not re.fullmatch(r"[a-z0-9_-]+", roadmap_id):
        raise HTTPException(status_code=400, detail="ID de roadmap inválido")

    path = os.path.join(DATA_DIR, f"roadmap_{roadmap_id}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            result: dict[str, object] = json.load(f)
            return result
    raise HTTPException(status_code=404, detail="Roadmap não encontrado")


@router.get("/api/dep-map")
async def get_dep_map() -> dict[str, list[str]]:
    """Retorna o mapa de dependências entre tópicos."""
    import json
    import os

    from backend.core.config import DATA_DIR

    path = os.path.join(DATA_DIR, "dep_map.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            result: dict[str, list[str]] = json.load(f)
            return result
    return {}


@router.post("/api/generate-lesson", response_model=GenerateLessonResponse)
async def generate_lesson(req: GenerateLessonRequest) -> GenerateLessonResponse:
    """Gera uma lição para o nó especificado."""
    processar_node(req.node_id, req.title, req.type)
    return GenerateLessonResponse(status="success", node_id=req.node_id)


@router.post("/api/generate-roadmap", response_model=CreateRoadmapResponse)
async def create_roadmap(req: CreateRoadmapRequest) -> CreateRoadmapResponse:
    """Cria um novo roadmap via IA."""
    roadmap_data = gerar_roadmap_ia(req.tema)
    if not roadmap_data:
        raise HTTPException(status_code=500, detail="Erro ao gerar roadmap")
    salvar_roadmap(req.tema, roadmap_data)
    return CreateRoadmapResponse(status="success", tema=req.tema, data=roadmap_data)


@router.post("/api/quiz/generate", response_model=GenerateQuizResponse)
async def generate_quiz(req: GenerateQuizRequest) -> GenerateQuizResponse:
    """Gera um quiz baseado no conteúdo da lição."""
    try:
        quiz_data = quiz_service.generate_quiz(req.node_id, req.title)
        return GenerateQuizResponse(status="success", quiz=quiz_data)
    except FileNotFoundError as e:
        return GenerateQuizResponse(status="error", message=f"Arquivo não encontrado: {e}")
    except ValueError as e:
        return GenerateQuizResponse(status="error", message=f"Dados inválidos: {e}")


@router.post("/api/quiz/evaluate", response_model=EvaluateQuizResponse)
async def evaluate_quiz(req: EvaluateQuizRequest) -> EvaluateQuizResponse:
    """Avalia as respostas do usuário para um quiz."""
    try:
        evaluation = quiz_service.evaluate_quiz(
            req.node_id, req.title, req.quiz_data, req.user_answers
        )
        return EvaluateQuizResponse(status="success", evaluation=evaluation)
    except FileNotFoundError as e:
        return EvaluateQuizResponse(status="error", message=f"Arquivo não encontrado: {e}")
    except ValueError as e:
        return EvaluateQuizResponse(status="error", message=f"Dados inválidos: {e}")


@router.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(req: DiagnoseRequest) -> DiagnoseResponse:
    """Realiza diagnóstico de conhecimento sobre um tópico."""
    result = diagnosis_service.diagnose(req.topic, req.user_answer)
    return DiagnoseResponse(status="success", result=result)


@router.get("/licoes/{lesson_file:path}")
async def get_lesson(lesson_file: str) -> FileResponse:
    """Retorna o arquivo Markdown de uma lição."""
    lesson_path = (LICOES_DIR / lesson_file).resolve()
    if not lesson_path.is_relative_to(LICOES_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Acesso negado: path traversal detectado")
    if lesson_path.exists() and lesson_path.is_file():
        return FileResponse(lesson_path, media_type="text/markdown; charset=utf-8")
    raise HTTPException(status_code=404, detail=f"Lição não encontrada: {lesson_file}")
