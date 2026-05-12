import json
import os
from backend.core.config import DATA_DIR
from backend.services.ai_content.lesson_generator import processar_node
from backend.services.ai_content.roadmap_generator import (
    gerar_roadmap_ia,
    salvar_roadmap,
)
from backend.services.quiz.quiz_service import QuizService
from backend.services.diagnosis.diagnosis_service import DiagnosisService

quiz_service = QuizService()
diagnosis_service = DiagnosisService()


class ApiRoutes:
    @staticmethod
    def list_roadmaps():
        roadmaps = []
        if os.path.exists(DATA_DIR):
            for f in os.listdir(DATA_DIR):
                if f.startswith("roadmap_") and f.endswith(".json"):
                    roadmaps.append(f.replace("roadmap_", "").replace(".json", ""))
        return roadmaps

    @staticmethod
    def load_roadmap(roadmap_id):
        path = os.path.join(DATA_DIR, f"roadmap_{roadmap_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    @staticmethod
    def get_dep_map():
        path = os.path.join(DATA_DIR, "dep_map.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def generate_lesson(data):
        node_id = data.get("node_id")
        title = data.get("title")
        node_type = data.get("type", "subtopic")
        if node_id and title:
            processar_node(node_id, title, node_type)
            return {"status": "success", "node_id": node_id}
        return None

    @staticmethod
    def create_roadmap(data):
        tema = data.get("tema")
        if tema:
            roadmap_data = gerar_roadmap_ia(tema)
            if roadmap_data:
                salvar_roadmap(tema, roadmap_data)
                return {"status": "success", "tema": tema, "data": roadmap_data}
        return None

    @staticmethod
    def handle_quiz_generate(data):
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
    def handle_quiz_evaluate(data):
        node_id = data.get("node_id")
        title = data.get("title")
        quiz_data = data.get("quiz_data")
        user_answers = data.get("user_answers")
        if all([node_id, title, quiz_data, user_answers]):
            try:
                evaluation = quiz_service.evaluate_quiz(
                    node_id, title, quiz_data, user_answers
                )
                return {"status": "success", "evaluation": evaluation}
            except Exception as e:
                return {"status": "error", "message": f"Erro ao avaliar quiz: {str(e)}"}
        return {"status": "error", "message": "Parâmetros inválidos"}

    @staticmethod
    def handle_diagnose(data):
        topic = data.get("topic")
        user_answer = data.get("user_answer")
        if topic and user_answer:
            return diagnosis_service.diagnose(topic, user_answer)
        return None
