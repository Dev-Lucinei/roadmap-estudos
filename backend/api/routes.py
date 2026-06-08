"""Rotas legado do servidor http.server (mantido para compatibilidade)."""

import json
import os

from backend.core.config import DATA_DIR
from backend.services.ai_content.lesson_generator import processar_node
from backend.services.ai_content.roadmap_generator import (
    gerar_roadmap_ia,
    salvar_roadmap,
)
from backend.services.diagnosis.diagnosis_service import DiagnosisService
from backend.services.quiz.quiz_service import QuizService

quiz_service = QuizService()
diagnosis_service = DiagnosisService()


class ApiRoutes:
    """Rotas legado do servidor http.server (mantido para compatibilidade)."""

    @staticmethod
    def list_roadmaps() -> list[str]:
        """Lista todos os roadmaps disponíveis no diretório de dados."""
        roadmaps = []
        if os.path.exists(DATA_DIR):
            for f in os.listdir(DATA_DIR):
                if f.startswith("roadmap_") and f.endswith(".json"):
                    roadmaps.append(f.replace("roadmap_", "").replace(".json", ""))
        return roadmaps

    @staticmethod
    def load_roadmap(roadmap_id: str) -> dict[str, object] | None:
        """Carrega um roadmap pelo ID."""
        path = os.path.join(DATA_DIR, f"roadmap_{roadmap_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                result: dict[str, object] = json.load(f)
                return result
        return None

    @staticmethod
    def get_dep_map() -> dict[str, list[str]]:
        """Retorna o mapa de dependências entre tópicos."""
        path = os.path.join(DATA_DIR, "dep_map.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                result: dict[str, list[str]] = json.load(f)
                return result
        return {}

    @staticmethod
    def generate_lesson(data: dict[str, str]) -> dict[str, str] | None:
        """Gera uma lição para o nó especificado."""
        node_id = data.get("node_id")
        title = data.get("title")
        node_type = data.get("type", "subtopic")
        if node_id and title:
            processar_node(node_id, title, node_type)
            return {"status": "success", "node_id": node_id}
        return None

    @staticmethod
    def create_roadmap(data: dict[str, str]) -> dict[str, object] | None:
        """Cria um novo roadmap com base no tema fornecido."""
        tema = data.get("tema")
        if tema:
            roadmap_data = gerar_roadmap_ia(tema)
            if roadmap_data:
                salvar_roadmap(tema, roadmap_data)
                return {"status": "success", "tema": tema, "data": roadmap_data}
        return None

    @staticmethod
    def handle_quiz_generate(data: dict[str, str]) -> dict[str, str | list[dict[str, object]]]:
        """Gera um quiz para a lição especificada."""
        node_id = data.get("node_id")
        title = data.get("title")
        if node_id and title:
            try:
                quiz_data = quiz_service.generate_quiz(node_id, title)
                return {"status": "success", "quiz": quiz_data}
            except FileNotFoundError as e:
                return {"status": "error", "message": f"Lição não encontrada: {str(e)}"}
            except Exception as e:
                return {"status": "error", "message": f"Erro ao gerar quiz: {str(e)}"}
        return {
            "status": "error",
            "message": "Parâmetros inválidos: node_id e title são obrigatórios",
        }

    @staticmethod
    def handle_quiz_evaluate(data: dict[str, object]) -> dict[str, str | object]:
        """Avalia as respostas de um quiz."""
        node_id = data.get("node_id")
        title = data.get("title")
        quiz_data = data.get("quiz_data")
        user_answers = data.get("user_answers")
        if (
            isinstance(node_id, str)
            and isinstance(title, str)
            and isinstance(quiz_data, list)
            and isinstance(user_answers, dict)
        ):
            try:
                evaluation = quiz_service.evaluate_quiz(node_id, title, quiz_data, user_answers)
                return {"status": "success", "evaluation": evaluation}
            except Exception as e:
                return {"status": "error", "message": f"Erro ao avaliar quiz: {str(e)}"}
        return {"status": "error", "message": "Parâmetros inválidos"}

    @staticmethod
    def handle_diagnose(data: dict[str, str]) -> dict[str, object] | None:
        """Realiza diagnóstico de conhecimento."""
        topic = data.get("topic")
        user_answer = data.get("user_answer")
        if topic and user_answer:
            return diagnosis_service.diagnose(topic, user_answer)
        return None
