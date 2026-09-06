from src.utils.io import generate_filename
from src.config.logging import logger
from src.utils.io import load_yaml
from typing import Union
from typing import Tuple
from typing import Dict 
from typing import Any 
import requests
import json
import os


# Static paths
CREDENTIALS_PATH = './credentials/key.yml'
SEARCH_RESULTS_OUTPUT_DIR = './data/patterns/web_access/output/search'

class SerpAPIClient:
    """
    Client for interacting with the SERP API to perform search queries.
    """

    def __init__(self, api_key: str):
        """
        Initializes SerpAPIClient with the provided API key.

        Args:
            api_key (str): API key for authenticating with the SERP API.
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search.json"

    def search(self, query: str, engine: str = "google", location: str = "") -> Union[Dict[str, Any], Tuple[int, str]]:
        """
        Executes a search query using the SERP API.

        Args:
            query (str): Search query string.
            engine (str, optional): Search engine to use (default is "google").
            location (str, optional): Location for the search query (default is "").

        Returns:
            Union[Dict[str, Any], Tuple[int, str]]: Search results as a JSON dictionary if successful, 
            or a tuple with HTTP status code and error message if the request fails.
        """
        params = {
            "engine": engine,
            "q": query,
            "api_key": self.api_key,
            "location": location
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Request to SERP API failed: {e}")
            return response.status_code, str(e)

def load_api_key(credentials_path: str) -> str:
    """
    Loads the API key from a YAML file.

    Args:
        credentials_path (str): Path to the YAML file containing API credentials.

    Returns:
        str: API key extracted from the YAML file.

    Raises:
        KeyError: If 'serp' or 'key' keys are missing in the YAML file.
    """
    config = load_yaml(credentials_path)
    return config['serp']['key']

def log_top_search_results(results: Dict[str, Any], top_n: int = 5) -> None:
    """
    Logs the top N search results.

    Args:
        results (Dict[str, Any]): Search results from the SERP API.
        top_n (int, optional): Number of top results to log (default is 10).
    """
    logger.info(f"Top {top_n} Search Results:")
    for i, result in enumerate(results.get('organic_results', [])[:top_n], start=1):
        logger.info(f"Result #{i}:")
        logger.info(f"  Position: {result.get('position')}")
        logger.info(f"  Title: {result.get('title')}")
        logger.info(f"  Link: {result.get('link')}")
        logger.info(f"  Snippet: {result.get('snippet')}")
        logger.info('-' * 100)

def save_top_search_results_to_json(results: Dict[str, Any], output_path: str, top_n: int = 5) -> None:
    """
    Saves the top N search results to a JSON file.

    Args:
        results (Dict[str, Any]): Search results from the SERP API.
        output_path (str): File path to save the JSON output.
        top_n (int, optional): Number of top results to save (default is 10).
    """
    top_results = [
        {
            "Position": result.get('position'),
            "Title": result.get('title'),
            "Link": result.get('link'),
            "Snippet": result.get('snippet')
        }
        for result in results.get('organic_results', [])[:top_n]
    ]

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump({"Top Results": top_results}, json_file, indent=4)

    logger.info(f"Top {top_n} search results saved to {output_path}")

def run(raw_query: str, search_query: str, location: str) -> None:
    """
    Executes the search using SERP API, logs the top results, and saves them to a JSON file.

    Args:
        raw_query (str): Raw query string for filename generation.
        search_query (str): Search query for the SERP API.
        location (str): Location for the search query.
    """
    # Load the API key
    api_key = load_api_key(CREDENTIALS_PATH)

    # Initialize the SERP API client
    serp_client = SerpAPIClient(api_key)

    # Perform the search
    results = serp_client.search(search_query, location=location)

    # Process results if the search was successful
    if isinstance(results, dict):
        # Log and save the top search results
        log_top_search_results(results)
        output_path = os.path.join(SEARCH_RESULTS_OUTPUT_DIR, generate_filename(raw_query, 'json'))
        save_top_search_results_to_json(results, output_path)
    else:
        # Handle the error response
        status_code, error_message = results
        logger.error(f"Search failed with status code {status_code}: {error_message}")

if __name__ == "__main__":
    search_query = "greek restaurants"
    location = 'frisco, texas'
    run(search_query, location)
