import os
import sys

# Add the project's src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.insert(0, src_dir)

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileWriterTool

# Import the agent factory
from meeting_minutes.utils.llm_agent_factory import create_agent_from_config
from meeting_minutes.utils.llm_config import get_llm

file_writer_tool_summary = FileWriterTool(
    file_name="summary.txt", directory="meeting_minutes_text"
)
file_writer_tool_action_items = FileWriterTool(
    file_name="action_items.txt", directory="meeting_minutes_text"
)
file_writer_tool_sentiment = FileWriterTool(
    file_name="sentiment.txt", directory="meeting_minutes_text"
)


@CrewBase
class MeetingMinutesCrew:
    """Meeting Minutes Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = get_llm()

    @agent
    def meeting_minutes_summarizer(self) -> Agent:
        return create_agent_from_config(
            config=self.agents_config["meeting_minutes_summarizer"],
            tools=[
                file_writer_tool_summary,
                file_writer_tool_action_items,
                file_writer_tool_sentiment,
            ],
        )

    @agent
    def meeting_minutes_writer(self) -> Agent:
        return create_agent_from_config(
            config=self.agents_config["meeting_minutes_writer"]
        )

    @task
    def meeting_minutes_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["meeting_minutes_summary_task"],
        )

    @task
    def meeting_minutes_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["meeting_minutes_writing_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
