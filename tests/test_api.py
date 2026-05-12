"""
Tests for the Diagnosis Service.
"""

import json
import os
import shutil
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.services.diagnosis.diagnosis_service import DiagnosisService


class TestDiagnosisService(unittest.TestCase):
    """Test cases for the DiagnosisService."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_dir = "/tmp/test_data"
        os.makedirs(self.data_dir, exist_ok=True)

        self.dep_map = {"Python Fundamentos": ["variáveis", "tipos"]}
        with open(
            os.path.join(self.data_dir, "dep_map.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.dep_map, f)

        self.service = DiagnosisService(self.data_dir)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.data_dir, ignore_errors=True)

    def test_diagnose_success(self):
        """Test successful diagnosis with a hit (no gap)."""
        with patch(
            "backend.services.diagnosis.diagnosis_service.OpenAI"
        ) as mock_openai_class:
            mock_client = Mock()
            mock_completion = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = (
                "O usuário demonstra domínio dos pré-requisitos. Pode avançar."
            )
            mock_choice.message = mock_message
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai_class.return_value = mock_client

            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
                result = self.service.diagnose(
                    "Python Fundamentos", "Variáveis armazenam dados."
                )

                self.assertEqual(result["status"], "hit")
                self.assertFalse(result["has_gap"])
                self.assertEqual(result["tags"], self.dep_map["Python Fundamentos"])
                self.assertIn("avançar", result["message"])

    def test_diagnose_with_gap(self):
        """Test successful diagnosis with a miss (gap found)."""
        with patch(
            "backend.services.diagnosis.diagnosis_service.OpenAI"
        ) as mock_openai_class:
            mock_client = Mock()
            mock_completion = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = (
                "Falta conhecimento básico sobre tipos de dados. "
                "Revisar tipagem dinâmica."
            )
            mock_choice.message = mock_message
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai_class.return_value = mock_client

            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
                result = self.service.diagnose(
                    "Python Fundamentos", "Não sei o que são variáveis."
                )

                self.assertEqual(result["status"], "miss")
                self.assertTrue(result["has_gap"])
                self.assertIn("Falta", result["message"])

    def test_diagnose_missing_api_key(self):
        """Test diagnosis when API key is missing."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}, clear=False):
            with self.assertRaises(PermissionError) as cm:
                self.service.diagnose("Python Fundamentos", "Resposta")
            self.assertEqual(str(cm.exception), "API key não configurada")

    def test_diagnose_missing_dep_map(self):
        """Test diagnosis when dep_map is missing."""
        empty_dir = "/tmp/empty_test_data"
        os.makedirs(empty_dir, exist_ok=True)
        service = DiagnosisService(empty_dir)

        with self.assertRaises(FileNotFoundError) as cm:
            service.diagnose("Python Fundamentos", "Resposta")
        self.assertEqual(str(cm.exception), "Mapa de dependências não encontrado")

        shutil.rmtree(empty_dir, ignore_errors=True)

    def test_diagnose_truncation(self):
        """Test that diagnosis is truncated to 100 words."""
        with patch(
            "backend.services.diagnosis.diagnosis_service.OpenAI"
        ) as mock_openai_class:
            mock_client = Mock()
            mock_completion = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "palavra " * 150
            mock_choice.message = mock_message
            mock_completion.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai_class.return_value = mock_client

            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
                result = self.service.diagnose("Python Fundamentos", "Resposta")

                words = result["message"].split()
                self.assertEqual(len(words), 100)
                self.assertTrue(result["message"].endswith("..."))


if __name__ == "__main__":
    unittest.main()
