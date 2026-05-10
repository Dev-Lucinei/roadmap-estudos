"""Tests para generate_lessons.py."""

import os
import sys
import json
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProcessarNode:
    """Test cases for processar_node function."""

    def test_processar_node_new_file(self, temp_output_dir, sample_lesson_content):
        """Testa processar_node criando novo arquivo."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content=sample_lesson_content))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                with patch("generate_lessons.BASE_DIR", temp_output_dir):
                    from generate_lessons import processar_node

                    filepath = processar_node("variaveis", "Variáveis em Python", "subtopic")

                    assert os.path.exists(filepath)
                    assert "variaveis.md" in filepath

                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    assert "# Variáveis em Python" in content

    def test_processar_node_creates_dir(self, temp_output_dir, sample_lesson_content):
        """Testa que processar_node cria diretório se não existir."""
        new_dir = os.path.join(temp_output_dir, "licoes_novas")

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content=sample_lesson_content))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                with patch("generate_lessons.BASE_DIR", new_dir):
                    from generate_lessons import processar_node

                    filepath = processar_node("node1", "Título", "subtopic")

                    assert os.path.exists(new_dir)
                    assert os.path.exists(filepath)

    def test_processar_node_encoding_utf8(self, temp_output_dir):
        """Testa que processar_node usa encoding UTF-8."""
        lesson_with_accents = "# Tópico: Português\n\nConteúdo com acentos: ããõõ éíüü"

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content=lesson_with_accents))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                with patch("generate_lessons.BASE_DIR", temp_output_dir):
                    from generate_lessons import processar_node

                    filepath = processar_node("unicode", "Tópico Unicode", "subtopic")

                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    assert "ããõõ" in content
                    assert "éíüü" in content

    def test_processar_node_custom_output_dir(self, temp_data_dir):
        """Testa processar_node com diretório de saída customizado."""
        custom_dir = os.path.join(temp_data_dir, "custom_licoes")

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content="# Título"))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_lessons import processar_node

                filepath = processar_node("custom", "Custom", "subtopic", output_dir=custom_dir)

                assert os.path.exists(custom_dir)
                assert os.path.exists(filepath)
                assert custom_dir in filepath


class TestBaseDir:
    """Test cases for BASE_DIR resolution."""

    def test_base_dir_resolution(self):
        """Testa que BASE_DIR resolve para diretório correto."""
        from generate_lessons import BASE_DIR

        assert os.path.exists(BASE_DIR)
        assert os.path.isdir(BASE_DIR)
        assert "roadmap-estudos" in BASE_DIR


class TestGerarConteudoIA:
    """Test cases for gerar_conteudo_ia function."""

    def test_gerar_conteudo_success(self):
        """Testa gerar_conteudo_ia com resposta válida."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content="# Título\n\nConteúdo"))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_lessons import gerar_conteudo_ia

                result = gerar_conteudo_ia("Variáveis", "subtopic")

                assert result is not None
                assert "# Título" in result

    def test_gerar_conteudo_empty_response(self):
        """Testa gerar_conteudo_ia com resposta vazia."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content=""))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_lessons import gerar_conteudo_ia

                result = gerar_conteudo_ia("Variáveis", "subtopic")

                assert result == ""

    def test_gerar_conteudo_long_content(self):
        """Testa gerar_conteudo_ia com conteúdo longo."""
        long_content = "# Variáveis em Python\n\n" + "Conteúdo extenso. " * 500

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content=long_content))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_lessons import gerar_conteudo_ia

                result = gerar_conteudo_ia("Variáveis", "subtopic")

                assert result is not None
                assert len(result) > 1000


if __name__ == "__main__":
    import unittest
    unittest.main()