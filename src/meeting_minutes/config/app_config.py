"""
Centralized configuration management for Meeting Minutes Agent.
"""

import os
from pathlib import Path
from typing import Any, Dict

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
MEETING_MINUTES_DIR = SRC_DIR / "meeting_minutes"
TOOLS_DIR = MEETING_MINUTES_DIR / "crews" / "gmailcrew" / "tools"
LLM_SERVER = {
    "base_url": "http://localhost:1337/v1",
    "model_name": "gpt-4",
    "api_key": "not-needed",  # No API key needed for local server
}


# Google OAuth Configuration
GOOGLE_OAUTH: Dict[str, Any] = {
    "port": int(os.getenv("GOOGLE_OAUTH_PORT", "62366")),
    "callback_url": f"http://localhost:{os.getenv('GOOGLE_OAUTH_PORT', '62366')}",
    "scopes": ["https://www.googleapis.com/auth/gmail.compose"],
    "credentials_path": str(TOOLS_DIR / "credentials.json"),
    "token_path": str(TOOLS_DIR / "token.json"),
}

# API Configuration
API_CONFIG: Dict[str, Any] = {
    "elevenlabs": {
        "model_id": "scribe_v1",
        "tag_audio_events": True,
        "diarize": True,
        "language_code": None,  # Auto-detect
    },
    "openai": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
    },
}

# Processing Configuration
PROCESSING_CONFIG: Dict[str, Any] = {
    "audio": {
        "chunk_length_ms": 60000,  # 1 minute chunks
        "supported_formats": ["wav", "mp3", "m4a", "flac"],
        "max_file_size_mb": 100,
    },
    "transcription": {
        "cleanup_temp_files": False,  # Disable to avoid permission issues
        "retry_attempts": 3,
        "retry_delay": 1.0,
    },
}

# Logging Configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": str(PROJECT_ROOT / "logs" / "meeting_minutes.log"),
}

# Validate required environment variables
REQUIRED_ENV_VARS = [
    "ELEVENLABS_API_KEY",
    "OPENAI_API_KEY",
]


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var) and not os.getenv(
            var.replace("ELEVENLABS", "ELEVEN_LABS")
        ):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False

    return True


def get_credentials_info() -> Dict[str, Any]:
    """Get information about OAuth credentials setup."""
    creds_path = Path(GOOGLE_OAUTH["credentials_path"])
    token_path = Path(GOOGLE_OAUTH["token_path"])

    return {
        "credentials_exists": creds_path.exists(),
        "token_exists": token_path.exists(),
        "credentials_path": str(creds_path),
        "token_path": str(token_path),
        "callback_url": GOOGLE_OAUTH["callback_url"],
    }
