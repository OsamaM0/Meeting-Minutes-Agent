"""Factory for creating agents with local LLM configuration."""

from crewai import Agent

from meeting_minutes.utils.llm_config import get_llm


def create_local_agent(
    role, goal, backstory, tools=None, verbose=True, allow_delegation=True, **kwargs
):
    """
    Create an agent that uses the local LLM instead of OpenAI's API.

    Args:
        role: Agent role
        goal: Agent goal
        backstory: Agent backstory
        tools: List of tools agent can use
        verbose: Whether to enable verbose output
        allow_delegation: Whether to allow delegation
        **kwargs: Additional arguments for Agent constructor

    Returns:
        Agent configured with local LLM
    """
    # Get the LLM configured for local use
    local_llm = get_llm()

    # Create agent with specified parameters and local LLM
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools or [],
        verbose=verbose,
        allow_delegation=allow_delegation,
        llm=local_llm,
        **kwargs,
    )


def create_agent_from_config(config, tools=None, **kwargs):
    """
    Create an agent from configuration with local LLM.

    Args:
        config: Agent configuration dictionary
        tools: List of tools agent can use
        **kwargs: Additional arguments for Agent constructor

    Returns:
        Agent configured with local LLM and specified config
    """
    # Get the LLM configured for local use
    local_llm = get_llm()

    # Create agent with local LLM
    return Agent(
        config=config, tools=tools or [], llm=local_llm, verbose=True, **kwargs
    )
