from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from database_assistant.tools.postgres_schema_tool import PostgresSchemaTool
from database_assistant.tools.postgres_sql_executor import PostgresSQLExecutor
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class DatabaseAssistant():
    """DatabaseAssistant crew (full flow: intent, schema, mapping, SQL build, execution)"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def NLIntentAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['NLIntentAgent'],
            verbose=True
        )

    @agent
    def SchemaToolAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['SchemaToolAgent'],
            tools=[PostgresSchemaTool()],
            verbose=True
        )

    @agent
    def TableMappingAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['TableMappingAgent'],
            verbose=True
        )

    @agent
    def SQLBuilderAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['SQLBuilderAgent'],
            verbose=True
        )

    @agent
    def SQLExecutorAgent(self) -> Agent:
        return Agent(
            config=self.agents_config['SQLExecutorAgent'],
            tools=[PostgresSQLExecutor()],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def extract_intent(self) -> Task:
        return Task(
            config=self.tasks_config['extract_intent'],
        )

    @task
    def fetch_schema(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_schema'],
        )

    @task
    def map_tables(self) -> Task:
        return Task(
            config=self.tasks_config['map_tables'],
            # The schema can be passed as context or input if needed by CrewAI's API
        )

    @task
    def build_sql(self) -> Task:
        return Task(
            config=self.tasks_config['build_sql'],
        )

    @task
    def execute_sql(self) -> Task:
        return Task(
            config=self.tasks_config['execute_sql'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DatabaseAssistant crew (full flow)"""
        return Crew(
            agents=[
                self.NLIntentAgent(),
                self.SchemaToolAgent(),
                self.TableMappingAgent(),
                self.SQLBuilderAgent(),
                self.SQLExecutorAgent()
            ],
            tasks=[
                self.extract_intent(),
                self.fetch_schema(),
                self.map_tables(),
                self.build_sql(),
                self.execute_sql()
            ],
            process=Process.sequential,
            verbose=True,
        )
