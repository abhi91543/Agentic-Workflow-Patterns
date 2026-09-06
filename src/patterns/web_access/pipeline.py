from src.patterns.web_access.factory import TaskFactory
from src.config.logging import logger
from typing import Optional
import shutil
import os


class Pipeline:
    """
    Pipeline class that orchestrates the execution of search, scrape, and summarize tasks.
    
    Attributes:
        _search_task: Task instance responsible for performing search operations.
        _scrape_task: Task instance responsible for scraping data from search results.
        _summarize_task: Task instance responsible for summarizing the scraped content.
        _output_folders: List of folders for output files related to each task.
    """
    def __init__(self):
        self._search_task = TaskFactory.create_search_task()
        self._scrape_task = TaskFactory.create_scrape_task()
        self._summarize_task = TaskFactory.create_summarize_task()
        self._output_folders = [
            './data/patterns/web_access/output/search',
            './data/patterns/web_access/output/scrape',
            './data/patterns/web_access/output/summarize'
        ]

    def _flush_output_folders(self):
        """
        Flushes all files in the output folders before starting the pipeline.
        Ensures a clean start for each execution by removing previous results.
        """
        for folder in self._output_folders:
            try:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    logger.info(f"Flushed output folder: {folder}")
                else:
                    logger.warning(f"Output folder does not exist: {folder}")
            except Exception as e:
                logger.error(f"Error flushing folder {folder}: {str(e)}")

    def execute(self, model_name: str, query: str, location: str = '') -> str:
        """
        Executes the pipeline: search, scrape, and summarize tasks sequentially.

        Args:
            model_name (str): The model to be used for summarization.
            query (str): The search query to process.
            location (str): Optional location context for search and scrape tasks.

        Returns:
            str: A summary generated from the search results.

        Raises:
            Exception: If any task fails, the error is logged and re-raised.
        """
        try:
            # logger.info(f"Starting pipeline execution for query: '{query}' with model: '{model_name}' and location: '{location}'.")
            self._flush_output_folders()

            logger.info("Executing search task.")
            self._search_task.run(model_name, query, location)

            logger.info("Executing scrape task.")
            self._scrape_task.run(query, location)

            logger.info("Executing summarize task.")
            summary = self._summarize_task.run(model_name, query)

            logger.info("Pipeline execution completed successfully.")
            return summary

        except Exception as e:
            logger.error(f"An error occurred during pipeline execution: {e}", exc_info=True)
            raise


def run(query: str, model_name: Optional[str] = 'gemini-1.5-flash-001') -> str:
    """
    Initializes and runs the pipeline to generate a summary for the given query.

    Args:
        query (str): The search query to process.
        model_name (Optional[str]): The model used for summarization. Defaults to 'gemini-1.5-pro-001'.

    Returns:
        str: The generated summary from the pipeline.

    Raises:
        Exception: Logs and re-raises any error during pipeline execution.
    """
    try:
        logger.info(f"Starting pipeline for query: {query} with model: {model_name}")
        pipeline = Pipeline()
        summary = pipeline.execute(model_name, query)
        logger.info("Pipeline run successfully completed.")
        return summary
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        raise


if __name__ == '__main__':
    query = 'best hotels in Fresno, California'
    summary = run(query)
    logger.info(f"Generated Summary: {summary}")
