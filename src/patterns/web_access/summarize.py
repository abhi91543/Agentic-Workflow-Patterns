from src.patterns.web_access.tasks import SummarizeTask
from src.llm.generate import ResponseGenerator
from src.prompt.manage import TemplateManager
from src.utils.io import generate_filename
from src.config.logging import logger
from src.utils.io import read_file
from typing import Dict
import os


class WebContentSummarizeAgent(SummarizeTask):
    """
    Agent for summarizing scraped web content using a language model and predefined templates.
    
    Attributes:
        INPUT_DIR (str): Directory path for scraped content to be summarized.
        OUTPUT_DIR (str): Directory path to save generated summaries.
        TEMPLATE_PATH (str): Path to template configuration file for generating instructions.
    """
    INPUT_DIR = './data/patterns/web_access/output/scrape'
    OUTPUT_DIR = './data/patterns/web_access/output/summarize'
    TEMPLATE_PATH = './config/patterns/web_access.yml'

    def __init__(self) -> None:
        """
        Initializes WebContentSummarizeAgent with a template manager and response generator.
        """
        self.template_manager = TemplateManager(self.TEMPLATE_PATH)
        self.response_generator = ResponseGenerator()

    def _read_scraped_content(self, query: str) -> str:
        """
        Reads scraped content from the input directory based on the query.

        Args:
            query (str): Query string to locate the specific scraped content.

        Returns:
            str: Scraped content as a string.
        """
        try:
            logger.info(f"Reading scraped content for query: '{query}'")
            input_file_path = os.path.join(self.INPUT_DIR, generate_filename(query, 'txt'))
            return read_file(input_file_path)
        except Exception as e:
            logger.error(f"Error reading scraped content: {e}")
            raise

    def _save_summary(self, summary: str, query: str) -> None:
        """
        Saves the generated summary to the specified output directory.

        Args:
            summary (str): Generated summary to save.
            query (str): Query string used to generate the filename.
        """
        output_path = os.path.join(self.OUTPUT_DIR, f"{generate_filename(query, 'txt')}")
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            logger.info(f"Saving summary to {output_path}")
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(summary)
            logger.info("Summary saved successfully.")
        except Exception as e:
            logger.error(f"Error saving summary: {e}", exc_info=True)
            raise

    def run(self, model_name: str, query: str) -> str:
        """
        Executes the summarization process for scraped content, generating a summary and saving it.

        Args:
            model_name (str): Model name to be used for summarization.
            query (str): Query string to contextualize the summary.

        Returns:
            str: Generated summary.
        """
        try:
            # Read content specific to the query
            scraped_content = self._read_scraped_content(query)

            # Generate prompt template
            logger.info("Fetching and processing template for response generation.")
            template: Dict[str, str] = self.template_manager.create_template('tools', 'summarize')
            system_instruction = template['system']
            user_instruction = self.template_manager.fill_template(
                template['user'], query=query, scraped_content=scraped_content
            )

            # Generate response
            logger.info("Generating response from LLM.")
            response = self.response_generator.generate_response(
                model_name, system_instruction, [user_instruction]
            )
            summary = response.text.strip()
            logger.info("Response generated successfully.")

            # Save the summary
            self._save_summary(summary, query)
            
            return summary
        
        except Exception as e:
            logger.error(f"Error during summarization process: {e}", exc_info=True)
            raise
