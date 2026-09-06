from src.config.logging import logger
from collections import OrderedDict
from typing import Optional
from typing import Dict
from typing import Any 


class StateManager:
    """
    StateManager class that maintains an ordered dictionary to store key-value pairs and
    provides functionality to convert the state into a Markdown formatted string.

    Attributes:
        _state (OrderedDict[str, Any]): An ordered dictionary to store state entries.
        _state_md (Optional[str]): A string representation of the state in Markdown format.
    """

    def __init__(self):
        """
        Initialize the StateManager with an empty ordered dictionary and None for the Markdown state.
        """
        self._state: OrderedDict[str, Any] = OrderedDict()
        self._state_md: Optional[str] = None

    def add_entry(self, key: str, value: Any) -> None:
        """
        Add a key-value pair to the state and update the Markdown representation.

        Args:
            key (str): The key for the state entry.
            value (Any): The value associated with the key.

        Raises:
            ValueError: If key is empty or None.
            Exception: If any other error occurs during the process.
        """
        if not key:
            logger.error("The key provided is empty or None.")
            raise ValueError("Key must not be empty or None.")

        try:
            self._state[key] = value
            self._state_md = self.to_markdown()
            logger.info(f"Entry added to state: {key} = {value}")
        except Exception as e:
            logger.error(f"Error adding entry to state: {e}")
            raise

    def to_markdown(self) -> str:
        """
        Convert the current state to a Markdown formatted string.

        Returns:
            str: The state as a Markdown formatted string.

        Raises:
            Exception: If an error occurs during the conversion.
        """
        try:
            markdown = []
            for key, value in self._state.items():
                markdown.append(f"### {key}\n")
                if isinstance(value, dict):
                    markdown.append(f"\n{self._dict_to_markdown(value)}\n")
                else:
                    markdown.append(f"\n{value}\n")
                markdown.append("\n")
            logger.info("State successfully converted to Markdown.")
            return ''.join(markdown)
        except Exception as e:
            logger.error(f"Error converting state to Markdown: {e}")
            raise

    @staticmethod
    def _dict_to_markdown(data: Dict[str, Any], indent_level: int = 0) -> str:
        """
        Recursively convert a dictionary to a Markdown formatted string.

        Args:
            data (Dict[str, Any]): The dictionary to convert.
            indent_level (int): The current indentation level for nested dictionaries.

        Returns:
            str: The dictionary as a Markdown formatted string.

        Raises:
            Exception: If an error occurs during the conversion.
        """
        try:
            markdown = []
            indent = ' ' * indent_level
            for key, value in data.items():
                if isinstance(value, dict):
                    markdown.append(f"{indent}- **{key.capitalize()}**:\n")
                    markdown.append(StateManager._dict_to_markdown(value, indent_level + 2))
                else:
                    markdown.append(f"{indent}- **{key.capitalize()}**: {value}\n")
            logger.info("Dictionary successfully converted to Markdown.")
            return ''.join(markdown)
        except Exception as e:
            logger.error(f"Error converting dictionary to Markdown: {e}")
            raise

    def get_state(self) -> OrderedDict[str, Any]:
        """
        Get the current state as an ordered dictionary.

        Returns:
            OrderedDict[str, Any]: The current state.
        """
        return self._state

    def get_state_markdown(self) -> Optional[str]:
        """
        Get the current state as a Markdown formatted string.

        Returns:
            Optional[str]: The current state in Markdown format, or None if the state is empty.
        """
        return self._state_md
