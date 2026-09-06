from src.patterns.web_access.summarize import WebContentSummarizeAgent
from src.patterns.web_access.search import WebSearchAgent
from src.patterns.web_access.scrape import WebScrapeAgent
from src.patterns.web_access.tasks import SummarizeTask
from src.patterns.web_access.tasks import SearchTask
from src.patterns.web_access.tasks import ScrapeTask
from src.config.logging import logger


class TaskFactory:
    """
    Factory class to create instances of various web-related tasks.
    This class encapsulates the logic for creating different tasks, such as search, scrape, and summarize.
    """

    @staticmethod
    def create_search_task() -> SearchTask:
        """
        Creates and returns a new SearchTask instance using WebSearchAgent.

        Returns:
            SearchTask: An instance of the SearchTask class, implemented by WebSearchAgent.
        """
        try:
            logger.info("Creating search task (WebSearchAgent).")
            return WebSearchAgent()
        except Exception as e:
            logger.error(f"Error while creating search task: {str(e)}")
            raise

    @staticmethod
    def create_scrape_task() -> ScrapeTask:
        """
        Creates and returns a new ScrapeTask instance using WebScrapeAgent.

        Returns:
            ScrapeTask: An instance of the ScrapeTask class, implemented by WebScrapeAgent.
        """
        try:
            logger.info("Creating scrape task (WebScrapeAgent).")
            return WebScrapeAgent()
        except Exception as e:
            logger.error(f"Error while creating scrape task: {str(e)}")
            raise

    @staticmethod
    def create_summarize_task() -> SummarizeTask:
        """
        Creates and returns a new SummarizeTask instance using WebContentSummarizeAgent.

        Returns:
            SummarizeTask: An instance of the SummarizeTask class, implemented by WebContentSummarizeAgent.
        """
        try:
            logger.info("Creating summarize task (WebContentSummarizeAgent).")
            return WebContentSummarizeAgent()
        except Exception as e:
            logger.error(f"Error while creating summarize task: {str(e)}")
            raise
