from src.patterns.dag_orchestration.agent import Agent
from src.llm.generate import ResponseGenerator
from src.commons.message import Message
from src.config.logging import logger
from typing import Tuple
from typing import List
from typing import Dict 
from typing import Any 
from glob import glob
import asyncio
import os


class CollectAgent(Agent):
    ROOT_PATTERN_PATH = './data/patterns/dag_orchestration'
    DOCS_FOLDER = os.path.join(ROOT_PATTERN_PATH, 'docs')
    SCHEMA_PATH = os.path.join(ROOT_PATTERN_PATH, 'schemas', 'collect.json')
    MODEL_NAME = 'gemini-1.5-flash-001'

    async def process(self, message: Message) -> Message:
        """
        Preprocesses collected documents by cleaning the content using an LLM. This is particularly useful if the collected
        content is obtained via OCR or web scraping, which often requires further processing.

        Args:
            message (Message): The input message containing collected documents.

        Returns:
            Message: The message containing preprocessed documents.

        Raises:
            RuntimeError: If document preprocessing or validation fails.
        """
        logger.info(f"{self.name} started collecting documents.")
        # Uncomment and use the following line if the message content needs to be processed or accessed 
        # before orchestrating subtasks.
        # input_data = message.content  

        try:
            # Asynchronously collect documents from the specified folder
            docs = await self._collect_documents(self.DOCS_FOLDER)
            
            # Validate the collected documents against the defined schema for consistency
            self.validate_output(docs, self.SCHEMA_PATH)
        except Exception as e:
            logger.error(f"Validation failed for collected documents: {e}")
            raise RuntimeError("Validation failed for collected documents") from e

        logger.info(f"{self.name} successfully collected and validated documents.")
        return Message(content=docs, sender=self.name, recipient=message.sender)

    async def _collect_documents(self, folder_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collects text documents from a specified folder and processes each document.

        Args:
            folder_path (str): Path to the folder containing text documents.

        Returns:
            Dict[str, List[Dict[str, Any]]]: A dictionary containing metadata of collected documents.

        Raises:
            RuntimeError: If any document collection fails.
        """
        doc_files = glob(os.path.join(folder_path, '*.txt'))
        docs = {"docs": []}

        for idx, filepath in enumerate(doc_files):
            try:
                content, title = self._read_document(filepath)
                extracted_title = await self._extract_title_from_llm(content)  # Directly await the coroutine

                docs["docs"].append({
                    "id": f"doc{idx + 1}",
                    "title": extracted_title if extracted_title else title,
                    "content": content,
                    "filename": filepath
                })
            except Exception as e:
                logger.error(f"Failed to collect document from {filepath}: {e}")
                raise RuntimeError(f"Error collecting document from {filepath}") from e

        return docs

    def _read_document(self, filepath: str) -> Tuple[str, str]:
        """
        Reads a text document and returns its content and title.

        Args:
            filepath (str): Path to the document.

        Returns:
            Tuple[str, str]: The content and title of the document.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            title = os.path.splitext(os.path.basename(filepath))[0]
            return content, title
        except Exception as e:
            logger.error(f"Error reading document from {filepath}: {e}")
            raise RuntimeError(f"Failed to read document from {filepath}") from e

    async def _extract_title_from_llm(self, document: str) -> str:
        """
        Extracts an appropriate title for a document using an LLM.

        Args:
            document (str): The document content to extract the title from.

        Returns:
            str: The extracted title.
        """
        llm_input = (
            "The following text represents a document that requires a precise and descriptive title: \n\n"
            f"{document}\n\n"
            "Please analyze the content thoroughly and generate a concise, professional, short title that accurately reflects the core theme of the document. "
            "Only return one title."
        )
        logger.info(f"Extracting title using LLM for content length: {len(document)} characters.")

        try:
            response_generator = ResponseGenerator()

            def blocking_call():
                return response_generator.generate_response(
                    model_name=self.MODEL_NAME,
                    system_instruction='',
                    contents=[llm_input]
                ).text.strip()

            extracted_title = await asyncio.to_thread(blocking_call)
            return extracted_title
        except Exception as e:
            logger.error(f"Failed to extract title using LLM: {e}")
            return ""  # Return empty if LLM fails