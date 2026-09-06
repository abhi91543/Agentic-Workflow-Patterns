from src.llm.generate import ResponseGenerator
from src.prompt.manage import TemplateManager
from src.commons.message import Message
from src.config.logging import logger
from abc import abstractmethod
from abc import ABC 


class Agent(ABC):
    """
    Abstract base class for agents that handle specific tasks in a coordinator-delegate pattern.
    Each agent must implement the 'process' method to handle incoming messages.
    Shared resources like TemplateManager and ResponseGenerator are initialized here for all agents.
    """

    TEMPLATE_PATH = './config/patterns/semantic_router.yml'

    def __init__(self, name: str) -> None:
        """
        Initializes the Agent with a name, TemplateManager, and ResponseGenerator.

        :param name: Name of the agent.
        """
        self.name = name
        self.template_manager = TemplateManager(self.TEMPLATE_PATH)
        self.response_generator = ResponseGenerator()
        logger.info(f"Agent {self.name} initialized with shared resources.")

    @abstractmethod
    def process(self, message: Message) -> Message:
        """
        Abstract method to process the incoming message. Must be implemented by subclasses.

        :param message: The message to be processed by the agent.
        :raise NotImplementedError: If the method is not implemented by a subclass.
        :return: A processed Message object with the response.
        """
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the 'process' method.")
