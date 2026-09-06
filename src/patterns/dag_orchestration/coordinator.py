from src.patterns.dag_orchestration.agent import Agent
from src.commons.message import Message
from src.config.logging import logger
from typing import Optional, List, Dict, Any
import importlib
import traceback
import asyncio
import yaml
import json
import os


class Config:
    """
    Configuration class to hold the paths for DAG files and trace directory.
    """
    PATTERN_ROOT_PATH = './data/patterns/dag_orchestration'
    DAG_FILE_PATH = f"{PATTERN_ROOT_PATH}/dag.yml"
    TRACE_DIR = f"{PATTERN_ROOT_PATH}/trace"


class CoordinatorAgent(Agent):
    """
    A coordinator agent responsible for executing a Directed Acyclic Graph (DAG) of tasks
    using various sub-agents. The agent manages task execution, dependencies, and states.
    """

    def __init__(self, name: str, dag_file: str = Config.DAG_FILE_PATH) -> None:
        """
        Initializes the CoordinatorAgent with the specified name and DAG file.
        
        Args:
            name (str): The name of the coordinator agent.
            dag_file (str): Path to the YAML file defining the DAG.
        """
        super().__init__(name)
        self.dag_file = dag_file
        self.tasks = {}
        self.task_results = {}
        self.task_states = {}
        self._load_dag()
        logger.info(f"{self.name} initialized with DAG from {dag_file}.")

    async def process(self, message: Message) -> Message:
        """
        Processes the incoming message and executes the DAG.
        
        Args:
            message (Message): The input message for the coordinator.

        Returns:
            Message: The final output message after executing the DAG.
        """
        logger.info(f"{self.name} processing message.")
        try:
            await self._execute_dag()
            final_task_id = self._find_final_task()
            final_output = self.task_results.get(final_task_id, "No final output generated.")
            return Message(content=final_output, sender=self.name, recipient=message.sender)
        except Exception as e:
            logger.error(f"Error during processing: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Message(
                content="An error occurred while processing the task.",
                sender=self.name,
                recipient=message.sender
            )

    def _load_dag(self) -> None:
        """
        Loads the DAG definition from the specified YAML file.
        """
        with open(self.dag_file, 'r') as file:
            dag_data = yaml.safe_load(file)
            for task_data in dag_data.get('tasks', []):
                task_id = task_data['id']
                self.tasks[task_id] = task_data
                self.task_states[task_id] = 'pending'
                logger.info(f"Task {task_id} loaded: {task_data['description']}")

    async def _execute_dag(self) -> None:
        """
        Executes the tasks defined in the DAG based on their dependencies.
        """
        pending_tasks = set(self.tasks.keys())
        while pending_tasks:
            executable_tasks = self._find_executable_tasks(pending_tasks)
            if not executable_tasks:
                logger.error("No executable tasks found. Possible circular dependency.")
                break

            tasks = []
            for task_id in executable_tasks:
                task_data = self.tasks[task_id]
                agent = self._create_agent(task_data['agent'], task_data['name'])
                input_data = self._collect_inputs(task_data['dependencies'])
                sub_message = Message(content=input_data, sender=self.name, recipient=agent.name)
                task = asyncio.create_task(self._run_task(task_id, agent, sub_message))
                tasks.append(task)
                pending_tasks.remove(task_id)
                self.task_states[task_id] = 'running'

            await asyncio.gather(*tasks)

    def _find_executable_tasks(self, pending_tasks: set) -> List[str]:
        """
        Finds tasks that can be executed based on their dependencies.

        Args:
            pending_tasks (set): The set of tasks that are yet to be executed.

        Returns:
            List[str]: A list of task IDs that can be executed.
        """
        return [task_id for task_id in pending_tasks if self._can_execute(task_id)]

    def _can_execute(self, task_id: str) -> bool:
        """
        Checks if a task can be executed based on its dependencies.

        Args:
            task_id (str): The ID of the task to check.

        Returns:
            bool: True if all dependencies are satisfied, False otherwise.
        """
        dependencies = self.tasks[task_id]['dependencies']
        return all(dep in self.task_results for dep in dependencies)

    def _collect_inputs(self, dependencies: list) -> Dict[str, Any]:
        """
        Collects input data based on the dependencies of a task.

        Args:
            dependencies (list): List of dependent task IDs.

        Returns:
            Dict[str, Any]: Collected input data for the task.
        """
        if not dependencies:
            return {}
        elif len(dependencies) == 1:
            dep = dependencies[0]
            return self.task_results[dep]
        else:
            return {dep: self.task_results[dep] for dep in dependencies}

    async def _run_task(self, task_id: str, agent: Agent, message: Message) -> None:
        """
        Runs a single task using the specified agent and message.

        Args:
            task_id (str): The ID of the task to run.
            agent (Agent): The agent responsible for processing the task.
            message (Message): The message containing the input data.
        """
        logger.info(f"Starting task {task_id}: {agent.name}")
        try:
            result_message = await agent.process(message)
            self.task_results[task_id] = result_message.content
            self.task_states[task_id] = 'completed'
            self._log_task_result(task_id, result_message.content)
            logger.info(f"Completed task {task_id}: {agent.name}")
        except Exception as e:
            self.task_states[task_id] = 'failed'
            logger.error(f"Task {task_id} failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")

    def _create_agent(self, agent_class_name: str, agent_name: str) -> Agent:
        """
        Dynamically creates an agent based on the agent class name.

        Args:
            agent_class_name (str): The class name of the agent.
            agent_name (str): The name of the agent instance.

        Returns:
            Agent: An instance of the specified agent class.
        """
        agent_module_map = {
            'CollectAgent': 'collect',
            'PreprocessAgent': 'preprocess',
            'ExtractAgent': 'extract',
            'CompileAgent': 'compile',
            'SummarizeAgent': 'summarize',
        }

        module_name = agent_module_map.get(agent_class_name)
        if not module_name:
            raise ImportError(f"No module found for agent class '{agent_class_name}'")

        try:
            module = importlib.import_module(f'src.patterns.dag_orchestration.agents.{module_name}')
            agent_class = getattr(module, agent_class_name)
            return agent_class(name=agent_name)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(f"Could not create agent '{agent_class_name}' from module '{module_name}': {e}")

    def _find_final_task(self) -> Optional[str]:
        """
        Finds the final task in the DAG that has no dependents.

        Returns:
            Optional[str]: The ID of the final task, or None if not found.
        """
        all_tasks = set(self.tasks.keys())
        dependent_tasks = {dep for task in self.tasks.values() for dep in task['dependencies']}
        final_tasks = all_tasks - dependent_tasks
        return final_tasks.pop() if final_tasks else None

    def _log_task_result(self, task_id: str, result: Any) -> None:
        """
        Logs the result of a completed task to a JSON file.

        Args:
            task_id (str): The ID of the task whose result is being logged.
            result (Any): The result data to log.
        """
        os.makedirs(Config.TRACE_DIR, exist_ok=True)
        trace_file = f"{Config.TRACE_DIR}/{task_id}.json"

        with open(trace_file, 'w') as f:
            json.dump(result, f, indent=2)

        logger.info(f"Task result logged for {task_id} at {trace_file}.")
