"""Tests para os endpoints HTTP do server.py."""

import os
import sys
import json
import tempfile
import shutil
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import RoadmapHandler, DATA_DIR, LICOES_DIR


class MockWFile:
    """Mock file object for response body."""

    def __init__(self):
        self.data = b""

    def write(self, data):
        self.data += data


class MockRoadmapHandler(RoadmapHandler):
    """Mock handler for testing without actual HTTP server."""

    def __init__(self, data_dir=None, licoes_dir=None):
        self._test_data_dir = data_dir
        self._test_licoes_dir = licoes_dir
        self._response_code = None
        self._response_headers = {}
        self._wfile = MockWFile()

    def send_response(self, code, message=None):
        self._response_code = code

    def send_header(self, name, value):
        self._response_headers[name] = value

    def end_headers(self):
        pass

    @property
    def wfile(self):
        return self._wfile

    @property
    def client_address(self):
        return ("127.0.0.1", 8000)

    def log_message(self, format, *args):
        pass

    @property
    def data_dir(self):
        return self._test_data_dir or DATA_DIR

    @property
    def licoes_dir(self):
        return self._test_licoes_dir or LICOES_DIR


def create_handler(data_dir):
    """Factory para criar handler com diretório controlado."""
    with patch("server.DATA_DIR", data_dir):
        with patch("server.LICOES_DIR", data_dir):
            return MockRoadmapHandler(data_dir=data_dir)


class TestListRoadmaps:
    """Test GET /api/roadmaps."""

    def test_list_roadmaps_empty_dir(self, temp_data_dir):
        """Testa list_roadmaps com diretório vazio."""
        handler = create_handler(temp_data_dir)
        handler.list_roadmaps()
        assert handler._response_code == 200
        assert json.loads(handler.wfile.data) == []

    def test_list_roadmaps_with_files(self, temp_data_dir):
        """Testa list_roadmaps com arquivos roadmap_*.json."""
        open(os.path.join(temp_data_dir, "roadmap_python.json"), "w").close()
        open(os.path.join(temp_data_dir, "roadmap_devops.json"), "w").close()

        handler = create_handler(temp_data_dir)
        handler.list_roadmaps()
        assert handler._response_code == 200
        files = json.loads(handler.wfile.data)
        assert len(files) == 2
        assert "roadmap_python.json" in files

    def test_list_roadmaps_excludes_dep_map(self, temp_data_dir):
        """Testa que list_roadmaps exclui dep_map.json."""
        open(os.path.join(temp_data_dir, "roadmap_test.json"), "w").close()
        open(os.path.join(temp_data_dir, "dep_map.json"), "w").close()

        handler = create_handler(temp_data_dir)
        handler.list_roadmaps()
        files = json.loads(handler.wfile.data)
        assert "dep_map.json" not in files
        assert "roadmap_test.json" in files

    def test_list_roadmaps_creates_dir_if_not_exists(self, temp_data_dir):
        """Testa que list_roadmaps cria diretório se não existir."""
        new_dir = os.path.join(temp_data_dir, "new_dir")
        handler = create_handler(new_dir)
        handler.list_roadmaps()
        assert os.path.exists(new_dir)


class TestLoadRoadmap:
    """Test GET /api/roadmap/<file>."""

    def test_load_roadmap_success(self, temp_data_dir):
        """Testa load_roadmap com arquivo existente."""
        filepath = os.path.join(temp_data_dir, "test_roadmap.json")
        roadmap_data = {"title": "Test", "nodes": []}
        with open(filepath, "w") as f:
            json.dump(roadmap_data, f)

        handler = create_handler(temp_data_dir)
        handler.path = "/api/roadmap/test_roadmap.json"
        handler.load_roadmap()
        assert handler._response_code == 200
        assert json.loads(handler.wfile.data)["title"] == "Test"

    def test_load_roadmap_not_found(self, temp_data_dir):
        """Testa load_roadmap com arquivo inexistente (404)."""
        handler = create_handler(temp_data_dir)
        handler.path = "/api/roadmap/nonexistent.json"
        handler.load_roadmap()
        assert handler._response_code == 404


class TestDepMap:
    """Test GET /api/dep-map."""

    def test_get_dep_map_success(self, temp_data_dir, sample_dep_map):
        """Testa get_dep_map com arquivo existente."""
        dep_map_path = os.path.join(temp_data_dir, "dep_map.json")
        with open(dep_map_path, "w") as f:
            json.dump(sample_dep_map, f)

        handler = create_handler(temp_data_dir)
        handler.get_dep_map()
        assert handler._response_code == 200
        assert json.loads(handler.wfile.data) == sample_dep_map

    def test_get_dep_map_not_found(self, temp_data_dir):
        """Testa get_dep_map com arquivo inexistente (404)."""
        handler = create_handler(temp_data_dir)
        handler.get_dep_map()
        assert handler._response_code == 404
        result = json.loads(handler.wfile.data)
        assert result["status"] == "error"
        assert "não encontrado" in result["message"]


