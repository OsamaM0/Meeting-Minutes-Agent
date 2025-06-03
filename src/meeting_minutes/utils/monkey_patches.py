"""
Monkey patches for the CrewAI library to make it work with local LLM endpoints.
"""

from config.app_config import LLM_SERVER


def apply_monkey_patches():
    """Apply all needed monkey patches to make CrewAI work with local LLMs."""
    _patch_crewai_llm()
    _patch_litellm()
    _patch_openai()


def _patch_crewai_llm():
    """Patch CrewAI's LLM class to bypass API key validation."""
    try:
        from crewai.llm import LLM

        # Store original init
        original_init = LLM.__init__

        # Create patched init
        def patched_init(self, *args, **kwargs):
            # Force local configuration
            kwargs["api_key"] = LLM_SERVER["api_key"]
            kwargs["base_url"] = LLM_SERVER["base_url"]

            # Remove env_var to prevent lookup
            if "env_var" in kwargs:
                kwargs.pop("env_var")

            # Call original init
            return original_init(self, *args, **kwargs)

        # Apply patch
        LLM.__init__ = patched_init
        print("✅ CrewAI LLM initialization patched successfully")
    except Exception as e:
        print(f"❌ Failed to patch CrewAI LLM: {e}")


def _patch_litellm():
    """Patch LiteLLM to bypass API key validation and add debugging."""
    try:
        import litellm
        import litellm.utils

        # Enable debugging
        litellm.set_verbose = True

        # Patch completion function to use local endpoint
        original_completion = litellm.completion

        def patched_completion(*args, **kwargs):
            # Debug: Print what we're trying to call
            print(f"🔍 LiteLLM Debug - Original kwargs: {kwargs}")

            # Force local configuration
            kwargs["api_key"] = LLM_SERVER["api_key"]
            kwargs["base_url"] = LLM_SERVER["base_url"]

            # Try different model names that might work with local server
            original_model = kwargs.get("model", "gpt-4o")
            model_alternatives = [
                original_model,
                "gpt-4",
                "gpt-3.5-turbo",
                "text-davinci-003",
                "llama",
                "local-model",
            ]

            last_error = None
            for model_name in model_alternatives:
                try:
                    kwargs["model"] = model_name
                    print(f"🔍 Trying model: {model_name} at {kwargs['base_url']}")

                    # Add custom headers that might be needed
                    if "extra_headers" not in kwargs:
                        kwargs["extra_headers"] = {}
                    kwargs["extra_headers"]["Content-Type"] = "application/json"

                    response = original_completion(*args, **kwargs)
                    print(f"✅ Success with model: {model_name}")
                    return response

                except Exception as e:
                    last_error = e
                    print(f"❌ Failed with model {model_name}: {str(e)}")
                    continue

            # If all models failed, provide detailed error info
            print(f"🚨 All model attempts failed. Last error: {last_error}")
            print(f"🔍 Server URL: {kwargs['base_url']}")
            print(
                f"🔍 Available at server: Check if your local LLM server is running at {kwargs['base_url']}"
            )

            # Try to make a simple request to check if server is alive
            try:
                import requests

                health_check = requests.get(
                    f"{kwargs['base_url'].rstrip('/')}/health", timeout=5
                )
                print(f"🔍 Server health check: {health_check.status_code}")
            except Exception as health_error:
                print(f"🚨 Server appears to be down: {health_error}")

            raise last_error

        # Apply patch
        litellm.completion = patched_completion
        print("✅ LiteLLM completion function patched successfully")
    except Exception as e:
        print(f"❌ Failed to patch LiteLLM: {e}")


def _patch_openai():
    """Patch OpenAI to bypass API key validation."""
    try:
        import openai

        # Store original init
        if hasattr(openai, "OpenAI"):
            original_init = openai.OpenAI.__init__

            # Create patched init
            def patched_init(self, *args, **kwargs):
                # Force local configuration
                kwargs["api_key"] = LLM_SERVER["api_key"]
                kwargs["base_url"] = LLM_SERVER["base_url"]

                # Call original init
                return original_init(self, *args, **kwargs)

            # Apply patch
            openai.OpenAI.__init__ = patched_init
            print("✅ OpenAI client patched successfully")
    except Exception as e:
        print(f"❌ Failed to patch OpenAI: {e}")


def debug_local_server():
    """Debug function to test local LLM server connectivity."""
    import requests
    from config.app_config import LLM_SERVER

    base_url = LLM_SERVER["base_url"]
    print(f"🔍 Testing local LLM server at: {base_url}")

    # Test endpoints that local LLM servers commonly expose
    test_endpoints = ["/health", "/v1/models", "/models", "/api/v1/models", "/"]

    for endpoint in test_endpoints:
        try:
            url = f"{base_url.rstrip('/')}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"✅ {endpoint}: {response.status_code} - {response.text[:100]}")

            if (
                endpoint in ["/v1/models", "/models", "/api/v1/models"]
                and response.status_code == 200
            ):
                try:
                    models = response.json()
                    print(f"🔍 Available models: {models}")
                except:
                    pass

        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")
