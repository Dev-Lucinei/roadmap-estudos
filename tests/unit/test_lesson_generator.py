"""Tests for lesson_generator service."""

import os
from unittest.mock import Mock, patch

import pytest

from backend.services.ai_content.lesson_generator import (
    gerar_conteudo_ia,
    get_client,
    processar_node,
)


class TestGetClient:
    """Tests for get_client function."""

    def test_missing_api_key(self):
        with patch(
            "backend.services.ai_content.lesson_generator.get_api_key",
            return_value=None,
        ):
            with pytest.raises(PermissionError, match="não configurada"):
                get_client()

    def test_valid_key(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("backend.services.ai_content.lesson_generator.OpenAI") as mock_cls:
                get_client()
                mock_cls.assert_called_once()


class TestGerarConteudoIa:
    """Tests for gerar_conteudo_ia function."""

    def test_successful_generation(self):
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="# Lição\nConteúdo"))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch(
            "backend.services.ai_content.lesson_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_conteudo_ia(tema="Python", tipo="subtopic")
            assert result == "# Lição\nConteúdo"

    def test_none_content(self):
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=None))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch(
            "backend.services.ai_content.lesson_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_conteudo_ia(tema="Python")
            assert result is None

    def test_empty_content(self):
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="   "))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch(
            "backend.services.ai_content.lesson_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_conteudo_ia(tema="Python")
            assert result == ""

    def test_with_full_context(self):
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="# Lição"))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch(
            "backend.services.ai_content.lesson_generator.get_client",
            return_value=mock_client,
        ):
            result = gerar_conteudo_ia(
                tema="Classes e Objetos",
                tipo="subtopic",
                content="Definição de classes e instanciamento de objetos",
                group="Fundamentos POO",
                difficulty="easy",
                roadmap_title="Programação Orientada a Objetos em Python",
                subtopics=["Herança", "Polimorfismo"],
            )
            assert result == "# Lição"
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args.kwargs.get("messages") or call_args[1]["messages"]
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert "Arquiteto Pedagógico" in messages[0]["content"]
            assert "Fundamentos POO" in messages[1]["content"]


class TestProcessarNode:
    """Tests for processar_node function."""

    def test_successful_processing(self, tmp_path):
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="# Lesson"))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch(
            "backend.services.ai_content.lesson_generator.get_client",
            return_value=mock_client,
        ):
            result = processar_node(
                "n1",
                "Python",
                "subtopic",
                output_dir=str(tmp_path),
            )
            assert os.path.exists(result)
            with open(result) as f:
                assert f.read() == "# Lesson"

    def test_creates_output_dir(self, tmp_path):
        output_dir = str(tmp_path / "subdir")
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="# Content"))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch(
            "backend.services.ai_content.lesson_generator.get_client",
            return_value=mock_client,
        ):
            result = processar_node("n1", "T", "topic", output_dir=output_dir)
            assert os.path.exists(output_dir)
            assert os.path.exists(result)

    def test_raises_on_empty_content(self, tmp_path):
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=None))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch(
            "backend.services.ai_content.lesson_generator.get_client",
            return_value=mock_client,
        ):
            with pytest.raises(ValueError, match="Falha"):
                processar_node(
                    "n1",
                    "T",
                    "topic",
                    output_dir=str(tmp_path),
                )

    def test_passes_context_to_gerar_conteudo_ia(self, tmp_path):
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="# Lesson"))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch(
            "backend.services.ai_content.lesson_generator.get_client",
            return_value=mock_client,
        ):
            processar_node(
                "n1",
                "Classes e Objetos",
                "subtopic",
                output_dir=str(tmp_path),
                content="Definição de classes",
                group="Fundamentos POO",
                difficulty="easy",
                roadmap_title="POO em Python",
                subtopics=["Herança"],
            )
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args.kwargs.get("messages") or call_args[1]["messages"]
            user_prompt = messages[1]["content"]
            assert "Fundamentos POO" in user_prompt
            assert "POO em Python" in user_prompt
