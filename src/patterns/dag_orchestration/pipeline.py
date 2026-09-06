from src.patterns.dag_orchestration.coordinator import CoordinatorAgent
from src.commons.message import Message
from src.config.logging import logger
from typing import Any
import asyncio
import json


class Config:
    """
    Configuration class to hold the paths for DAG file and final report file.
    """
    PATTERN_ROOT_PATH = './data/patterns/dag_orchestration'
    DAG_FILE_PATH = f"{PATTERN_ROOT_PATH}/dag.yml"
    REPORT_FILE_PATH = f"{PATTERN_ROOT_PATH}/final_report.json"


async def pipeline() -> None:
    """
    Main pipeline function to orchestrate task processing using the Coordinator agent.
    This function processes a main task message and saves the final output to a JSON file.

    Steps:
    1. Initializes the Coordinator with a specified DAG file.
    2. Sends a main task message to the Coordinator for processing.
    3. Receives the response and extracts the content.
    4. Saves the final content as a JSON report.

    Returns:
        None
    """
    try:
        logger.info("Initializing the Coordinator agent with the DAG file.")
        coordinator = CoordinatorAgent(name="CoordinatorAgent", dag_file=Config.DAG_FILE_PATH)

        # The main task is to orchestrate the DAG, hence no specific content is needed for the message.
        message = Message(content='', sender="User", recipient="CoordinatorAgent")

        logger.info("Sending the main task message to the Coordinator for processing.")
        response = await coordinator.process(message)

        final_output = response.content
        save_final_report(final_output)

        logger.info("Task completed successfully. The final report has been saved.")

    except Exception as e:
        logger.error(f"An error occurred during the pipeline execution: {e}")
        raise


def save_final_report(report_data: Any) -> None:
    """
    Saves the final processed output to a JSON file.

    Args:
        report_data (Any): The processed output content to be saved.

    Returns:
        None
    """
    try:
        with open(Config.REPORT_FILE_PATH, 'w') as output_file:
            json.dump(report_data, output_file, indent=2)
        logger.info(f"Final report saved successfully at {Config.REPORT_FILE_PATH}.")

    except (OSError, json.JSONDecodeError) as save_error:
        logger.error(f"Failed to save the final report: {save_error}")
        raise


if __name__ == "__main__":
    """
    Entry point of the script.
    """
    logger.info("Starting the pipeline.")
    asyncio.run(pipeline())
    logger.info("Pipeline execution completed.")
