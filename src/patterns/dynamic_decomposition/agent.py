from src.commons.message import Message
from abc import abstractmethod 
from abc import ABC


class Agent(ABC):
    """
    A base class representing an agent responsible for processing messages 
    and validating input and output data based on given JSON schemas.
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the agent with a given name.
        
        Args:
            name (str): The name of the agent.
        """
        self.name = name

    @abstractmethod
    async def process(self, message: 'Message') -> 'Message':
        """
        Abstract method to process the message.
        
        Args:
            message (Message): A message object containing relevant data.
        
        Returns:
            Message: Processed message.
        
        Raises:
            NotImplementedError: If not overridden by a subclass.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
