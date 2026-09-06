from src.patterns.dynamic_sharding.delegates import Delegate
from src.patterns.dynamic_sharding.agent import Agent
from src.commons.message import Message
from src.config.logging import logger
from typing import List
import asyncio


class Coordinator(Agent):
    """
    An agent that coordinates the processing of a list of entities by sharding
    the list and dynamically creating sub-agents to process each shard in parallel.

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
        Processes the incoming message containing entities and shard size,
        shards the list, creates sub-agents dynamically, and collects the results.

        Args:
            message (Message): The incoming message containing the list and shard size.

        Returns:
            Message: A message containing the consolidated entity information.
        """
        logger.info(f"{self.name} processing message.")
        try:
            # Extract the list of entities and shard size from the message
            data = message.content
            entities: List[str] = data.get('entities', [])
            shard_size: int = data.get('shard_size', 1)

            if not entities:
                raise ValueError("No entities provided.")

            # Shard the list
            shards = [entities[i:i + shard_size] for i in range(0, len(entities), shard_size)]
            logger.info(f"Sharded list into {len(shards)} shards.")

            # Note: You could also incorporate pre-processing logic here that uses Gemini or any LLM as a coordinating task. 

            # Create sub-agents dynamically and process shards in parallel
            tasks = []
            for idx, shard in enumerate(shards):
                agent_name = f"ShardProcessingAgent_{idx}"
                agent = Delegate(name=agent_name)
                task = asyncio.create_task(agent.process(Message(content=shard, sender=self.name, recipient=agent_name)))
                tasks.append(task)

            # Gather results from all sub-agents
            sub_responses = await asyncio.gather(*tasks)

            # Consolidate the results
            entity_info = [response.content for response in sub_responses if response.content]

            # Note: The coordinator doesn't use an LLM to post-process or consolidate responses from sub-agents (delegates). However, this feature could be implemented if desired.

            final_response = "\n\n".join(entity_info)

            return Message(content=final_response, sender=self.name, recipient=message.sender)
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return Message(
                content="An error occurred while processing the request.",
                sender=self.name,
                recipient=message.sender
            )