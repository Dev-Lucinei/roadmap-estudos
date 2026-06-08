"""Tests for backend/main.py."""

from unittest.mock import patch

import pytest

from backend.main import app, lifespan


class TestApp:
    """Tests for FastAPI app creation."""

    def test_app_title(self):
        assert app.title == "Roadmap Estudos API"

    def test_app_version(self):
        assert app.version == "1.0.0"

    def test_app_has_routes(self):
        routes = [r.path for r in app.routes]
        assert "/api/roadmaps" in routes

    def test_app_has_cors_middleware(self):
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes


class TestLifespan:
    """Tests for lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_creates_dirs(self, tmp_path):
        with (
            patch("backend.main.DATA_DIR", tmp_path / "data"),
            patch("backend.main.LICOES_DIR", tmp_path / "licoes"),
        ):
            async with lifespan(app):
                assert (tmp_path / "data").exists()
                assert (tmp_path / "licoes").exists()
