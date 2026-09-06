from src.patterns.task_decomposition.delegates import SubTaskAgent
from src.patterns.task_decomposition.agent import Agent
from src.commons.message import Message
from src.config.logging import logger
from typing import List
from typing import Any 
import asyncio


class CoordinatorAgent(Agent):
    """
    An agent that coordinates the processing of a document by decomposing it
    into extraction subtasks and assigning them to sub-agents to execute in parallel.

    Attributes:
        name (str): The name of the coordinator agent.
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the CoordinatorAgent.

        Args:
            name (str): The name of the agent.
        """
        super().__init__(name)
        logger.info(f"{self.name} initialized.")

    async def process(self, message: Message) -> Message:
        """
        Processes the incoming message containing the document input,
        decomposes it into subtasks, assigns them to sub-agents, and
        collects the results concurrently.

        Args:
            message (Message): The incoming message containing the document input.

        Returns:
            Message: A message containing the final combined result.
        """
        logger.info(f"{self.name} processing message.")
        try:
            document_content = message.content  # Assume message content is the document

            # Decompose the document into subtasks
            subtasks = self.decompose_task(document_content)

            # Create sub-agents and execute subtasks in parallel
            tasks = []
            for idx, subtask in enumerate(subtasks):
                agent_name = f"SubTaskAgent_{idx}"
                agent = SubTaskAgent(name=agent_name)
                sub_message = Message(content=subtask, sender=self.name, recipient=agent_name)
                task = asyncio.create_task(agent.process(sub_message))
                tasks.append(task)

            # Gather results from all sub-agents concurrently
            sub_results = await asyncio.gather(*tasks)

            # Combine results into a structured summary
            combined_result = self.combine_results(sub_results)

            # Return the final message
            return Message(content=combined_result, sender=self.name, recipient=message.sender)

        except Exception as e:
            logger.error(f"Error during processing: {str(e)}")
            return Message(
                content="An error occurred while processing the document.",
                sender=self.name,
                recipient=message.sender
            )

    def decompose_task(self, document_content: str) -> List[dict]:
        """
        Decomposes the document into extraction subtasks.
        
        Args:
            document_content (str): The full text of the document.
        
        Returns:
            List[dict]: A list of subtasks, where each subtask is a dictionary containing
                        the document and the specific task to be performed.
        """
        # Generalized approach for task decomposition
        return [
            {"document": document_content, "task": "Extract all named entities (people, organizations, locations) and their roles or significance"},
            {"document": document_content, "task": "Identify and extract all direct quotations with speakers and context"},
            {"document": document_content, "task": "Extract all numerical data (dates, statistics, measurements) with descriptions"},
            {"document": document_content, "task": "Identify and extract key terms or concepts with their definitions or explanations"},
            {"document": document_content, "task": "Extract all references to external sources with available citation information"}
        ]

    def combine_results(self, sub_results: List[Any]) -> str:
        """
        Combines the results of the subtasks into a structured summary.
        
        Args:
            sub_results (List[Any]): The results of the subtasks from the sub-agents.
        
        Returns:
            str: A structured summary of the document.
        """
        summary = "Document Summary:\n"
        for result in sub_results:
            summary += f"{result.content}\n"
        return summary
