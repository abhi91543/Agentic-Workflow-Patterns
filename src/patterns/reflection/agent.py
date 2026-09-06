from src.patterns.reflection.utils import save_to_disk
from src.llm.generate import ResponseGenerator
from src.prompt.manage import TemplateManager
from src.config.logging import logger
from abc import abstractmethod
from typing import Any
from abc import ABC


class ContentGenerator(ABC):
    """
    Abstract base class for content generators.
    
    Methods:
    --------
    generate(model_name: str, **kwargs: Any) -> str:
        Abstract method that must be implemented by subclasses to generate content.
    """

    @abstractmethod
    def generate(self, model_name: str, **kwargs: Any) -> str:
        """
        Generate content based on provided arguments.

        Parameters:
        -----------
        model_name : str
            The name of the model to be used for generating content.
        kwargs : Any
            Additional arguments required for content generation.

        Returns:
        --------
        str
            The generated content.

        Raises:
        -------
        NotImplementedError
            If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the `generate` method")


class Agent:
    """
    Agent is responsible for managing the process of content generation and saving the generated content.
    
    Attributes:
    -----------
    model_name : str
        The name of the model used for generating content.
    topic : str
        The topic for content generation.
    output_path : str
        The path where generated content will be saved.
    template_manager : TemplateManager
        Manages templates for generating content.
    response_generator : ResponseGenerator
        Generates responses based on the instructions and templates.
    
    Methods:
    --------
    _generate_content(generator: ContentGenerator, **kwargs: Any) -> str:
        Generates content using the specified content generator.
    _save_content(content: str, content_type: str, version: int) -> None:
        Saves the generated content to disk.
    """

    def __init__(self, model_name: str, topic: str, config_path: str, output_path: str):
        """
        Initialize the Agent with a model name, topic, configuration path, and output path.

        Parameters:
        -----------
        model_name : str
            The name of the model used for generating content.
        topic : str
            The topic for which content will be generated.
        config_path : str
            The path to the configuration file for template management.
        output_path : str
            The path where the generated content will be saved.
        """
        self.model_name = model_name
        self.topic = topic
        self.output_path = output_path
        self.template_manager = TemplateManager(config_path)
        self.response_generator = ResponseGenerator()

    def _generate_content(self, generator: ContentGenerator, **kwargs: Any) -> str:
        """
        Generate content using the specified content generator.

        Parameters:
        -----------
        generator : ContentGenerator
            The content generator to use for generating content.
        kwargs : Any
            Additional arguments required for content generation.

        Returns:
        --------
        str
            The generated content.
        """
        return generator.generate(model_name=self.model_name, 
                                  template_manager=self.template_manager, 
                                  response_generator=self.response_generator, 
                                  **kwargs)

    def _save_content(self, content: str, content_type: str, version: int) -> None:
        """
        Save the generated content to disk.

        Parameters:
        -----------
        content : str
            The content to save.
        content_type : str
            The type of content being saved (e.g., 'draft', 'feedback').
        version : int
            The version number of the content being saved.

        Raises:
        -------
        Exception
            If an error occurs during saving.
        """
        try:
            save_to_disk(content, content_type, version, self.output_path)
        except Exception as e:
            logger.error(f"Error saving {content_type}: {e}")
            raise
