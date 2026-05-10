"""Tests para generate_roadmap.py."""

import os
import sys
import json
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSalvarRoadmap:
    """Test cases for salvar_roadmap function."""

    def test_salvar_roadmap_new_file(self, temp_data_dir, sample_roadmap):
        """Testa salvar_roadmap criando novo arquivo."""
        with patch("generate_roadmap.BASE_DIR", temp_data_dir):
            from generate_roadmap import salvar_roadmap

            filename = salvar_roadmap("test", sample_roadmap)

            assert os.path.exists(filename)
            assert "roadmap_test.json" in filename

            with open(filename, "r") as f:
                saved_data = json.load(f)
            assert saved_data == sample_roadmap

    def test_salvar_roadmap_existing_file(self, temp_data_dir, sample_roadmap):
        """Testa salvar_roadmap sobrescrevendo arquivo existente."""
        with patch("generate_roadmap.BASE_DIR", temp_data_dir):
            from generate_roadmap import salvar_roadmap

            filepath = salvar_roadmap("test", sample_roadmap)
            assert os.path.exists(filepath)

            new_roadmap = {"title": "Updated", "nodes": []}
            new_filepath = salvar_roadmap("test", new_roadmap)

            assert new_filepath == filepath
            with open(new_filepath, "r") as f:
                saved_data = json.load(f)
            assert saved_data["title"] == "Updated"

    def test_salvar_roadmap_creates_dir(self, temp_data_dir, sample_roadmap):
        """Testa que salvar_roadmap cria diretório se não existir."""
        new_dir = os.path.join(temp_data_dir, "new_data_dir")
        with patch("generate_roadmap.BASE_DIR", new_dir):
            from generate_roadmap import salvar_roadmap

            filepath = salvar_roadmap("test", sample_roadmap)

            assert os.path.exists(new_dir)
            assert os.path.exists(filepath)

    def test_salvar_roadmap_encoding_utf8(self, temp_data_dir):
        """Testa que salvar_roadmap usa encoding UTF-8."""
        with patch("generate_roadmap.BASE_DIR", temp_data_dir):
            from generate_roadmap import salvar_roadmap

            roadmap_with_accents = {
                "title": "Código Português: ããõõ éíüü",
                "nodes": [{"id": "n1", "title": "Tópico: não"}],
            }
            filepath = salvar_roadmap("unicode", roadmap_with_accents)

            with open(filepath, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            assert saved_data["title"] == roadmap_with_accents["title"]

    def test_salvar_roadmap_permission_error(self, temp_data_dir, sample_roadmap):
        """Testa salvar_roadmap com erro de permissão."""
        readonly_dir = os.path.join(temp_data_dir, "readonly")
        os.makedirs(readonly_dir)

        filepath = os.path.join(readonly_dir, "test.json")
        with open(filepath, "w") as f:
            json.dump({}, f)
        os.chmod(readonly_dir, 0o444)

        try:
            with patch("generate_roadmap.BASE_DIR", readonly_dir):
                from generate_roadmap import salvar_roadmap

                with pytest.raises(PermissionError):
                    salvar_roadmap("test", sample_roadmap)
        finally:
            os.chmod(readonly_dir, 0o755)


class TestBaseDir:
    """Test cases for BASE_DIR resolution."""

    def test_base_dir_resolution(self):
        """Testa que BASE_DIR resolve para diretório correto."""
        from generate_roadmap import BASE_DIR

        assert os.path.exists(BASE_DIR)
        assert os.path.isdir(BASE_DIR)
        assert "roadmap-estudos" in BASE_DIR


class TestGerarRoadmapIA:
    """Test cases for gerar_roadmap_ia function."""

    def test_gerar_roadmap_success(self, sample_roadmap):
        """Testa gerar_roadmap_ia com resposta válida da IA."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [
                    Mock(message=Mock(content=json.dumps(sample_roadmap)))
                ]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_roadmap import gerar_roadmap_ia

                result = gerar_roadmap_ia("Python")

                assert result is not None
                assert result["title"] == sample_roadmap["title"]

    def test_gerar_roadmap_invalid_json(self):
        """Testa gerar_roadmap_ia com JSON inválido na resposta."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [
                    Mock(message=Mock(content="Não é JSON válido"))
                ]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_roadmap import gerar_roadmap_ia

                result = gerar_roadmap_ia("Python")

                assert result is None

    def test_gerar_roadmap_no_json_in_response(self):
        """Testa gerar_roadmap_ia quando não há JSON na resposta."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content="Texto sem JSON"))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_roadmap import gerar_roadmap_ia

                result = gerar_roadmap_ia("Python")

                assert result is None

    def test_gerar_roadmap_empty_response(self):
        """Testa gerar_roadmap_ia com resposta vazia."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content=""))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_roadmap import gerar_roadmap_ia

                result = gerar_roadmap_ia("Python")

                assert result is None

    def test_gerar_roadmap_with_json_wrapped_in_text(self, sample_roadmap):
        """Testa gerar_roadmap_ia com JSON dentro de texto."""
        json_str = json.dumps(sample_roadmap)
        response_text = f"Aqui está seu roadmap:\n{json_str}\n\nFim do roadmap."

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            with patch("openai.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content=response_text))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from generate_roadmap import gerar_roadmap_ia

                result = gerar_roadmap_ia("Python")

                assert result is not None
                assert result["title"] == sample_roadmap["title"]


if __name__ == "__main__":
    import unittest

    unittest.main()
