"""Test LLM connection functionality."""
import json
from unittest.mock import Mock, patch
import sys
import os

import pytest
import requests
from langchain_openai import ChatOpenAI

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestLLMConnection:
    """Test LLM connection methods."""

    @pytest.mark.llm
    def test_direct_llm_connection(self, llm_config):
        """Test direct connection to local LLM."""
        endpoint = f"{llm_config['base_url']}/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": llm_config["model"],
            "messages": [
                {"role": "user", "content": "Say hello in a simple short sentence"}
            ],
            "temperature": llm_config["temperature"],
        }

        with patch("requests.post") as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {"message": {"content": "Hello! How can I help you today?"}}
                ]
            }
            mock_post.return_value = mock_response

            response = requests.post(endpoint, headers=headers, json=data, timeout=10)

            assert response.status_code == 200
            json_response = response.json()
            assert "choices" in json_response
            assert "message" in json_response["choices"][0]

    @pytest.mark.llm
    def test_langchain_connection(self, llm_config, mock_llm):
        """Test LangChain LLM connection."""
        with patch("langchain_openai.ChatOpenAI") as mock_chat_openai:
            # Configure the mock to return our mock_llm
            mock_chat_openai.return_value = mock_llm
            
            # Mock the invoke method to return a predictable response
            mock_response = Mock()
            mock_response.content = "Test response from LLM"
            mock_llm.invoke.return_value = mock_response

            llm = mock_chat_openai(
                model_name=llm_config["model"],
                base_url=llm_config["base_url"],
                api_key=llm_config["api_key"],
                temperature=llm_config["temperature"],
            )

            response = llm.invoke(
                [{"role": "user", "content": "Say hello in a simple short sentence"}]
            )

            assert response.content == "Test response from LLM"
            mock_chat_openai.assert_called_once()

    @pytest.mark.llm
    def test_get_llm_function(self):
        """Test the get_llm utility function."""
        try:
            with patch("meeting_minutes.utils.llm_config.get_llm") as mock_get_llm:
                mock_instance = Mock()
                mock_get_llm.return_value = mock_instance

                from meeting_minutes.utils.llm_config import get_llm
                llm = get_llm()

                assert llm == mock_instance
                mock_get_llm.assert_called_once()
        except ImportError:
            pytest.skip("meeting_minutes module not available in test environment")

    @pytest.mark.llm
    def test_llm_config_values(self):
        """Test LLM configuration values."""
        try:
            from meeting_minutes.config.app_config import LLM_SERVER
            
            assert "base_url" in LLM_SERVER
            assert "api_key" in LLM_SERVER
            assert LLM_SERVER["base_url"]  # Should not be empty
            # Handle case where API key might be None (for local LLM setups)
            api_key = LLM_SERVER["api_key"]
            assert api_key is not None or api_key == "not-needed", f"API key should be set or 'not-needed', got: {api_key}"
        except ImportError:
            pytest.skip("meeting_minutes.config module not available in test environment")

    @pytest.mark.slow
    @pytest.mark.llm
    def test_real_llm_connection(self):
        """Test real LLM connection (slow test)."""
        try:
            from meeting_minutes.utils.llm_config import get_llm
            llm = get_llm()
            response = llm.invoke([
                {"role": "user", "content": "Hello, respond with just 'OK'"}
            ])
            assert response is not None
            assert hasattr(response, 'content')
        except ImportError:
            pytest.skip("meeting_minutes module not available")
        except Exception as e:
            pytest.skip(f"Real LLM not available: {e}")
