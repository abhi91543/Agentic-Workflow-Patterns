from vertexai.generative_models import HarmBlockThreshold 
from vertexai.generative_models import GenerationConfig
from vertexai.generative_models import HarmCategory
from src.config.logging import logger
from abc import abstractmethod
from typing import Dict
from typing import Any 
from abc import ABC


class GenerationStrategy(ABC):
    """
    Abstract base class for generation strategies. 
    All strategies must implement methods for creating generation configurations and safety settings.
    """

    @abstractmethod
    def create_generation_config(self, response_schema: Dict[str, Any]) -> GenerationConfig:
        """
        Create the generation configuration based on the provided response schema.

        Args:
            response_schema (Dict[str, Any]): The schema defining the response structure.

        Returns:
            GenerationConfig: The configuration object for text generation.
        """
        raise NotImplementedError("Subclasses must implement the `create_generation_config` method")

    @abstractmethod
    def create_safety_settings(self) -> Dict[HarmCategory, HarmBlockThreshold]:
        """
        Create the safety settings for the generation process.

        Returns:
            Dict[HarmCategory, HarmBlockThreshold]: A dictionary mapping harm categories to block thresholds.
        """
        raise NotImplementedError("Subclasses must implement the `create_safety_settings` method")


class DefaultGenerationStrategy(GenerationStrategy):
    """
    Default implementation of the GenerationStrategy.
    Provides a basic configuration and safety settings for text generation.
    """

    def create_generation_config(self, response_schema: Dict[str, Any]) -> GenerationConfig:
        """
        Create the default generation configuration.

        Args:
            response_schema (Dict[str, Any]): The schema defining the response structure.

        Returns:
            GenerationConfig: The configuration object for text generation.
        """
        try:
            config = GenerationConfig(
                temperature=0.0,
                top_p=0.0,
                top_k=1,
                candidate_count=1,
                max_output_tokens=8192,
                response_mime_type="application/json",
                response_schema=response_schema
            )
            logger.info("Generation configuration created successfully.")
            return config
        except Exception as e:
            logger.error(f"Error creating generation configuration: {e}")
            raise

    def create_safety_settings(self) -> Dict[HarmCategory, HarmBlockThreshold]:
        """
        Create the default safety settings.

        Returns:
            Dict[HarmCategory, HarmBlockThreshold]: A dictionary mapping harm categories to block thresholds.
        """
        try:
            safety_settings = {
                HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
            }
            logger.info("Safety settings created successfully.")
            return safety_settings
        except Exception as e:
            logger.error(f"Error creating safety settings: {e}")
            raise


class GenerationStrategyFactory:
    """
    Factory for creating generation strategies based on the specified type.
    """

    @staticmethod
    def get_strategy(strategy_type: str = "default") -> GenerationStrategy:
        """
        Retrieve the appropriate generation strategy based on the provided type.

        Args:
            strategy_type (str): The type of strategy to retrieve. Defaults to "default".

        Returns:
            GenerationStrategy: The corresponding strategy object.
        """
        try:
            if strategy_type == "default":
                logger.info("Default generation strategy selected.")
                return DefaultGenerationStrategy()
            else:
                raise ValueError(f"Unknown strategy type: {strategy_type}")
        except ValueError as e:
            logger.error(f"Error in strategy selection: {e}")
            raise
