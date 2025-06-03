"""
Custom wrapper for CrewAI to ensure it uses our local LLM configuration.
This prevents CrewAI from attempting to authenticate with OpenAI's API.
"""

import os

from crewai import Agent

from meeting_minutes.utils.llm_config import get_llm


def create_agent_with_local_llm(agent_config, tools=None):
    """
    Create a CrewAI agent with the local LLM configuration.

    Args:
        agent_config: Agent configuration from the YAML file
        tools: Optional tools for the agent

    Returns:
        CrewAI Agent instance
    """
    # Force API key to be consistent
    os.environ["OPENAI_API_KEY"] = "sk-111222333444555666777888999000"

    # Get the local LLM
    llm = get_llm()

    # Create agent with the local LLM
    if tools:
        return Agent(config=agent_config, tools=tools, llm=llm, verbose=True)
    else:
        return Agent(config=agent_config, llm=llm, verbose=True)
