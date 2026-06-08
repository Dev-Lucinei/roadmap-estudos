"""Configurações centrais do Roadmap-Estudos."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
LICOES_DIR = BASE_DIR / "licoes"
FRONTEND_DIR = BASE_DIR / "frontend" / "public"


class Settings(BaseSettings):
    """Configurações carregadas do ambiente."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_API_KEY: str | None = None


settings = Settings()

OPENROUTER_BASE_URL = settings.OPENROUTER_BASE_URL
OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY


def get_api_key() -> str | None:
    """Retorna a API key atual do ambiente."""
    return settings.OPENROUTER_API_KEY


def check_api_key() -> None:
    """Verifica se a API key está configurada no ambiente atual."""
    if not get_api_key():
        raise PermissionError("API key não configurada")
