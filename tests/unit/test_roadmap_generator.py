"""Tests for roadmap_generator service."""

import json
import os
from unittest.mock import patch

import pytest

from backend.services.ai_content.roadmap_generator import (
    gerar_roadmap_ia,
    get_client,
    salvar_roadmap,
)


class TestGetClient:
    """Tests for get_client function."""

    def test_import_error(self):
        with patch(
            "backend.services.ai_content.roadmap_generator.OpenAI",
            None,
        ):
            with pytest.raises(ImportError, match="not installed"):
                get_client()

    def test_missing_api_key(self):
        with patch("backend.core.config.get_api_key", return_value=None):
            with patch("backend.services.ai_content.roadmap_generator.OpenAI"):
                with pytest.raises(PermissionError):
                    get_client()

    def test_valid_client(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "key"}):
            with patch("backend.services.ai_content.roadmap_generator.OpenAI") as mock_cls:
                get_client()
                mock_cls.assert_called_once()


class TestGerarRoadmapIa:
    """Tests for gerar_roadmap_ia function."""

    def test_successful_generation(self, mock_openai_client):
        roadmap_json = json.dumps(
            {
                "title": "Python",
                "nodes": [
                    {
                        "id": "n1",
                        "title": "Basics",
                        "type": "central",
                        "group": "G",
                    }
                ],
            }
        )
        mock_client = mock_openai_client(roadmap_json)

        with patch(
            "backend.services.ai_content.roadmap_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_roadmap_ia("Python")
            assert result is not None
            assert result["title"] == "Python"

    def test_none_content(self, mock_openai_client):
        mock_client = mock_openai_client(None)

        with patch(
            "backend.services.ai_content.roadmap_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_roadmap_ia("Python")
            assert result is None

    def test_invalid_json(self, mock_openai_client):
        mock_client = mock_openai_client("not json at all")

        with patch(
            "backend.services.ai_content.roadmap_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_roadmap_ia("Python")
            assert result is None

    def test_no_nodes_in_json(self, mock_openai_client):
        mock_client = mock_openai_client(json.dumps({"title": "No nodes"}))

        with patch(
            "backend.services.ai_content.roadmap_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_roadmap_ia("Python")
            assert result is None

    def test_json_with_markdown_blocks(self, mock_openai_client):
        roadmap = {
            "title": "Test",
            "nodes": [{"id": "n1", "title": "T"}],
        }
        content = f"```json\n{json.dumps(roadmap)}\n```"
        mock_client = mock_openai_client(content)

        with patch(
            "backend.services.ai_content.roadmap_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_roadmap_ia("Test")
            assert result is not None


class TestSalvarRoadmap:
    """Tests for salvar_roadmap function."""

    def test_save_basic(self, tmp_path):
        with patch(
            "backend.services.ai_content.roadmap_generator.DATA_DIR",
            str(tmp_path),
        ):
            data = {"title": "Test", "nodes": []}
            result = salvar_roadmap("Python Basics", data)
            assert os.path.exists(result)
            with open(result) as f:
                loaded = json.load(f)
            assert loaded["title"] == "Test"

    def test_save_creates_dir(self, tmp_path):
        new_dir = str(tmp_path / "newdir")
        with patch(
            "backend.services.ai_content.roadmap_generator.DATA_DIR",
            new_dir,
        ):
            data = {"title": "T", "nodes": []}
            result = salvar_roadmap("Test", data)
            assert os.path.exists(new_dir)
            assert os.path.exists(result)

    def test_save_normalizes_name(self, tmp_path):
        with patch(
            "backend.services.ai_content.roadmap_generator.DATA_DIR",
            str(tmp_path),
        ):
            data = {"title": "T", "nodes": []}
            result = salvar_roadmap("Python Fundamentos!", data)
            filename = os.path.basename(result)
            assert "!" not in filename

    def test_save_accented_name(self, tmp_path):
        with patch(
            "backend.services.ai_content.roadmap_generator.DATA_DIR",
            str(tmp_path),
        ):
            data = {"title": "T", "nodes": []}
            result = salvar_roadmap("Programação Web", data)
            assert os.path.exists(result)
