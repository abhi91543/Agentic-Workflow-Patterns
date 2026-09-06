from coordinator import CoordinatorAgent
from src.commons.message import Message
from src.config.logging import logger
import asyncio


class Config:
    """
    Static class to hold configuration paths for input and output files.
    """
    PATTERN_ROOT_PATH = './data/patterns/task_decomposition'
    INPUT_FILE = f'{PATTERN_ROOT_PATH}/sample_doc.txt'
    OUTPUT_FILE = f'{PATTERN_ROOT_PATH}/extracted_info.md'


async def pipeline():
    # Initialize the coordinator agent
    coordinator = CoordinatorAgent(name="CoordinatorAgent")

    # Read the document content from the file
    with open(Config.INPUT_FILE, 'r') as file:
        document_content = file.read()

    # Define the task input (document content)
    task_input = document_content

    # Create the message with the task input
    message = Message(content=task_input, sender="User", recipient="CoordinatorAgent")

    # Process the message and get the final result (async call to CoordinatorAgent)
    response = await coordinator.process(message)

    # Save the extracted information to a file
    with open(Config.OUTPUT_FILE, 'w') as output_file:
        output_file.write(response.content)

    # Print the final extracted result
    logger.info("Extraction completed. The extracted information has been saved to 'extracted_info.md'.")


if __name__ == "__main__":
    # Run the pipeline to process the document
    asyncio.run(pipeline())
