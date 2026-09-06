from src.patterns.dynamic_sharding.agent import Agent
from src.patterns.web_access.pipeline import run 
from src.commons.message import Message 
from src.config.logging import logger
from typing import List
import asyncio


class Delegate(Agent):
    """
    An agent that processes a shard of entities by fetching information
    using web research.

    Attributes:
        name (str): The name of the shard processing agent.
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the ShardProcessingAgent.

        Args:
            name (str): The name of the agent.
        """
        super().__init__(name)
        logger.info(f"{self.name} initialized.")

    async def process(self, message: Message) -> Message:
        """
        Processes the shard by fetching information for each entity in the shard.

        Args:
            message (Message): The message containing the shard (list of entities).

        Returns:
            Message: A message containing the concatenated information.
        """
        logger.info(f"{self.name} processing shard.")
        try:
            entities: List[str] = message.content
            tasks = []

            # Create tasks to fetch information for each entity
            for entity in entities:
                task = asyncio.create_task(self.fetch_entity_info(entity))
                tasks.append(task)

            # Gather information
            entity_info = await asyncio.gather(*tasks)
            shard_info = "\n\n".join(entity_info)

            return Message(content=shard_info, sender=self.name, recipient=message.sender)
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return Message(
                content="An error occurred while processing the shard.",
                sender=self.name,
                recipient=message.sender
            )

    async def fetch_entity_info(self, entity: str) -> str:
        """
        Fetches information about an entity using web search.

        Args:
            entity (str): The name of the entity.

        Returns:
            str: Information about the entity.
        """
        logger.info(f"{self.name} fetching information for {entity}.")
        try:
            # Use the run function to perform web search asynchronously
            info = await asyncio.to_thread(run, f"{entity} information")
            return f"Information about {entity}:\n{info}"
        except Exception as e:
            logger.error(f"Error fetching information for {entity}: {e}")
            return f"Could not fetch information for {entity}."