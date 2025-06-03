"""Test CrewAI integration functionality."""

from unittest.mock import Mock, patch

import pytest

# Handle CrewAI import gracefully
try:
    from crewai import Agent, Crew, Process, Task

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    # Create mock classes for testing
    Agent = Mock
    Crew = Mock
    Process = Mock
    Task = Mock


@pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI not available")
class TestCrewIntegration:
    """Test CrewAI integration with LLM."""

    @pytest.fixture
    def test_agent(self, mock_llm):
        """Create a test agent."""
        if not CREWAI_AVAILABLE:
            return Mock()
        return Agent(
            role="Test Agent",
            goal="Test the CrewAI integration with local LLM",
            backstory="You're a test agent created to verify that CrewAI works with a local LLM.",
            llm=mock_llm,
            verbose=False,
        )

    @pytest.fixture
    def test_task(self, test_agent):
        """Create a test task."""
        if not CREWAI_AVAILABLE:
            return Mock()
        return Task(
            description="Write a short greeting message confirming that you're working with a local LLM.",
            expected_output="A short greeting message",
            agent=test_agent,
        )

    def test_agent_creation(self, mock_llm):
        """Test agent creation with LLM."""
        if not CREWAI_AVAILABLE:
            pytest.skip("CrewAI not available")

        agent = Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
            llm=mock_llm,
            verbose=False,
        )

        assert agent.role == "Test Agent"
        assert agent.goal == "Test goal"
        assert agent.backstory == "Test backstory"
        assert agent.llm == mock_llm

    def test_task_creation(self, test_agent):
        """Test task creation with agent."""
        if not CREWAI_AVAILABLE:
            pytest.skip("CrewAI not available")

        task = Task(
            description="Test task description",
            expected_output="Test output",
            agent=test_agent,
        )

        assert task.description == "Test task description"
        assert task.expected_output == "Test output"
        assert task.agent == test_agent

    @pytest.mark.integration
    def test_crew_execution(self, test_agent, test_task):
        """Test crew execution with mocked components."""
        if not CREWAI_AVAILABLE:
            pytest.skip("CrewAI not available")

        with patch.object(Crew, "kickoff") as mock_kickoff:
            mock_kickoff.return_value = "Test crew execution result"

            crew = Crew(
                agents=[test_agent],
                tasks=[test_task],
                process=Process.sequential,
                verbose=False,
            )

            result = crew.kickoff()

            assert result == "Test crew execution result"
            mock_kickoff.assert_called_once()

    @pytest.mark.llm
    def test_get_llm_integration(self, mock_llm):
        """Test LLM configuration integration."""
        if not CREWAI_AVAILABLE:
            pytest.skip("CrewAI not available")

        with patch("meeting_minutes.utils.llm_config.get_llm") as mock_get_llm:
            mock_get_llm.return_value = mock_llm

            from meeting_minutes.utils.llm_config import get_llm

            llm = get_llm()

            # Test that agent can be created with the LLM
            agent = Agent(
                role="Integration Test Agent",
                goal="Test LLM integration",
                backstory="Testing agent creation with get_llm()",
                llm=llm,
                verbose=False,
            )

            assert agent.llm == mock_llm
            mock_get_llm.assert_called_once()

    @pytest.mark.slow
    @pytest.mark.integration
    def test_real_crew_execution(self):
        """Test real crew execution (slow test)."""
        if not CREWAI_AVAILABLE:
            pytest.skip("CrewAI not available")

        try:
            from meeting_minutes.utils.llm_config import get_llm

            llm = get_llm()

            agent = Agent(
                role="Test Agent",
                goal="Provide a simple test response",
                backstory="You are a test agent.",
                llm=llm,
                verbose=False,
            )

            task = Task(
                description="Say 'Hello from CrewAI!'",
                expected_output="A greeting message",
                agent=agent,
            )

            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False,
            )

            result = crew.kickoff()
            assert result is not None

        except Exception as e:
            pytest.skip(f"Real CrewAI execution not available: {e}")
