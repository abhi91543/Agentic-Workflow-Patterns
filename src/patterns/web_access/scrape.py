from src.patterns.web_access.tasks import ScrapeTask
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from src.utils.io import generate_filename
from src.config.logging import logger
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import Tuple
from typing import Dict 
from typing import List 
from typing import Any 
import requests
import json
import time
import os
import re


class WebScrapeAgent(ScrapeTask):
    """
    WebScrapeAgent is responsible for scraping content from websites based on search results.

    Attributes:
        INPUT_DIR (str): Directory path where search results (JSON) are stored.
        OUTPUT_DIR (str): Directory path where scraped content is saved.
        MAX_WORKERS (int): Maximum number of concurrent threads for scraping.
    """
    INPUT_DIR = "./data/patterns/web_access/output/search"
    OUTPUT_DIR = "./data/patterns/web_access/output/scrape"
    MAX_WORKERS = 10

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans extracted text by removing extra spaces and newlines.

        Args:
            text (str): Raw extracted text.

        Returns:
            str: Cleaned text with unnecessary spaces removed.
        """
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def get_domain(url: str) -> str:
        """
        Extracts the domain name from a URL.

        Args:
            url (str): Full URL.

        Returns:
            str: Domain name extracted from the URL.
        """
        return urlparse(url).netloc

    def scrape_website(self, url: str) -> str:
        """
        Scrapes content from a specified URL, with a timeout of 5 seconds. 

        Args:
            url (str): Website URL to be scraped.

        Returns:
            str: Extracted text content or an empty string if an error occurs.
        """
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            extracted_text = ' '.join(elem.get_text() for elem in text_elements)
            return self.clean_text(extracted_text)
        except requests.Timeout:
            logger.warning(f"Skipping {url} due to timeout.")
            return ""
        except requests.RequestException as e:
            logger.warning(f"Error scraping {url}: {e}")
            return ""

    def scrape_with_delay(self, result: Dict[str, Any], delay: int) -> Tuple[Dict[str, Any], str]:
        """
        Scrapes a website after a delay to avoid server overload.

        Args:
            result (Dict[str, Any]): Search result containing URL and metadata.
            delay (int): Delay in seconds before initiating scrape.

        Returns:
            Tuple[Dict[str, Any], str]: Original result and scraped content.
        """
        time.sleep(delay)
        content = self.scrape_website(result['Link'])
        return result, content

    def scrape_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Concurrently scrapes content from provided search results.

        Args:
            results (List[Dict[str, Any]]): List of search result dictionaries.

        Returns:
            List[Dict[str, Any]]: List of dictionaries with title, URL, snippet, and content.
        """
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        scraped_results = []
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            future_to_result = {executor.submit(self.scrape_with_delay, result, i): result for i, result in enumerate(results)}
            for future in as_completed(future_to_result):
                try:
                    result, content = future.result()
                    if content:
                        scraped_results.append({
                            'title': result['Title'],
                            'url': result['Link'],
                            'snippet': result['Snippet'],
                            'content': content
                        })
                        logger.info(f"Scraped: {result['Title']}")
                    else:
                        logger.info(f"Skipping {result['Title']} due to empty content.")
                except Exception as e:
                    logger.error(f"Error processing result: {e}")
        return scraped_results

    def save_results(self, query: str, scraped_results: List[Dict[str, Any]]) -> None:
        """
        Saves scraped results to a text file.

        Args:
            query (str): Query string used to generate filename.
            scraped_results (List[Dict[str, Any]]): List of scraped results.
        """
        try:
            output_path = os.path.join(self.OUTPUT_DIR, generate_filename(query, 'txt'))

            with open(output_path, 'w', encoding='utf-8') as outfile:
                for result in scraped_results:
                    outfile.write("==== BEGIN ENTRY ====\n")
                    outfile.write(f"TITLE: {result['title']}\n")
                    outfile.write(f"URL: {result['url']}\n")
                    outfile.write(f"SNIPPET: {result['snippet']}\n")
                    outfile.write(f"CONTENT:\n{result['content']}\n")
                    outfile.write("==== END ENTRY ====\n\n")
            logger.info(f"Scraping complete. Results saved to '{output_path}'")
            time.sleep(3)  # Delay to ensure no rapid consecutive saves
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def load_search_results(self, query: str, location: str) -> List[Dict[str, Any]]:
        """
        Loads search results from a JSON file based on the query and location.

        Args:
            query (str): Query string for filename generation.
            location (str): Location identifier for additional file context.

        Returns:
            List[Dict[str, Any]]: List of search result dictionaries.
        """
        try:
            filename = generate_filename(query, 'json')
            file_path = os.path.join(self.INPUT_DIR, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Search results file not found for query: '{query}' and location: '{location}'")
            
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            logger.info(f"Loaded search results from '{filename}'")
            return data.get('Top Results', [])
        except Exception as e:
            logger.error(f"Error loading search results: {e}")
            raise

    def run(self, query: str, location: str) -> None:
        """
        Orchestrates the web scraping process by loading search results, scraping content, and saving the results.

        Args:
            query (str): Query string for identifying relevant search results.
            location (str): Location identifier for loading appropriate files.
        """
        try:
            logger.info(f"Initiating scraping process for query: '{query}' and location: '{location}'")
            results = self.load_search_results(query, location)
            scraped_results = self.scrape_results(results)
            self.save_results(query, scraped_results)
        except Exception as e:
            logger.error(f"Error during scraping process: {e}")
            raise