class TestGenerateLesson:
    """Test POST /api/generate-lesson."""

    def test_generate_lesson_success(self, temp_data_dir):
        """Testa handle_generate_lesson com dados válidos."""
        with patch("server.processar_node") as mock_process:
            mock_process.return_value = os.path.join(temp_data_dir, "node1.md")

            handler = create_handler(temp_data_dir)
            data = {"id": "node1", "title": "Variáveis", "type": "subtopic"}
            handler.path = "/api/generate-lesson"
            handler.handle_generate_lesson(data)

            assert handler._response_code == 200
            result = json.loads(handler.wfile.data)
            assert result["status"] == "success"

    def test_generate_lesson_missing_id(self, temp_data_dir):
        """Testa handle_generate_lesson com dados incompletos."""
        handler = create_handler(temp_data_dir)
        data = {"title": "Variáveis"}
        handler.path = "/api/generate-lesson"
        handler.handle_generate_lesson(data)
        assert handler._response_code == 500

    def test_generate_lesson_error(self, temp_data_dir):
        """Testa handle_generate_lesson com erro."""
        with patch("server.processar_node") as mock_process:
            mock_process.side_effect = Exception("Erro na geração")

            handler = create_handler(temp_data_dir)
            data = {"id": "node1", "title": "Variáveis"}
            handler.path = "/api/generate-lesson"
            handler.handle_generate_lesson(data)

            assert handler._response_code == 500


class TestGenerateRoadmap:
    """Test POST /api/generate-roadmap."""

    def test_generate_roadmap_success(self, temp_data_dir, sample_roadmap):
        """Testa handle_generate_roadmap com tema válido."""
        with patch("server.gerar_roadmap_ia") as mock_gerar:
            with patch("server.salvar_roadmap") as mock_salvar:
                mock_gerar.return_value = sample_roadmap
                mock_salvar.return_value = os.path.join(temp_data_dir, "roadmap_test.json")

                handler = create_handler(temp_data_dir)
                data = {"tema": "Python"}
                handler.path = "/api/generate-roadmap"
                handler.handle_generate_roadmap(data)

                assert handler._response_code == 200
                result = json.loads(handler.wfile.data)
                assert result["status"] == "success"

    def test_generate_roadmap_empty_theme(self, temp_data_dir):
        """Testa handle_generate_roadmap com tema vazio."""
        with patch("server.gerar_roadmap_ia") as mock_gerar:
            mock_gerar.return_value = None

            handler = create_handler(temp_data_dir)
            data = {"tema": ""}
            handler.path = "/api/generate-roadmap"
            handler.handle_generate_roadmap(data)

            assert handler._response_code == 500

    def test_generate_roadmap_error(self, temp_data_dir):
        """Testa handle_generate_roadmap com erro na IA."""
        with patch("server.gerar_roadmap_ia") as mock_gerar:
            mock_gerar.return_value = None

            handler = create_handler(temp_data_dir)
            data = {"tema": "Test"}
            handler.path = "/api/generate-roadmap"
            handler.handle_generate_roadmap(data)

            assert handler._response_code == 500


class TestSaveRoadmap:
    """Test POST /api/save-roadmap."""

    def test_save_roadmap_success(self, temp_data_dir, sample_roadmap):
        """Testa handle_save_roadmap com dados válidos."""
        handler = create_handler(temp_data_dir)
        data = {"filename": "test_save.json", "data": sample_roadmap}
        handler.path = "/api/save-roadmap"
        handler.handle_save_roadmap(data)

        assert handler._response_code == 200
        result = json.loads(handler.wfile.data)
        assert result["status"] == "success"

        filepath = os.path.join(temp_data_dir, "test_save.json")
        assert os.path.exists(filepath)

    def test_save_roadmap_permission_error(self, temp_data_dir):
        """Testa handle_save_roadmap com erro de permissão."""
        test_dir = os.path.join(temp_data_dir, "readonly")
        os.makedirs(test_dir)
        filepath = os.path.join(test_dir, "readonly.json")
        with open(filepath, "w") as f:
            f.write("{}")
        os.chmod(test_dir, 0o444)

        handler = create_handler(temp_data_dir)
        data = {"filename": os.path.join(test_dir, "readonly.json"), "data": {"test": "data"}}
        handler.path = "/api/save-roadmap"
        handler.handle_save_roadmap(data)

        assert handler._response_code == 500

        os.chmod(test_dir, 0o755)


