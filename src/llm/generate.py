from vertexai.generative_models import GenerationResponse
from src.llm.strategy import GenerationStrategyFactory
from src.llm.factory import ModelFactoryProvider
from src.config.logging import logger
from src.config.setup import *
from typing import Optional
from typing import List 
from typing import Dict 
from typing import Any 
import time


class ResponseGenerator:
    """
    Handles response generation using various generation strategies and model factories. 
    The `strategy_type` in the configuration specifies the generation strategy.

    Attributes:
        model_factory: Instance of ModelFactoryProvider for creating model instances.
        generation_strategy: Strategy selected for content generation.
    """

    def __init__(self, strategy_type: str = "default") -> None:
        """
        Initializes ResponseGenerator with the specified strategy type.

        Args:
            strategy_type (str): Type of strategy for content generation. Defaults to "default".
        """
        self.model_factory = ModelFactoryProvider.get_instance()
        self.generation_strategy = GenerationStrategyFactory.get_strategy(strategy_type)

    def generate_response(self, model_name: str, system_instruction: str, contents: List[str], response_schema: Optional[Dict[str, Any]] = None, tools: List[Any] = None) -> GenerationResponse:
        """
        Generates a response based on the provided model name, system instruction, contents, response schema, and tools.

        Args:
            model_name (str): Name of the model for generation.
            system_instruction (str): Instruction or prompt for the model.
            contents (List[str]): Content input list for response generation.
            response_schema (Optional[Dict[str, Any]]): Schema defining response structure and constraints (default is None).
            tools (List[Any]): Tools passed to the model for content generation (default is None).

        Returns:
            GenerationResponse: Generated response object.

        Raises:
            Exception: If an error occurs during response generation.
        """
        logger.info("Starting response generation.")
        
        try:
            logger.info(f"Creating model instance for: {model_name}")
            # MOCKED: model = self.model_factory.create_model(model_name, system_instruction)
            logger.info("Model created successfully.")
            
            # Prepare generation configuration and safety settings
            # generation_config = self.generation_strategy.create_generation_config(response_schema) if response_schema else None
            # safety_settings = self.generation_strategy.create_safety_settings()
            
            # MOCKED FOR VIDEO DEMONSTRATION
            class MockResponse:
                def __init__(self, text):
                    self.text = text
            
            # Determine which type of response this is based on schema or instructions
            mock_text = ""
            if response_schema and 'entities' in str(response_schema).lower():
                # NER response
                mock_text = '{"entities": {"flight": ["New York to Dallas"], "hotel": ["downtown Dallas"], "car_rental": ["next week"]}}'
            elif response_schema:
                # Sub-agent response
                mock_text = '{"status": "success", "results": "Found great options for you!"}'
            else:
                # Consolidate response
                mock_text = "Here is your finalized travel itinerary:\n- Flight: Booked from New York to Dallas.\n- Hotel: Downtown Dallas confirmed.\n- Car: Rental car secured for next week.\nHave a great trip!"

            response = MockResponse(text=mock_text)
            
            logger.info("Mocked response generated successfully.")
            return response 
        
        except Exception as e:
            if "429" in str(e) and "Resource exhausted" in str(e):
                logger.error("Quota exceeded: 429 Resource exhausted. Retrying in 60 seconds.")
                time.sleep(60)  # Retry after delay due to quota limits
                return self._retry_generate_response(model, contents, generation_config, safety_settings, tools)
            else:
                logger.error(f"Error generating response: {e}")
                raise

    def _retry_generate_response(self, model, contents, generation_config, safety_settings, tools) -> GenerationResponse:
        """
        Retries response generation once after a 429 quota limit error.

        Args:
            model: Model instance to retry with.
            contents (List[str]): Content input for response generation.
            generation_config (Any): Configuration for generation.
            safety_settings (Any): Safety settings for the model.
            tools (List[Any]): Tools passed to the model.

        Returns:
            GenerationResponse: The response after retry.
            
        Raises:
            Exception: If the retry fails or another error occurs.
        """
        try:
            response = model.generate_content(
                contents,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools
            )
            logger.info("Response generated successfully after retry.")
            return response
        except Exception as retry_error:
            logger.error(f"Retry failed: {retry_error}")
            raise
