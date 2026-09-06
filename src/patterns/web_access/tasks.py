from src.config.logging import logger
from abc import abstractmethod
from abc import ABC


class SearchTask(ABC):
    """
    Abstract base class for search tasks.
    
    Subclasses are required to implement the `run` method, which will define
    the specific behavior for executing a search task.
    """

    @abstractmethod
    def run(self, model_name: str, query: str) -> None:
        """
        Executes the search task with the given model and query.

        Args:
            model_name (str): The name of the model to be used for the search.
            query (str): The search query.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        logger.error("SearchTask run method not implemented.")
        raise NotImplementedError("Subclasses must implement the `run` method")


class ScrapeTask(ABC):
    """
    Abstract base class for scrape tasks.
    
    Subclasses are required to implement the `run` method, which will define
    the specific behavior for executing a scraping task.
    """

    @abstractmethod
    def run(self, model_name: str, query: str) -> None:
        """
        Executes the scrape task with the given model and query.

        Args:
            model_name (str): The name of the model to be used for scraping.
            query (str): The query or URL to be scraped.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        logger.error("ScrapeTask run method not implemented.")
        raise NotImplementedError("Subclasses must implement the `run` method")


class SummarizeTask(ABC):
    """
    Abstract base class for summarization tasks.
    
    Subclasses are required to implement the `run` method, which will define
    the specific behavior for executing a summarization task.
    """

    @abstractmethod
    def run(self, model_name: str, query: str) -> None:
        """
        Executes the summarization task with the given model and query.

        Args:
            model_name (str): The name of the model to be used for summarization.
            query (str): The query or input data to be summarized.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        logger.error("SummarizeTask run method not implemented.")
        raise NotImplementedError("Subclasses must implement the `run` method")
