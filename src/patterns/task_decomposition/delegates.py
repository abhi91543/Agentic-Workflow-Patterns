from src.patterns.task_decomposition.agent import Agent
from src.llm.generate import ResponseGenerator
from src.commons.message import Message
from src.config.logging import logger
import asyncio


class SubTaskAgent(Agent):
    """
    An agent that processes a specific subtask of the document extraction
    by invoking an LLM to extract the required information.
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the SubTaskAgent.
        """
        super().__init__(name)
        logger.info(f"{self.name} initialized.")

    async def process(self, message: Message) -> Message:
        """
        Processes the assigned subtask of the document by calling the LLM.
        """
        logger.info(f"{self.name} processing subtask.")
        subtask = message.content

        # Extract the document and task from the subtask
        document = subtask.get("document")
        task = subtask.get("task")

        if not document or not task:
            return Message(
                content="Invalid subtask: Missing document or task.",
                sender=self.name,
                recipient=message.sender
            )

        # Prepare the LLM input
        llm_input = f"Document:\n{document}\n\nTask: {task}"
        logger.info(f"Calling LLM for task: {task}")

        try:
            response_generator = ResponseGenerator()

            # Define a blocking function to be run in a separate thread
            def blocking_call():
                return response_generator.generate_response(
                    model_name='gemini-1.5-flash-001',
                    system_instruction='',
                    contents=[llm_input]
                ).text.strip()

            # Run the blocking LLM call in a separate thread
            extraction_result = await asyncio.to_thread(blocking_call)

        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            extraction_result = f"Failed to extract information for task: {task}"

        # Return the extraction result as a message
        return Message(
            content=extraction_result,
            sender=self.name,
            recipient=message.sender
        )
