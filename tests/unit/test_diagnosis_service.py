"""Tests for DiagnosisService - additional coverage."""

import json
import os
import shutil
import tempfile
from unittest.mock import Mock, patch

import pytest

from backend.services.diagnosis.diagnosis_service import (
    DiagnosisService,
)


@pytest.fixture
def service_with_data():
    """Create a DiagnosisService with temp data."""
    tmp = tempfile.mkdtemp()
    dep_map = {"Python": ["vars", "types"], "Java": []}
    with open(os.path.join(tmp, "dep_map.json"), "w") as f:
        json.dump(dep_map, f)
    svc = DiagnosisService(data_dir=tmp)
    yield svc, tmp, dep_map
    shutil.rmtree(tmp, ignore_errors=True)


class TestDiagnosisServiceInit:
    """Tests for DiagnosisService initialization."""

    def test_default_data_dir(self):
        svc = DiagnosisService()
        assert str(svc.data_dir).endswith("data")

    def test_custom_data_dir(self, tmp_path):
        svc = DiagnosisService(data_dir=str(tmp_path))
        assert str(svc.data_dir) == str(tmp_path)


class TestGetClient:
    """Tests for get_client method."""

    def test_missing_api_key(self, service_with_data):
        svc, _, _ = service_with_data
        with patch("backend.core.config.get_api_key", return_value=None):
            with pytest.raises(PermissionError):
                svc.get_client()

    def test_import_error(self, service_with_data):
        svc, _, _ = service_with_data
        with patch(
            "backend.services.diagnosis.diagnosis_service.OpenAI",
            None,
        ):
            with pytest.raises(ImportError):
                svc.get_client()

    def test_valid_client(self, service_with_data):
        svc, _, _ = service_with_data
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "k"}):
            with patch("backend.services.diagnosis.diagnosis_service.OpenAI") as mock_cls:
                svc.get_client()
                mock_cls.assert_called_once()


class TestDiagnoseWithTopics:
    """Tests for diagnose with various topic configurations."""

    def test_topic_without_prerequisites(self, service_with_data):
        svc, _, dep_map = service_with_data
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Tudo bem. Pode avançar."))]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with (
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "key"}),
            patch.object(svc, "get_client", return_value=mock_client),
        ):
            result = svc.diagnose("Java", "Resposta")
            assert result["tags"] == []
            assert result["status"] == "hit"

    def test_diagnose_with_gap_indicators(self, service_with_data):
        svc, _, _ = service_with_data
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Falta entender tipos. Precisa revisar conceitos."))
        ]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with (
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "key"}),
            patch.object(svc, "get_client", return_value=mock_client),
        ):
            result = svc.diagnose("Python", "Resposta")
            assert result["status"] == "miss"
            assert result["has_gap"] is True
