import dotenv

# .env load
dotenv.load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew
from tools import search_tool, scrape_tool


"""
 Crew : agent들의 그롭
 여러 agent들이 모여 특정 task들을  같이 수행하는 협업그룹

 Agent : 독립적으로 움직이는 존재.
 - 자기 role과 goal에 따라 task를 수행하고 의사결정
 - 목적 달성을 위해 tools 사용

"""

@CrewBase
class NewsReaderAgent:
    ##---  agent -------------------------------------------#
    @agent
    def news_hunter_agent(self):
        return Agent(
            config=self.agents_config["news_hunter_agent"],
            tools=[search_tool, scrape_tool],
        )

    @agent
    def summarizer_agent(self):
        return Agent(
            config=self.agents_config["summarizer_agent"],
            tools=[scrape_tool,],
        )

    @agent
    def curator_agent(self):
        return Agent(
            config=self.agents_config["curator_agent"],
        )

    ##--- task -------------------------------------------#
    @task
    def content_harvesting_task(self):
        return Task(
            config=self.tasks_config["content_harvesting_task"],
        )

    @task
    def summarization_task(self):
        return Task(
            config=self.tasks_config["summarization_task"],
        )

    @task
    def final_report_assembly_task(self):
        return Task(
            config=self.tasks_config["final_report_assembly_task"],
        )

    @crew
    def crew(self):
        return Crew(
            tasks=self.tasks,
            agents=self.agents,
            verbose=True,
        )

## 연결 확인용
# NewsReaderAgent().crew().kickoff()

result = NewsReaderAgent().crew().kickoff(
    inputs={
        "topic": "월드컵."
    }
)

for task_output in result.tasks_output:
    print(task_output)