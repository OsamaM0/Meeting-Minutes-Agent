# Port Configuration for CrewAI Application

This document explains how to configure the application to work with a specific port (http://localhost:62366).

## Configuration

The application uses port 62366 for:

1. LLM server communication
2. Google OAuth authentication callback

All port configurations are centralized in `src/meeting_minutes/config/app_config.py`.

## Changing the Port

If you need to use a different port:

1. Open `src/meeting_minutes/config/app_config.py`
2. Update the port numbers in both the `LLM_SERVER` and `GOOGLE_OAUTH` settings
3. Update your Google Cloud Console OAuth credentials to allow the new redirect URI

## Testing the Connection

To test if your local LLM server is correctly configured with the port:

```bash
python test_local_llm.py
```

This will run tests against your configured LLM server to ensure it's working properly.
