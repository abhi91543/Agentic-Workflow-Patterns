from src.patterns.dag_orchestration.agent import Agent
from src.llm.generate import ResponseGenerator
from src.commons.message import Message
from src.config.logging import logger
import asyncio
import os
import json
import re

class CompileAgent(Agent):
    ROOT_PATTERN_PATH = './data/patterns/dag_orchestration'
    KEY_INFO_SCHEMA_PATH = os.path.join(ROOT_PATTERN_PATH, 'schemas', 'extract.json')
    SUMMARIES_SCHEMA_PATH = os.path.join(ROOT_PATTERN_PATH, 'schemas', 'summarize.json')
    FINAL_REPORT_SCHEMA_PATH = os.path.join(ROOT_PATTERN_PATH, 'schemas', 'compile.json')
    MODEL_NAME = 'gemini-1.5-flash-001'

    async def process(self, message: Message) -> Message:
        """
        Compiles a final report based on key information and summaries.

        Args:
            message (Message): The input message containing key information and summaries.

        Returns:
            Message: The message containing the compiled report.

        Raises:
            RuntimeError: If report compilation or validation fails.
        """
        logger.info(f"{self.name} started compiling final report.")
        input_data = message.content

        # Validate the input data for key information and summaries
        self._validate_input_data(input_data)

        key_info_data = input_data['task3']["extracted_items"]
        summaries_data = input_data['task4']["summaries"]
        response_generator = ResponseGenerator()
        report_sections = []

        for key_info_entry in key_info_data:
            try:
                report_section = await self._compile_report_section(
                    response_generator, key_info_entry, summaries_data
                )
                if report_section:
                    report_sections.append(report_section)
            except Exception as e:
                logger.error(f"Failed to compile report section for document ID '{key_info_entry['id']}': {e}")
                raise RuntimeError(f"Error compiling report section for document '{key_info_entry['id']}'") from e

        report = {"report": "\n\n".join(report_sections)}

        # Validate the compiled report against the final report schema
        self._validate_output_data(report)

        logger.info(f"{self.name} successfully compiled and validated the final report.")
        return Message(content=report, sender=self.name, recipient=message.sender)

    async def _compile_report_section(self, response_generator: ResponseGenerator, key_info_entry: dict, summaries_data: list) -> str:
        """
        Compiles a report section based on key information and summary using an LLM.

        Args:
            response_generator (ResponseGenerator): The LLM response generator instance.
            key_info_entry (dict): The key information entry for a document.
            summaries_data (list): The summaries data for all documents.

        Returns:
            str: The compiled report section.

        Raises:
            RuntimeError: If the LLM fails to generate a response.
        """
        doc_id = key_info_entry["id"]
        summary_entry = next(
            (s for s in summaries_data if s["id"] == doc_id), None
        )

        if not summary_entry:
            logger.warning(f"No summary found for document ID '{doc_id}'. Skipping.")
            return None
    
        llm_input = (
            f"You are a report compiler. Given the summary and key information of a document, "
            f"compile a well-formatted report section for this document. The report should include:\n"
            f"- Title of the document (use the document ID as the title).\n"
            f"- Summary.\n"
            f"- List of main characters with brief descriptions.\n"
            f"- Major themes with brief explanations.\n"
            f"- Important plot points in a narrative format.\n\n"
            f"IMPORTANT: Provide the report section in a clear, structured format. Use markdown formatting for headers and lists. "
            f"Ensure the content is coherent and well-organized.\n\n"
            f"Document ID: {doc_id}\n"
            f"Summary:\n{summary_entry['summary']}\n\n"
            f"Characters:\n{', '.join(key_info_entry['key_info'][0]['characters'])}\n\n"
            f"Themes:\n{', '.join(key_info_entry['key_info'][0]['themes'])}\n\n"
            f"Plot Points:\n- {' '.join(key_info_entry['key_info'][0]['plot_points'])}"
        )

        logger.info(f"Compiling report section for document ID '{doc_id}' using LLM.")

        try:
            def blocking_call():
                return response_generator.generate_response(
                    model_name=self.MODEL_NAME,
                    system_instruction='You are an AI trained to compile clear, well-structured reports based on provided information.',
                    contents=[llm_input]
                ).text.strip()

            report_section = await asyncio.to_thread(blocking_call)
            return self.clean_and_format_report_section(report_section)
        except Exception as e:
            logger.error(f"Failed to compile report section for document ID '{doc_id}': {e}")
            raise RuntimeError(f"Error compiling report section for document '{doc_id}'") from e

    def _validate_input_data(self, input_data: dict) -> None:
        """
        Validates the input data for key information and summaries.

        Args:
            input_data (dict): The input data to validate.

        Raises:
            RuntimeError: If input validation fails.
        """
        try:
            self.validate_input(input_data['task3'], self.KEY_INFO_SCHEMA_PATH)
            self.validate_input(input_data['task4'], self.SUMMARIES_SCHEMA_PATH)
        except Exception as e:
            logger.error(f"Validation failed for inputs to compile report: {e}")
            raise RuntimeError(f"Validation failed for inputs to compile report") from e

    def _validate_output_data(self, output_data: dict) -> None:
        """
        Validates the compiled report against the final report schema.

        Args:
            output_data (dict): The compiled report data to validate.

        Raises:
            RuntimeError: If output validation fails.
        """
        try:
            self.validate_output(output_data, self.FINAL_REPORT_SCHEMA_PATH)
        except Exception as e:
            logger.error(f"Validation failed for compiled report: {e}")
            raise RuntimeError(f"Validation failed for compiled report") from e

    @staticmethod
    def clean_and_format_report_section(report_section: str) -> str:
        """
        Cleans and formats the report section, ensuring proper markdown formatting.

        Args:
            report_section (str): The raw report section to clean and format.

        Returns:
            str: The cleaned and formatted report section.
        """
        # Remove any leading/trailing whitespace
        report_section = report_section.strip()

        # Ensure proper markdown formatting for headers
        report_section = re.sub(r'^(#+)\s*(.+)$', r'\1 \2', report_section, flags=re.MULTILINE)

        # Ensure proper markdown formatting for lists
        report_section = re.sub(r'^(\s*)-\s(.+)$', r'\1- \2', report_section, flags=re.MULTILINE)

        # Add an extra newline before headers for better readability
        report_section = re.sub(r'\n(#+\s.+)', r'\n\n\1', report_section)

        return report_section