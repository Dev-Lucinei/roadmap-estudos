"""Serviço de diagnóstico de gaps de conhecimento via IA."""

import json
import os
from backend.core.config import (
    OPENROUTER_BASE_URL,
    DATA_DIR,
    check_api_key,
    get_api_key,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


class DiagnosisService:
    """Analisa lacunas de conhecimento usando IA e mapa de dependências."""

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir

    def get_client(self) -> "OpenAI":
        """Retorna cliente OpenAI configurado para OpenRouter."""
        check_api_key()
        if OpenAI is None:
            raise ImportError("openai package not installed")
        return OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=get_api_key() or "",
        )

    def diagnose(self, topic: str, user_answer: str) -> dict:
        """Diagnostica o conhecimento do usuário sobre um tópico usando IA."""
        dep_map_path = os.path.join(self.data_dir, "dep_map.json")
        if not os.path.exists(dep_map_path):
            raise FileNotFoundError("Mapa de dependências não encontrado")

        with open(dep_map_path, "r", encoding="utf-8") as f:
            dep_map = json.load(f)

        prerequisites = dep_map.get(topic, [])
        client = self.get_client()

        prompt = f"""
        Analise a seguinte resposta do usuário sobre o tópico "{topic}":
        "{user_answer}"
        
        Pré-requisitos para este tópico: {", ".join(prerequisites) if prerequisites else "Nenhum"}
        
        Forneça um diagnóstico conciso (máximo 100 palavras) que:
        1. Identifique se há lacunas de conhecimento nos pré-requisitos
        2. Se houver lacunas, explique qual pré-requisito está faltando e por que é importante
        3. Se não houver lacunas, confirme que o usuário pode avançar
        4. Inclua uma fórmula/regra relevante e um erro comum
        
        Responda APENAS com o diagnóstico, sem formatação extra.
        """

        completion = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )

        diagnosis = completion.choices[0].message.content.strip()
        words = diagnosis.split()
        if len(words) > 100:
            diagnosis = " ".join(words[:100]) + "..."

        gap_indicators = [
            "falta",
            "não sabe",
            "revisar",
            "precisa",
            "lacuna",
            "não entende",
        ]
        has_gap = any(indicator in diagnosis.lower() for indicator in gap_indicators)

        return {
            "status": "miss" if has_gap else "hit",
            "message": diagnosis,
            "tags": prerequisites,
            "has_gap": has_gap,
        }
