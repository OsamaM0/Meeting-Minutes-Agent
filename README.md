# Meeting Minutes Agent

An AI-powered meeting minutes generator that transcribes audio files, generates structured meeting minutes, and automatically creates Gmail drafts.

## Features

- **Audio Transcription**: Uses ElevenLabs API to transcribe meeting recordings
- **AI-Powered Minutes**: Generates structured meeting minutes using CrewAI
- **Gmail Integration**: Automatically creates draft emails with meeting minutes
- **Chunked Processing**: Handles large audio files by processing in chunks
- **OAuth2 Authentication**: Secure Gmail authentication with proper redirect handling

## Architecture

```
src/meeting_minutes/
├── config/           # Configuration management
├── crews/           # CrewAI crew definitions
│   ├── meeting_minutes_crew/
│   └── gmailcrew/
├── tools/           # Custom tools and utilities
├── utils/           # Utility functions and patches
└── main.py         # Main application entry point
```

## Prerequisites

- Python 3.8+
- Google Cloud Console project with Gmail API enabled
- ElevenLabs API key
- **Local LLM Server** (e.g., Ollama, LocalAI, or compatible OpenAI API server)
- Audio file in WAV format

## Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd Meeting-Minutes-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Set up pre-commit hooks (recommended for development)
pre-commit install
```

### 1.1. Pre-commit Setup (For Developers)

This project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files (optional)
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

The pre-commit configuration includes:
- **Code formatting**: Black, isort
- **Linting**: flake8, pydocstyle  
- **Security**: bandit
- **General checks**: trailing whitespace, file endings, syntax validation

### 2. Local LLM Server Setup

**Option A: Using Ollama**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (e.g., Llama 2)
ollama pull llama2

# Start server (runs on http://localhost:11434 by default)
ollama serve
```

**Option B: Using LocalAI**
```bash
# Using Docker
docker run -p 8080:8080 --name local-ai -ti localai/localai:latest
```

**Option C: Any OpenAI-compatible server**
- Ensure it's running on http://localhost:1337 (or update config)
- Supports `/v1/chat/completions` endpoint
- Has at least one model available

### 3. API Keys Configuration

Create a `.env` file in the root directory:

```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVEN_LABS_API_KEY=your_elevenlabs_api_key  # Alternative name
OPENAI_API_KEY=your_openai_api_key
```

### 4. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Add redirect URI: `http://localhost:62366`
6. Download `credentials.json`
7. Place `credentials.json` in `src/meeting_minutes/crews/gmailcrew/tools/`

### 5. Audio File Preparation

Place your audio file as `EarningsCall.wav` in the `src/meeting_minutes/` directory.

## Usage

### Running the Application

```bash
python src/meeting_minutes/main.py
```

### Testing Gmail Authentication

```bash
python test_gmail_auth.py
```

### Testing Local LLM Server

```python
# Add this to your main.py or run separately
from src.meeting_minutes.utils.monkey_patches import debug_local_server
debug_local_server()
```

## Configuration

The application uses centralized configuration in `src/meeting_minutes/config/app_config.py`:

- OAuth port configuration
- API endpoints
- File paths
- Processing parameters
- **Local LLM server settings**

## Troubleshooting

### Local LLM Server Issues (404 Error)

**Problem**: `litellm.NotFoundError: NotFoundError: OpenAIException - Error code: 404 - {'detail': 'Not Found'}`

**Solutions**:

1. **Check if your local LLM server is running**:
   ```bash
   curl http://localhost:1337/health
   # or whatever port your server uses
   ```

2. **Verify available models**:
   ```bash
   curl http://localhost:1337/v1/models
   ```

3. **Common Local LLM Server URLs**:
   - Ollama: `http://localhost:11434`
   - LocalAI: `http://localhost:8080`
   - Text Generation WebUI: `http://localhost:5000`
   - Update `LLM_SERVER["base_url"]` in config accordingly

4. **Enable debugging**:
   ```python
   # Add to your main.py
   import litellm
   litellm.set_verbose = True
   ```

5. **Check server logs** for what endpoint is being requested

6. **Try different model names**:
   - The app tries multiple model names automatically
   - Check your server's model list and update config if needed

### Gmail Authentication Issues

1. Verify redirect URI matches: `http://localhost:62366`
2. Check credentials.json is properly placed
3. Run the test script: `python test_gmail_auth.py`

### Audio Processing Issues

1. Ensure audio file is in WAV format
2. Check ElevenLabs API key is valid
3. Verify audio file size (large files are chunked automatically)

## Development

### Code Quality Standards

This project uses automated code quality tools:

- **Black**: Code formatting (88 character line limit)
- **isort**: Import sorting  
- **flake8**: Linting and style checking
- **pydocstyle**: Docstring conventions (Google style)
- **bandit**: Security vulnerability scanning
- **pre-commit**: Automated quality checks before commits

### Running Quality Checks Manually

```bash
# Format code
black src/ test_*.py

# Sort imports  
isort src/ test_*.py

# Lint code
flake8 src/ test_*.py

# Check docstrings
pydocstyle src/

# Security scan
bandit -r src/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Adding Custom Tools

1. Create new tool in `src/meeting_minutes/tools/`
2. Inherit from `BaseTool`
3. Define input schema with Pydantic
4. Implement `_run` method

### Extending Crews

1. Add new crew in `src/meeting_minutes/crews/`
2. Define agents and tasks
3. Configure crew parameters
4. Integrate in main flow

### Local LLM Integration

The application uses monkey patches to redirect CrewAI's LLM calls to your local server:

1. **Automatic model detection** - Tries multiple model names
2. **Debug logging** - Shows what's being sent to server
3. **Health checks** - Verifies server connectivity
4. **Fallback handling** - Graceful error messages

## License

Apache License 2.0 - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## Support

For issues and questions:
1. Check troubleshooting section
2. Run debug functions for local LLM server
3. Review test scripts
4. Check configuration files
5. Submit GitHub issue with debug output
