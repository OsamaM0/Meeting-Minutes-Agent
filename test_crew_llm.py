"""
Test script to verify CrewAI with local LLM configuration is working.
This helps isolate any issues with the CrewAI and LLM integration.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Force API key to be consistent
os.environ["OPENAI_API_KEY"] = "sk-111222333444555666777888999000"

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

from crewai import Agent, Crew, Task, Process
from meeting_minutes.utils.llm_config import get_llm

def test_crew_with_local_llm():
    """Test CrewAI with local LLM."""
    
    # Get the configured LLM
    llm = get_llm()
    
    # Create a simple agent
    test_agent = Agent(
        role="Test Agent",
        goal="Test the CrewAI integration with local LLM",
        backstory="You're a test agent created to verify that CrewAI works with a local LLM.",
        llm=llm,
        verbose=True
    )
    
    # Create a simple task
    test_task = Task(
        description="Write a short greeting message confirming that you're working with a local LLM.",
        expected_output="A short greeting message",
        agent=test_agent
    )
    
    # Create a crew with the agent and task
    test_crew = Crew(
        agents=[test_agent],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Run the crew
    print("Starting test crew with local LLM...")
    result = test_crew.kickoff()
    print("Crew execution completed!")
    print("Result:", result)
    return result

if __name__ == "__main__":
    test_crew_with_local_llm()
