"""
LLM configuration for the application.
"""

from langchain_community.chat_models import ChatOpenAI

from ..config.app_config import LLM_SERVER
from .skip_validation_wrapper import SkipValidationWrapper


def get_llm():
    """
    Returns a configured LLM instance using a local API endpoint.
    """
    # Configure LLM to use local endpoint - no need for API key for local server
    llm = ChatOpenAI(
        model_name="gpt-4o",
        base_url=LLM_SERVER["base_url"],
        api_key=LLM_SERVER["api_key"],
        temperature=0.7,
        streaming=False,
    )

    # Wrap LLM to skip validation
    return SkipValidationWrapper(llm)
