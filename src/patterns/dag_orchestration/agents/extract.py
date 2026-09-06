from src.patterns.dag_orchestration.agent import Agent
from src.llm.generate import ResponseGenerator
from src.commons.message import Message
from src.config.logging import logger
from typing import Dict, List, Any
import asyncio
import os
import json
import re

class ExtractAgent(Agent):
    ROOT_PATTERN_PATH = './data/patterns/dag_orchestration'
    INPUT_SCHEMA_PATH = os.path.join(ROOT_PATTERN_PATH, 'schemas', 'preprocess.json')
    OUTPUT_SCHEMA_PATH = os.path.join(ROOT_PATTERN_PATH, 'schemas', 'extract.json')
    MODEL_NAME = 'gemini-1.5-flash-001'

    async def process(self, message: Message) -> Message:
        """
        Extracts key information from the preprocessed documents using an LLM.

        Args:
            message (Message): The input message containing preprocessed documents.

        Returns:
            Message: The message containing extracted key information in the format required by the schema.
        """
        logger.info(f"{self.name} started extracting key information from documents.")
        input_data = message.content

        # Validate the input data against the defined schema
        self._validate_input_data(input_data)

        response_generator = ResponseGenerator()
        extracted_items = []

        for doc in input_data.get("preprocessed_docs", []):
            try:
                extracted_data = await self._extract_key_information(response_generator, doc["id"], doc["title"], doc["content"])
                self._validate_characters(doc["title"], extracted_data.get("characters", []))
                self._validate_themes(doc["title"], extracted_data.get("themes", []))
                self._validate_plot_points(doc["title"], extracted_data.get("plot_points", []))

                # Create the extracted item following the updated schema
                extracted_items.append({
                    "id": doc["id"],
                    "key_info": [
                        {
                            "characters": extracted_data.get("characters", []),
                            "themes": extracted_data.get("themes", []),
                            "plot_points": extracted_data.get("plot_points", [])
                        }
                    ]
                })
            except Exception as e:
                logger.error(f"Failed to extract key information from document '{doc['title']}' with ID '{doc['id']}': {e}")
                raise RuntimeError(f"Error extracting key information for document '{doc['title']}'") from e

        # Prepare the final output in the required format
        output_data = {"extracted_items": extracted_items}

        # Validate the extracted key information against the output schema
        self._validate_output_data(output_data)

        logger.info(f"{self.name} successfully extracted and validated key information.")
        return Message(content=output_data, sender=self.name, recipient=message.sender)

    async def _extract_key_information(self, response_generator: ResponseGenerator, doc_id: str, doc_title: str, doc_content: str) -> Dict[str, Any]:
        """
        Extracts key information from a document using an LLM.

        Args:
            response_generator (ResponseGenerator): The LLM response generator instance.
            doc_id (str): The ID of the document being processed.
            doc_title (str): The title of the document.
            doc_content (str): The content of the document.

        Returns:
            Dict[str, Any]: The extracted key information in dictionary format.
        """
        llm_input = (
            "You are a literary analyst with expertise in text interpretation. Your task is to analyze the following document "
            "and extract key information. Specifically, identify the following:\n"
            "- A list of main characters (only names).\n"
            "- The major themes discussed or explored within the document.\n"
            "- Important plot points that are crucial to understanding the document's storyline.\n\n"
            "IMPORTANT: Provide the output as a single, properly formatted JSON object with keys 'characters', 'themes', and 'plot_points'. "
            "Ensure that 'characters' is an array of strings representing character names only. "
            "Do not include any explanations or additional text outside the JSON.\n"
            "Example of correct format:\n"
            '{"characters": ["Name1", "Name2"], "themes": ["Theme1", "Theme2"], "plot_points": ["Point1", "Point2"]}\n\n'
            f"Document ID: {doc_id}\n"
            f"Document Title: {doc_title}\n"
            f"Document Text:\n{doc_content}"
        )

        logger.info(f"Extracting key information from document '{doc_title}' with ID '{doc_id}' using LLM.")

        try:
            def blocking_call():
                return response_generator.generate_response(
                    model_name=self.MODEL_NAME,
                    system_instruction='You are an AI trained to extract key information from documents and output perfect JSON.',
                    contents=[llm_input]
                ).text.strip()

            extraction_result = await asyncio.to_thread(blocking_call)
            logger.info(f"LLM Response for document '{doc_title}': {extraction_result}")

            extracted_data = self.clean_and_parse_json(extraction_result)
            if not extracted_data:
                logger.error(f"Failed to extract valid JSON for document '{doc_title}'.")
                raise ValueError(f"Invalid JSON extraction for document '{doc_title}'")

            return extracted_data
        except Exception as e:
            logger.error(f"Failed to extract key information from document '{doc_title}' with ID '{doc_id}': {e}")
            raise RuntimeError(f"Error extracting key information for document '{doc_title}'") from e

    def _validate_input_data(self, input_data: Dict[str, Any]) -> None:
        """
        Validates the input data using the defined input schema.

        Args:
            input_data (Dict[str, Any]): The input data to validate.

        Raises:
            RuntimeError: If input validation fails.
        """
        try:
            self.validate_input(input_data, self.INPUT_SCHEMA_PATH)
        except Exception as e:
            logger.error(f"Validation failed for input documents: {e}")
            raise RuntimeError(f"Validation failed for input documents") from e

    def _validate_output_data(self, output_data: Dict[str, Any]) -> None:
        """
        Validates the output data using the defined output schema.

        Args:
            output_data (Dict[str, Any]): The output data to validate.

        Raises:
            RuntimeError: If output validation fails.
        """
        try:
            self.validate_output(output_data, self.OUTPUT_SCHEMA_PATH)
        except Exception as e:
            logger.error(f"Validation failed for extracted key information: {e}")
            raise RuntimeError(f"Validation failed for extracted key information") from e

    def _validate_characters(self, doc_title: str, characters: List[Any]) -> None:
        """
        Validates the extracted characters list for the document.

        Args:
            doc_title (str): The title of the document.
            characters (List[Any]): The extracted characters list to validate.

        Raises:
            ValueError: If the extracted characters format is invalid.
        """
        if not isinstance(characters, list) or not all(isinstance(c, str) for c in characters):
            logger.error(f"Invalid characters format for document '{doc_title}'.")
            raise ValueError(f"Invalid characters format for document '{doc_title}'")

    def _validate_themes(self, doc_title: str, themes: List[Any]) -> None:
        """
        Validates the extracted themes list for the document.

        Args:
            doc_title (str): The title of the document.
            themes (List[Any]): The extracted themes list to validate.

        Raises:
            ValueError: If the extracted themes format is invalid.
        """
        if not isinstance(themes, list) or not all(isinstance(t, str) for t in themes):
            logger.error(f"Invalid themes format for document '{doc_title}'.")
            raise ValueError(f"Invalid themes format for document '{doc_title}'")

    def _validate_plot_points(self, doc_title: str, plot_points: List[Any]) -> None:
        """
        Validates the extracted plot points list for the document.

        Args:
            doc_title (str): The title of the document.
            plot_points (List[Any]): The extracted plot points list to validate.

        Raises:
            ValueError: If the extracted plot points format is invalid.
        """
        if not isinstance(plot_points, list) or not all(isinstance(p, str) for p in plot_points):
            logger.error(f"Invalid plot points format for document '{doc_title}'.")
            raise ValueError(f"Invalid plot points format for document '{doc_title}'")

    @staticmethod
    def clean_and_parse_json(json_string: str) -> dict:
        """
        Cleans and parses a JSON string, handling potential formatting issues.

        Args:
            json_string (str): The JSON string to clean and parse.

        Returns:
            dict: The parsed JSON data.

        Raises:
            ValueError: If the JSON cannot be parsed after cleaning.
        """
        # Remove any text before the first '{' and after the last '}'
        json_string = re.sub(r'^[^{]*', '', json_string)
        json_string = re.sub(r'[^}]*$', '', json_string)
        
        # Remove any extra sets of curly braces
        while json_string.startswith('{{') and json_string.endswith('}}'):
            json_string = json_string[1:-1]
        
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON after cleanup: {e}")