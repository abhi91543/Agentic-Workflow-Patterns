from vertexai.generative_models import GenerativeModel
from src.config.logging import logger
from abc import abstractmethod
from typing import Optional
from abc import ABC


class ModelFactory(ABC):
    """
    Abstract base class for creating generative models.

    This class defines the interface for creating generative models, 
    ensuring that subclasses implement the `create_model` method.
    """

    @abstractmethod
    def create_model(self, model_name: str, system_instruction: str) -> GenerativeModel:
        """
        Creates and returns an instance of a GenerativeModel.

        Args:
            model_name (str): The name of the model to create.
            system_instruction (str): The system instruction to initialize the model with.

        Returns:
        --------
        GenerativeModel: An instance of the GenerativeModel.

        Raises:
        -------
        NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement the `create_model` method")


class VertexAIModelFactory(ModelFactory):
    """
    Concrete implementation of the ModelFactory for Vertex AI models.

    This class is responsible for creating instances of GenerativeModel specific to Vertex AI.
    """

    def create_model(self, model_name: str, system_instruction: str) -> GenerativeModel:
        """
        Creates and returns an instance of a Vertex AI GenerativeModel.

        Args:
            model_name (str): The name of the Vertex AI model to create.
            system_instruction (str): The system instruction to initialize the model with.

        Returns:
        --------
        GenerativeModel: An instance of the Vertex AI GenerativeModel.

        Raises:
        -------
        Exception: If there is an error during model creation, it logs the error and re-raises it.
        """
        try:
            return GenerativeModel(model_name, system_instruction=system_instruction)
        except Exception as e:
            logger.error(f"Error creating GenerativeModel: {e}")
            raise


class ModelFactoryProvider:
    """
    Singleton provider for the ModelFactory.

    This class ensures that only one instance of the ModelFactory is created,
    providing a global access point for it.
    """
    _instance: Optional[ModelFactory] = None

    @staticmethod
    def get_instance() -> ModelFactory:
        """
        Returns the singleton instance of the ModelFactory.

        If no instance exists, it creates one.

        Returns:
        --------
        ModelFactory: The singleton instance of the ModelFactory.
        """
        if ModelFactoryProvider._instance is None:
            ModelFactoryProvider._instance = VertexAIModelFactory()
        return ModelFactoryProvider._instance
