"""Test configuration and fixtures."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to Python path
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return ROOT_DIR


@pytest.fixture(scope="session")
def src_dir():
    """Return the source directory."""
    return SRC_DIR


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    test_vars = {
        "OPENAI_API_KEY": "test-key",
        "LLM_SERVER_BASE_URL": "http://localhost:1337/v1",
        "LLM_SERVER_API_KEY": "test-local-key",
    }
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)
    return test_vars


@pytest.fixture
def llm_config():
    """LLM configuration for testing."""
    return {
        "base_url": "http://localhost:1337",
        "api_key": "test-key",
        "model": "test-model",
        "temperature": 0.7,
    }


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = Mock()
    mock.invoke.return_value = Mock(content="Mock response")
    return mock


@pytest.fixture
def mock_credentials_data():
    """Mock Google OAuth credentials data."""
    return {
        "web": {
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "redirect_uris": [
                "http://localhost:62366/oauth/callback",
                "http://localhost:62366",
            ],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


@pytest.fixture
def mock_token_data():
    """Mock token data for testing."""
    return {
        "token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
    }


def pytest_collection_modifyitems(config, items):
    """Skip tests that require unavailable dependencies."""
    skip_crewai = pytest.mark.skip(reason="CrewAI requires Python 3.10+ (Self type)")

    for item in items:
        # Skip CrewAI tests if Self type is not available
        if "crew" in item.nodeid.lower():
            try:
                pass
            except ImportError:
                item.add_marker(skip_crewai)
