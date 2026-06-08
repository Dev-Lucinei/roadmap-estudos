"""Tests for backend/core/config.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from backend.core.config import (
    BASE_DIR,
    DATA_DIR,
    FRONTEND_DIR,
    LICOES_DIR,
    check_api_key,
    get_api_key,
)


class TestConfigPaths:
    """Tests for configuration paths."""

    def test_base_dir_is_path(self):
        assert isinstance(BASE_DIR, Path)

    def test_data_dir(self):
        assert DATA_DIR == BASE_DIR / "data"

    def test_licoes_dir(self):
        assert LICOES_DIR == BASE_DIR / "licoes"

    def test_frontend_dir(self):
        assert FRONTEND_DIR == BASE_DIR / "frontend" / "public"


class TestGetApiKey:
    """Tests for get_api_key function."""

    def test_returns_key_when_set(self):
        with patch("backend.core.config.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            assert get_api_key() == "test-key"

    def test_returns_none_when_missing(self):
        with patch("backend.core.config.settings") as mock_settings:
            mock_settings.OPENROUTER_API_KEY = None
            assert get_api_key() is None


class TestCheckApiKey:
    """Tests for check_api_key function."""

    def test_raises_when_missing(self):
        with patch("backend.core.config.get_api_key", return_value=None):
            with pytest.raises(PermissionError):
                check_api_key()

    def test_passes_when_present(self):
        with patch("backend.core.config.get_api_key", return_value="key"):
            check_api_key()
