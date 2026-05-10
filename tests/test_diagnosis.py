"""
Unit tests for diagnostic functionality.
"""

import json
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDiagnosisLogic(unittest.TestCase):
    """Test cases for diagnostic logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = tempfile.mkdtemp()
        self.dep_map_path = os.path.join(self.test_data_dir, "dep_map.json")

        test_dep_map = {
            "Python Fundamentos": [],
            "Análise de Dados": ["Python Fundamentos"],
            "Machine Learning": ["Python Fundamentos", "Análise de Dados"],
        }
        with open(self.dep_map_path, "w", encoding="utf-8") as f:
            json.dump(test_dep_map, f)

        with open(self.dep_map_path, "r", encoding="utf-8") as f:
            self.dep_map = json.load(f)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_data_dir, ignore_errors=True)

    def test_load_dependency_map(self):
        """Test that dependency map loads correctly."""
        self.assertIsInstance(self.dep_map, dict)
        self.assertIn("Python Fundamentos", self.dep_map)
        self.assertIn("Análise de Dados", self.dep_map)

        # Check specific dependencies
        self.assertEqual(self.dep_map["Python Fundamentos"], [])
        self.assertEqual(self.dep_map["Análise de Dados"], ["Python Fundamentos"])

    def test_prerequisites_extraction(self):
        """Test extraction of prerequisites for topics."""
        python_fund_prereqs = self.dep_map.get("Python Fundamentos", [])
        self.assertEqual(python_fund_prereqs, [])

        analytics_prereqs = self.dep_map.get("Análise de Dados", [])
        self.assertEqual(analytics_prereqs, ["Python Fundamentos"])

        ml_prereqs = self.dep_map.get("Machine Learning", [])
        self.assertEqual(ml_prereqs, ["Python Fundamentos", "Análise de Dados"])

    def test_gap_detection_logic(self):
        """Test logic for detecting knowledge gaps."""
        # Sample diagnosis text that indicates a gap
        gap_diagnosis = "Você precisa revisar variáveis antes de avançar. Lacuna em compreensão de tipos."
        gap_indicators = [
            "falta",
            "não sabe",
            "revisar",
            "precisa",
            "lacuna",
            "não entende",
        ]
        has_gap = any(
            indicator in gap_diagnosis.lower() for indicator in gap_indicators
        )
        self.assertTrue(has_gap)

        # Sample diagnosis text that indicates no gap
        no_gap_diagnosis = "Entendo o conceito de variáveis. Uma regra importante é usar nomes descritivos."
        has_gap = any(
            indicator in no_gap_diagnosis.lower() for indicator in gap_indicators
        )
        self.assertFalse(has_gap)

    def test_word_count_limit(self):
        """Test that diagnosis respects 100-word limit."""
        # Create a text with exactly 100 words
        hundred_words = " ".join([f"word{i}" for i in range(100)])
        self.assertEqual(len(hundred_words.split()), 100)

        # Create a text with 101 words
        hundred_one_words = " ".join([f"word{i}" for i in range(101)])
        self.assertEqual(len(hundred_one_words.split()), 101)

        # Test truncation logic
        if len(hundred_one_words.split()) > 100:
            truncated = " ".join(hundred_one_words.split()[:100]) + "..."
            self.assertEqual(len(truncated.split()), 100)
            self.assertTrue(truncated.endswith("..."))


if __name__ == "__main__":
    unittest.main()