class TestRegenerateDepMap:
    """Test POST /api/regenerate-dep-map."""

    def test_regenerate_dep_map_success(self, temp_data_dir, sample_roadmap):
        """Testa handle_regenerate_dep_map com roadmaps existentes."""
        filepath = os.path.join(temp_data_dir, "roadmap_analise.json")
        with open(filepath, "w") as f:
            json.dump(sample_roadmap, f)

        handler = create_handler(temp_data_dir)
        handler.path = "/api/regenerate-dep-map"
        handler.handle_regenerate_dep_map()

        assert handler._response_code == 200
        result = json.loads(handler.wfile.data)
        assert result["status"] == "success"
        assert "entries" in result

        dep_map_path = os.path.join(temp_data_dir, "dep_map.json")
        assert os.path.exists(dep_map_path)

    def test_regenerate_dep_map_no_files(self, temp_data_dir):
        """Testa handle_regenerate_dep_map sem roadmaps."""
        handler = create_handler(temp_data_dir)
        handler.path = "/api/regenerate-dep-map"
        handler.handle_regenerate_dep_map()

        assert handler._response_code == 200
        result = json.loads(handler.wfile.data)
        assert result["status"] == "success"
        assert result["entries"] == 0


class TestDiagnosisErrorHandling:
    """Test POST /api/diagnose error cases."""

    def test_diagnose_missing_topic(self, temp_data_dir, sample_dep_map):
        """Testa diagnose sem topic (400)."""
        dep_map_path = os.path.join(temp_data_dir, "dep_map.json")
        with open(dep_map_path, "w") as f:
            json.dump(sample_dep_map, f)

        handler = create_handler(temp_data_dir)
        data = {"user_answer": "resposta"}
        handler.path = "/api/diagnose"
        handler.handle_diagnosis(data)

        assert handler._response_code == 400
        result = json.loads(handler.wfile.data)
        assert result["status"] == "error"

    def test_diagnose_missing_answer(self, temp_data_dir, sample_dep_map):
        """Testa diagnose sem user_answer (400)."""
        dep_map_path = os.path.join(temp_data_dir, "dep_map.json")
        with open(dep_map_path, "w") as f:
            json.dump(sample_dep_map, f)

        handler = create_handler(temp_data_dir)
        data = {"topic": "Python Fundamentos"}
        handler.path = "/api/diagnose"
        handler.handle_diagnosis(data)

        assert handler._response_code == 400

    def test_diagnose_llm_failure(self, temp_data_dir, sample_dep_map):
        """Testa diagnose com falha LLM (502)."""
        dep_map_path = os.path.join(temp_data_dir, "dep_map.json")
        with open(dep_map_path, "w") as f:
            json.dump(sample_dep_map, f)

        handler = create_handler(temp_data_dir)
        data = {"topic": "Python Fundamentos", "user_answer": "resposta"}
        handler.path = "/api/diagnose"

        with patch("server.DiagnosisService") as mock_service:
            mock_instance = Mock()
            mock_instance.diagnose.side_effect = Exception("OpenAI API Error")
            mock_service.return_value = mock_instance

            handler.handle_diagnosis(data)

            assert handler._response_code == 502

    def test_diagnose_internal_error(self, temp_data_dir, sample_dep_map):
        """Testa diagnose com erro interno (500)."""
        dep_map_path = os.path.join(temp_data_dir, "dep_map.json")
        with open(dep_map_path, "w") as f:
            json.dump(sample_dep_map, f)

        handler = create_handler(temp_data_dir)
        data = {"topic": "Python Fundamentos", "user_answer": "resposta"}
        handler.path = "/api/diagnose"

        with patch("server.DiagnosisService") as mock_service:
            mock_instance = Mock()
            mock_instance.diagnose.side_effect = Exception("Erro interno qualquer")
            mock_service.return_value = mock_instance

            handler.handle_diagnosis(data)

            assert handler._response_code == 500


class TestCORs:
    """Test CORS headers."""

    def test_cors_headers_present(self, temp_data_dir):
        """Testa que headers CORS estão presentes."""
        handler = create_handler(temp_data_dir)
        handler.end_headers()
        assert "Access-Control-Allow-Origin" in handler._response_headers
        assert handler._response_headers["Access-Control-Allow-Origin"] == "*"
        assert "Access-Control-Allow-Methods" in handler._response_headers
        assert "Access-Control-Allow-Headers" in handler._response_headers

    def test_do_options(self, temp_data_dir):
        """Testa que OPTIONS retorna 200."""
        handler = create_handler(temp_data_dir)
        handler.do_OPTIONS()
        assert handler._response_code == 200


if __name__ == "__main__":
    import unittest
    unittest.main()