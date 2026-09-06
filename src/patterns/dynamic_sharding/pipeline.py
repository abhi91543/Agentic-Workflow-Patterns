from src.patterns.dynamic_sharding.coordinator import Coordinator
from src.commons.message import Message
from src.config.logging import logger
import asyncio


# Paths for input and output files
INPUT_FILE = "./data/patterns/dynamic_sharding/entities.txt"
OUTPUT_FILE = "./data/patterns/dynamic_sharding/entity_info.txt"

async def pipeline() -> None:
    """
    Main function to initialize the coordinator, process entities, 
    and save the consolidated information to an output file.
    """
    # Initialize the coordinator agent
    coordinator = Coordinator(name="CoordinatorAgent")

    # Read entities from the input file
    with open(INPUT_FILE, 'r') as file:
        entities = [line.strip() for line in file.readlines()]

    shard_size = 3  # Number of entities per shard

    # Create a message containing entities and shard size
    message_content = {
        'entities': entities,
        'shard_size': shard_size
    }
    message = Message(content=message_content, sender="User", recipient="CoordinatorAgent")

    # Process the message through the coordinator and get the response
    response = await coordinator.process(message)

    # Save the consolidated response content to the output file
    with open(OUTPUT_FILE, 'w') as file:
        file.write(response.content)

    logger.info(f"Entity information has been saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    # Execute the pipeline within an asynchronous event loop
    asyncio.run(pipeline())
