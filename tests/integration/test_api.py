"""
Tests for the Diagnosis Service.
"""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from backend.services.diagnosis.diagnosis_service import DiagnosisService


class TestDiagnosisService(unittest.TestCase):
    """Test cases for the DiagnosisService."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_dir = tempfile.mkdtemp()
        self.dep_map = {"Python Fundamentos": ["variáveis", "tipos"]}
        with open(os.path.join(self.data_dir, "dep_map.json"), "w", encoding="utf-8") as f:
            json.dump(self.dep_map, f)
        self.service = DiagnosisService(self.data_dir)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_diagnose_success(self):
        """Test successful diagnosis with a hit (no gap)."""
        from tests.conftest import create_mock_openai_client

        mock_client = create_mock_openai_client(
            "O usuário demonstra domínio dos pré-requisitos. Pode avançar."
        )
        with (
            patch(
                "backend.services.diagnosis.diagnosis_service.OpenAI",
                return_value=mock_client,
            ),
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}),
        ):
            result = self.service.diagnose("Python Fundamentos", "Variáveis armazenam dados.")

            self.assertEqual(result["status"], "hit")
            self.assertFalse(result["has_gap"])
            self.assertEqual(result["tags"], self.dep_map["Python Fundamentos"])
            self.assertIn("avançar", result["message"])

    def test_diagnose_with_gap(self):
        """Test successful diagnosis with a miss (gap found)."""
        from tests.conftest import create_mock_openai_client

        mock_client = create_mock_openai_client(
            "Falta conhecimento básico sobre tipos de dados. Revisar tipagem dinâmica."
        )
        with (
            patch(
                "backend.services.diagnosis.diagnosis_service.OpenAI",
                return_value=mock_client,
            ),
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}),
        ):
            result = self.service.diagnose("Python Fundamentos", "Não sei o que são variáveis.")

            self.assertEqual(result["status"], "miss")
            self.assertTrue(result["has_gap"])
            self.assertIn("Falta", result["message"])

    def test_diagnose_missing_api_key(self):
        """Test diagnosis when API key is missing."""
        with patch("backend.core.config.get_api_key", return_value=None):
            with self.assertRaises(PermissionError) as cm:
                self.service.diagnose("Python Fundamentos", "Resposta")
            self.assertEqual(str(cm.exception), "API key não configurada")

    def test_diagnose_missing_dep_map(self):
        """Test diagnosis when dep_map is missing."""
        empty_dir = tempfile.mkdtemp()
        try:
            service = DiagnosisService(empty_dir)
            with self.assertRaises(FileNotFoundError) as cm:
                service.diagnose("Python Fundamentos", "Resposta")
            self.assertEqual(str(cm.exception), "Mapa de dependências não encontrado")
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)

    def test_diagnose_truncation(self):
        """Test that diagnosis is truncated to 100 words."""
        from tests.conftest import create_mock_openai_client

        mock_client = create_mock_openai_client("palavra " * 150)
        with (
            patch(
                "backend.services.diagnosis.diagnosis_service.OpenAI",
                return_value=mock_client,
            ),
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}),
        ):
            result = self.service.diagnose("Python Fundamentos", "Resposta")

            words = result["message"].split()
            self.assertEqual(len(words), 100)
            self.assertTrue(result["message"].endswith("..."))


if __name__ == "__main__":
    unittest.main()
