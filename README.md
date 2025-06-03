# 🎤 Meeting Minutes Agent

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![CrewAI](https://img.shields.io/badge/powered%20by-CrewAI-orange)](https://crewai.com)

> **Transform your meeting recordings into professional, structured minutes with AI-powered transcription and intelligent summarization.**

An enterprise-grade AI solution that automatically transcribes meeting audio, generates structured meeting minutes using advanced AI agents, and seamlessly integrates with Gmail for instant sharing. Perfect for businesses, teams, and professionals who want to streamline their meeting documentation workflow.

---

## 🌟 Features

### 🎯 Core Capabilities
- **🎙️ Audio Transcription**: High-accuracy transcription using ElevenLabs API with speaker diarization
- **🤖 AI-Powered Minutes**: Intelligent meeting minutes generation using CrewAI multi-agent system
- **📧 Gmail Integration**: Automatic draft creation with OAuth2 authentication
- **📊 Chunked Processing**: Efficient handling of large audio files (up to 100MB)
- **🔒 Secure Authentication**: Enterprise-grade OAuth2 with proper redirect handling
- **🎨 Rich Output**: Structured minutes with action items, sentiment analysis, and summaries

### 🛠️ Technical Features
- **Local LLM Support**: Works with Ollama, LocalAI, and OpenAI-compatible servers
- **Flexible Audio Formats**: Supports WAV, MP3, M4A, and FLAC
- **Robust Error Handling**: Comprehensive logging and fallback mechanisms
- **Code Quality**: Pre-commit hooks, automated testing, and documentation
- **Extensible Architecture**: Easy to add new agents, tools, and workflows

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/Meeting-Minutes-Agent.git
cd Meeting-Minutes-Agent
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
cp .env.example .env  # Edit with your API keys

# 4. Start local LLM (choose one)
ollama serve  # or your preferred local LLM server

# 5. Run the application
python src/meeting_minutes/main.py
```

**First time?** Follow our [detailed installation guide](#-installation) below.

---

## 📦 Installation

### Prerequisites

Before you begin, ensure you have:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.8+ | Core runtime |
| **Local LLM Server** | Any | AI processing (Ollama, LocalAI, etc.) |
| **ElevenLabs API** | Latest | Audio transcription |
| **Google Cloud Project** | - | Gmail API access |
| **Audio File** | WAV/MP3/M4A/FLAC | Meeting recording |

### Step 1: Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Meeting-Minutes-Agent.git
cd Meeting-Minutes-Agent

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Step 2: Local LLM Server Setup

Choose one of the following options:

#### Option A: Ollama (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull and run a model
ollama pull llama2
ollama serve  # Runs on http://localhost:11434
```

#### Option B: LocalAI
```bash
# Using Docker
docker run -p 8080:8080 --name local-ai -ti localai/localai:latest

# Or using Docker Compose
docker-compose up -d localai
```

#### Option C: Text Generation WebUI
```bash
# Clone and setup
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui
python server.py --api  # Runs on http://localhost:5000
```

### Step 3: API Configuration

Create your environment configuration:

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# ElevenLabs API (required)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVEN_LABS_API_KEY=your_elevenlabs_api_key_here  # Alternative name

# OpenAI API (for fallback, optional if using local LLM)
OPENAI_API_KEY=your_openai_api_key_here

# Local LLM Server Configuration (optional)
LOCAL_LLM_BASE_URL=http://localhost:11434  # Adjust based on your server
LOCAL_LLM_MODEL=llama2                     # Adjust based on your model

# Logging Configuration
LOG_LEVEL=INFO
GOOGLE_OAUTH_PORT=62366
```

### Step 4: Google Cloud Console Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one
   - Note your project ID

2. **Enable Gmail API**
   ```bash
   # Using gcloud CLI (optional)
   gcloud services enable gmail.googleapis.com --project=your-project-id
   ```

3. **Create OAuth 2.0 Credentials**
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop application"
   - Add authorized redirect URI: `http://localhost:62366`

4. **Download Credentials**
   - Download the `credentials.json` file
   - Place it in: `src/meeting_minutes/crews/gmailcrew/tools/credentials.json`

### Step 5: Audio File Preparation

```bash
# Place your audio file in the source directory
cp /path/to/your/meeting.wav src/meeting_minutes/EarningsCall.wav

# Supported formats: WAV, MP3, M4A, FLAC
# Maximum recommended size: 100MB
```

### Step 6: Development Setup (Optional)

For contributors and developers:

```bash
# Install pre-commit hooks
pre-commit install

# Run initial code quality check
pre-commit run --all-files

# Verify installation
python -m pytest tests/ -v  # Run tests (if available)
```

---

## ⚙️ Configuration

### Application Configuration

The application uses centralized configuration in `src/meeting_minutes/config/app_config.py`:

```python
# Example configuration customization
PROCESSING_CONFIG = {
    "audio": {
        "chunk_length_ms": 60000,  # 1 minute chunks
        "supported_formats": ["wav", "mp3", "m4a", "flac"],
        "max_file_size_mb": 100,
    },
    "transcription": {
        "cleanup_temp_files": True,
        "retry_attempts": 3,
        "retry_delay": 1.0,
    }
}
```

### Local LLM Server Configuration

Update server settings based on your setup:

```python
LLM_SERVER = {
    "base_url": "http://localhost:11434",  # Ollama default
    "model_name": "llama2",
    "api_key": "not-needed"
}
```

**Common Server URLs:**
- **Ollama**: `http://localhost:11434`
- **LocalAI**: `http://localhost:8080`
- **Text-gen WebUI**: `http://localhost:5000`
- **LM Studio**: `http://localhost:1234`

---

## 🎯 Usage

### Basic Usage

```bash
# Run the complete pipeline
python src/meeting_minutes/main.py
```

The application will:
1. 🎤 Transcribe your audio file using ElevenLabs
2. 🤖 Generate structured meeting minutes with AI
3. 📧 Create a Gmail draft with the results

### Advanced Usage

#### Testing Components Individually

```bash
# Test Gmail authentication
python test_gmail_auth.py

# Test local LLM connection
python -c "from src.meeting_minutes.utils.monkey_patches import debug_local_server; debug_local_server()"

# Validate audio file
python -c "
from src.meeting_minutes.utils.audio_processor import AudioProcessor
processor = AudioProcessor()
info = processor.get_audio_info('src/meeting_minutes/EarningsCall.wav')
print(info)
"
```

#### Custom Audio Processing

```python
from meeting_minutes.utils.audio_processor import AudioProcessor

processor = AudioProcessor()

# Get audio information
info = processor.get_audio_info("meeting.wav")
print(f"Duration: {info['duration_formatted']}")
print(f"Estimated chunks: {info['estimated_chunks']}")

# Process audio in chunks
for chunk_index, audio_data in processor.chunk_generator("meeting.wav"):
    print(f"Processing chunk {chunk_index}")
    # Your custom processing here
```

---

## 📞 Contact & Connect

### 👨‍💻 About the Me

**Osama Mohamed** - AI/ML Engineer & Developer

### 🌐 Professional Profiles

<div align="center">

[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/osamam0)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-FFD21E?style=for-the-badge)](https://huggingface.co/OsamaMo)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/osamam0)

</div>

### 💬 Get in Touch

- **💡 Project Collaborations** - Open to AI/ML partnerships and innovative projects
- **🎓 Mentoring & Consulting** - Available for AI implementation guidance
- **🔧 Technical Support** - Feel free to reach out for project-specific questions

<div align="center">

**"Building the future of AI, one intelligent system at a time"**

---

*Made with ❤️ and ☕ by [Osama Mohamed](https://linkedin.com/in/osamam0)*

</div>
