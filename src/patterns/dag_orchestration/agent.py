from src.commons.message import Message
from jsonschema import ValidationError
from src.config.logging import logger
from json import JSONDecodeError
from jsonschema import validate
from abc import abstractmethod
from typing import Dict
from typing import Any 
from abc import ABC
import json


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

    def validate_input(self, data: Dict[str, Any], schema_file: str) -> None:
        """
        Validates the input data against a JSON schema file.
        
        Args:
            data (Dict[str, Any]): The input data to validate.
            schema_file (str): Path to the JSON schema file.

        Raises:
            ValueError: If the schema file cannot be read or parsed.
            ValidationError: If the input data does not conform to the schema.
        """
        schema = self._load_schema(schema_file)
        try:
            validate(instance=data, schema=schema)
            logger.info(f"{self.name} input validated successfully against {schema_file}.")
        except ValidationError as e:
            logger.error(f"{self.name} input validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during input validation: {e}")
            raise

    def validate_output(self, data: Dict[str, Any], schema_file: str) -> None:
        """
        Validates the output data against a JSON schema file.
        
        Args:
            data (Dict[str, Any]): The output data to validate.
            schema_file (str): Path to the JSON schema file.

        Raises:
            ValueError: If the schema file cannot be read or parsed.
            ValidationError: If the output data does not conform to the schema.
        """
        schema = self._load_schema(schema_file)
        try:
            validate(instance=data, schema=schema)
            logger.info(f"{self.name} output validated successfully against {schema_file}.")
        except ValidationError as e:
            logger.error(f"{self.name} output validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during output validation: {e}")
            raise

    def _load_schema(self, schema_file: str) -> Dict[str, Any]:
        """
        Loads and returns a JSON schema from a file.
        
        Args:
            schema_file (str): Path to the JSON schema file.
        
        Returns:
            Dict[str, Any]: Loaded JSON schema.

        Raises:
            ValueError: If the schema file cannot be read or parsed.
        """
        try:
            with open(schema_file, 'r') as f:
                schema = json.load(f)
            return schema
        except (FileNotFoundError, JSONDecodeError) as e:
            logger.error(f"Failed to load schema file {schema_file}: {e}")
            raise ValueError(f"Error loading schema file {schema_file}: {e}")
