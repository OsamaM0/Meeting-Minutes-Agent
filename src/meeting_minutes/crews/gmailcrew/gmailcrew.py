import os

# Force API key to be consistent
os.environ["OPENAI_API_KEY"] = "sk-111222333444555666777888999000"

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Import the agent factory
from meeting_minutes.utils.llm_agent_factory import create_agent_from_config

from .tools.gmail_tool import GmailTool


@CrewBase
class GmailCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def gmail_draft_agent(self) -> Agent:
        return create_agent_from_config(
            config=self.agents_config["gmail_draft_agent"], tools=[GmailTool()]
        )

    @task
    def gmail_draft_task(self) -> Task:
        return Task(
            config=self.tasks_config["gmail_draft_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
