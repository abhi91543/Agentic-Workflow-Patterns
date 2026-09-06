from src.config.logging import logger
from src.utils.io import load_json
from src.utils.io import load_yaml
from typing import Optional
from typing import Dict


class TemplateManager:
    """
    Manages the creation and manipulation of templates based on a provided configuration file.

    Attributes:
        config (dict): The configuration loaded from a YAML file that specifies the templates for different roles and actions.
    """

    def __init__(self, config_path: str) -> None:
        """
        Initializes the TemplateManager with a given configuration path.

        Args:
            config_path (str): The path to the YAML configuration file.
        """
        self.config: Dict[str, Dict[str, Dict[str, Optional[str]]]] = load_yaml(config_path)

    def create_template(self, role: str, action: str) -> Dict[str, Optional[str]]:
        """
        Creates a template based on the provided role and action.

        Args:
            role (str): The role for which the template is to be created.
            action (str): The action associated with the role.

        Returns:
            Dict[str, Optional[str]]: A dictionary containing the system instructions, user instructions, and response schema (if available).

        Raises:
            KeyError: If the role or action does not exist in the configuration.
            Exception: For any other errors encountered during template creation.
        """
        try:
            template_config = self.config[role][action]

            return {
                'system': self.load_template(template_config['system_instructions']),
                'user': self.load_template(template_config['user_instructions']),
                'schema': self.load_schema(template_config.get('response_schema'))
            }
        except KeyError as e:
            logger.error(f"Invalid role or action in template configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise

    @staticmethod
    def load_template(template_path: str) -> str:
        """
        Loads a template from a given file path.

        Args:
            template_path (str): The path to the template file.

        Returns:
            str: The content of the template file.

        Raises:
            FileNotFoundError: If the template file is not found.
            Exception: For any other errors encountered during file reading.
        """
        try:
            with open(template_path, 'r') as file:
                return file.read()
        except FileNotFoundError as e:
            logger.error(f"Template file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            raise

    @staticmethod
    def load_schema(schema_path: Optional[str]) -> Optional[Dict]:
        """
        Loads a JSON schema from a given file path, if the path is provided.

        Args:
            schema_path (Optional[str]): The path to the JSON schema file, or None.

        Returns:
            Optional[Dict]: The content of the schema file, or None if the schema_path is None.

        Raises:
            FileNotFoundError: If the schema file is not found.
            Exception: For any other errors encountered during file reading.
        """
        if schema_path is None:
            return None
        try:
            return load_json(schema_path)
        except FileNotFoundError as e:
            logger.error(f"Schema file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading schema: {e}")
            raise

    @staticmethod
    def fill_template(template_content: str, **kwargs: str) -> str:
        """
        Fills a template with provided keyword arguments.

        Args:
            template_content (str): The content of the template to be filled.
            **kwargs (str): Key-value pairs where the key is the placeholder in the template and the value is the content to replace it with.

        Returns:
            str: The filled template content.

        Raises:
            Exception: For any errors encountered during the template filling process.
        """
        try:
            filled_template = template_content
            for key, value in kwargs.items():
                placeholder = f"{{{key}}}"
                filled_template = filled_template.replace(placeholder, str(value))
            return filled_template
        except Exception as e:
            logger.error(f"Error filling template: {e}")
            raise
