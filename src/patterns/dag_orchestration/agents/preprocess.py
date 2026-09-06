from src.patterns.dag_orchestration.agent import Agent
from src.llm.generate import ResponseGenerator
from src.commons.message import Message
from src.config.logging import logger
import asyncio
import os


class PreprocessAgent(Agent):
    ROOT_PATTERN_PATH = './data/patterns/dag_orchestration'
    INPUT_SCHEMA_PATH = os.path.join(ROOT_PATTERN_PATH, 'schemas', 'collect.json')
    OUTPUT_SCHEMA_PATH = os.path.join(ROOT_PATTERN_PATH, 'schemas', 'preprocess.json')
    MODEL_NAME = 'gemini-1.5-flash-001'

    async def process(self, message: Message) -> Message:
        """
        Preprocesses collected documents by cleaning the content using an LLM. This is especially useful if the collected
        content is read using OCR or scraped from the web.

        Args:
            message (Message): The input message containing collected documents.

        Returns:
            Message: The message containing preprocessed documents.

        Raises:
            RuntimeError: If document preprocessing or validation fails.
        """
        logger.info(f"{self.name} started preprocessing documents.")
        input_data = message.content

        # Validate the input data against the defined schema
        self._validate_input_data(input_data)

        response_generator = ResponseGenerator()
        preprocessed_docs = {"preprocessed_docs": []}

        for doc in input_data.get("docs", []):
            try:
                cleaned_content = await self._clean_document_content(
                    response_generator, doc["id"], doc["title"], doc["content"]
                )

                preprocessed_docs["preprocessed_docs"].append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "content": cleaned_content
                })
            except Exception as e:
                logger.error(f"Failed to preprocess document '{doc['title']}' with ID '{doc['id']}': {e}")
                raise RuntimeError(f"Error preprocessing document '{doc['title']}'") from e

        # Validate the preprocessed documents against the output schema
        self._validate_output_data(preprocessed_docs)

        logger.info(f"{self.name} successfully preprocessed and validated documents.")
        return Message(content=preprocessed_docs, sender=self.name, recipient=message.sender)

    async def _clean_document_content(self, response_generator: ResponseGenerator, doc_id: str, doc_title: str, doc_content: str) -> str:
        """
        Cleans the content of a document using an LLM.

        Args:
            response_generator (ResponseGenerator): The LLM response generator instance.
            doc_id (str): The ID of the document being processed.
            doc_title (str): The title of the document.
            doc_content (str): The raw content of the document.

        Returns:
            str: The cleaned document content.

        Raises:
            RuntimeError: If the LLM fails to generate a response.
        """
        llm_input = (
            "You are an expert in text processing and content refinement. Given the raw text of a document, "
            "perform advanced cleaning and normalization by removing any unnecessary formatting, correcting OCR errors, "
            "and improving readability without altering the original meaning or intent of the content. "
            "The goal is to produce a well-structured, clear, and professional document text.\n\n"
            f"Document Title: {doc_title}\n"
            f"Raw Document Text:\n{doc_content}"
        )

        logger.info(f"Processing document '{doc_title}' with ID '{doc_id}' using LLM for content cleaning.")

        try:
            def blocking_call():
                return response_generator.generate_response(
                    model_name=self.MODEL_NAME,
                    system_instruction='',
                    contents=[llm_input]
                ).text.strip()

            cleaned_content = await asyncio.to_thread(blocking_call)
            return cleaned_content
        except Exception as e:
            logger.error(f"Failed to clean content for document '{doc_title}' with ID '{doc_id}': {e}")
            return ""  # Return empty if LLM fails

    def _validate_input_data(self, input_data: dict) -> None:
        """
        Validates the input data using the defined input schema.

        Args:
            input_data (dict): The input data to validate.

        Raises:
            RuntimeError: If input validation fails.
        """
        try:
            self.validate_input(input_data, self.INPUT_SCHEMA_PATH)
        except Exception as e:
            logger.error(f"Validation failed for input documents: {e}")
            raise RuntimeError(f"Validation failed for input documents") from e

    def _validate_output_data(self, output_data: dict) -> None:
        """
        Validates the output data using the defined output schema.

        Args:
            output_data (dict): The output data to validate.

        Raises:
            RuntimeError: If output validation fails.
        """
        try:
            self.validate_output(output_data, self.OUTPUT_SCHEMA_PATH)
        except Exception as e:
            logger.error(f"Validation failed for preprocessed documents: {e}")
            raise RuntimeError(f"Validation failed for preprocessed documents") from e
