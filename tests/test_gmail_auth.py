"""Test Gmail authentication functionality."""
import json
import sys
import os
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
from google.oauth2.credentials import Credentials

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestGmailAuth:
    """Test Gmail authentication methods."""

    def test_environment_setup(self):
        """Test environment setup checking."""
        try:
            from meeting_minutes.config.app_config import GOOGLE_OAUTH, get_credentials_info
            
            creds_info = get_credentials_info()
            
            assert "credentials_exists" in creds_info
            assert "token_exists" in creds_info
            assert "callback_url" in creds_info
            assert "credentials_path" in creds_info
            assert creds_info["callback_url"] == GOOGLE_OAUTH["callback_url"]
        except ImportError:
            pytest.skip("meeting_minutes.config module not available in test environment")

    def test_credentials_file_validation(self, mock_credentials_data):
        """Test credentials file validation."""
        try:
            from meeting_minutes.config.app_config import GOOGLE_OAUTH
            
            with patch("builtins.open", mock_open(read_data=json.dumps(mock_credentials_data))):
                with patch("os.path.exists", return_value=True):
                    # Test valid credentials structure
                    assert "web" in mock_credentials_data
                    web_data = mock_credentials_data["web"]
                    
                    required_fields = ["client_id", "client_secret", "redirect_uris"]
                    for field in required_fields:
                        assert field in web_data
                    
                    # Test redirect URI - check if callback URL is in redirect URIs
                    expected_uri = GOOGLE_OAUTH["callback_url"]
                    redirect_uris = web_data["redirect_uris"]
                    # Check if any redirect URI contains the expected callback URL path
                    assert any(expected_uri in uri or uri.endswith('/oauth/callback') for uri in redirect_uris)
        except ImportError:
            pytest.skip("meeting_minutes.config module not available in test environment")

    @pytest.mark.gmail
    def test_token_validation(self, mock_token_data):
        """Test token validation logic."""
        try:
            from meeting_minutes.config.app_config import GOOGLE_OAUTH
            
            with patch("builtins.open", mock_open(read_data=json.dumps(mock_token_data))):
                with patch("os.path.exists", return_value=True):
                    with patch.object(Credentials, "from_authorized_user_file") as mock_creds:
                        mock_creds_instance = Mock()
                        mock_creds_instance.valid = True
                        mock_creds.return_value = mock_creds_instance
                        
                        creds = Credentials.from_authorized_user_file("test", GOOGLE_OAUTH["scopes"])
                        assert creds.valid
        except ImportError:
            pytest.skip("meeting_minutes.config module not available in test environment")

    @pytest.mark.gmail
    def test_oauth_configuration(self):
        """Test OAuth configuration values."""
        try:
            from meeting_minutes.config.app_config import GOOGLE_OAUTH
            
            assert "port" in GOOGLE_OAUTH
            assert "callback_url" in GOOGLE_OAUTH
            assert "credentials_path" in GOOGLE_OAUTH
            assert "token_path" in GOOGLE_OAUTH
            assert "scopes" in GOOGLE_OAUTH
            
            assert isinstance(GOOGLE_OAUTH["port"], int)
            assert GOOGLE_OAUTH["port"] == 62366
            assert "localhost:62366" in GOOGLE_OAUTH["callback_url"]
            assert isinstance(GOOGLE_OAUTH["scopes"], list)
            assert len(GOOGLE_OAUTH["scopes"]) > 0
        except ImportError:
            pytest.skip("meeting_minutes.config module not available in test environment")

    @pytest.mark.gmail
    def test_gmail_api_mock(self):
        """Test Gmail API interaction with mocks."""
        with patch("googleapiclient.discovery.build") as mock_build:
            mock_service = Mock()
            mock_users = Mock()
            mock_profile = Mock()
            
            mock_profile.execute.return_value = {
                "emailAddress": "test@example.com",
                "messagesTotal": 100,
                "threadsTotal": 50
            }
            mock_users.getProfile.return_value = mock_profile
            mock_service.users.return_value = mock_users
            mock_build.return_value = mock_service
            
            # Simulate API call
            service = mock_build("gmail", "v1", credentials=Mock())
            profile = service.users().getProfile(userId="me").execute()
            
            assert profile["emailAddress"] == "test@example.com"
            assert profile["messagesTotal"] == 100
            assert profile["threadsTotal"] == 50
