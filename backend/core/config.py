"""Configurações centrais do Roadmap-Estudos."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
LICOES_DIR = BASE_DIR / "licoes"
FRONTEND_DIR = BASE_DIR / "frontend" / "public"

env_path = BASE_DIR / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")


def get_api_key() -> str | None:
    """Retorna a API key atual do ambiente."""
    return os.getenv("OPENROUTER_API_KEY")


def check_api_key() -> None:
    """Verifica se a API key está configurada no ambiente atual."""
    if not get_api_key():
        raise PermissionError("API key não configurada")
