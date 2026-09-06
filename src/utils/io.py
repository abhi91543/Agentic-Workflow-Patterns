from src.config.logging import logger
from json import JSONDecodeError
from typing import Optional
from typing import Union
from typing import Dict 
from typing import Any 
import hashlib
import json 
import yaml
import os 
import re 


def read_file(path: str) -> Optional[str]:
    """
    Reads the content of a markdown file and returns it as a text object.

    Args:
        path (str): The path to the markdown file.

    Returns:
        Optional[str]: The content of the file as a string, or None if the file could not be read.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content: str = file.read()
            return content
    except FileNotFoundError:
        logger.info(f"File not found: {path}")
        return None
    except Exception as e:
        logger.info(f"Error reading file: {e}")
        return None


def load_yaml(filename: str) -> Dict[str, Any]:
    """
    Load a YAML file and return its contents.

    Args:
        filename (str): The path to the YAML file.

    Returns:
        Dict[str, Any]: The parsed YAML object.

    Raises:
        FileNotFoundError: If the file is not found.
        yaml.YAMLError: If there is an error parsing the YAML file.
        Exception: For any other exceptions.
    """
    try:
        with open(filename, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"File '{filename}' not found.")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file '{filename}': {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading YAML file: {e}")
        raise


def load_json(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load a JSON file and return its contents.

    Args:
        filename (str): The path to the JSON file.

    Returns:
        Optional[Dict[str, Any]]: The parsed JSON object, or None if an error occurs.

    Raises:
        FileNotFoundError: If the file is not found.
        json.JSONDecodeError: If there is an error parsing the JSON file.
        Exception: For any other exceptions.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        logger.error(f"File '{filename}' contains invalid JSON.")
        return None
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        raise


def generate_filename(query: str, extension: str) -> str:
    """
    Generate a filename based on a unique hash of the provided query.

    :param query: The query string for generating a unique hashed filename.
    :param extension: The file extension (e.g., 'json' or 'txt').
    :return: A string representing the generated filename.
    :raises ValueError: If the query is not provided.
    """
    try:
        if not query:
            raise ValueError("Query is missing")
        
        encoded_query = query.encode('utf-8')
        filename = hashlib.md5(encoded_query).hexdigest()
        return f"{filename}.{extension}"
    except Exception as e:
        logger.error(f"Error generating filename: {e}")
        raise


def ensure_directory_exists(path: str) -> None:
    """
    Ensure that the directory exists, creating it if it doesn't.
    
    :param path: The directory path to check or create.
    """
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Directory ensured at: {path}")
    except OSError as e:
        logger.error(f"Failed to create directory at {path}: {str(e)}")
        raise


def save_response(base_dir: str, category: str, response_type: str, content: Union[dict, list, str], file_type: str) -> None:
   """
   Save responses as JSON or text files.
   
   :param base_dir: The base directory where responses will be saved.
   :param category: Either 'coordinator' or 'delegate'.
   :param response_type: The type of response (e.g., 'route', 'consolidate', or delegate name).
   :param content: The response content to save, either JSON serializable (dict or list) or text (str).
   :param file_type: The type of file to save ('json' or 'txt').
   """
   try:
       if category not in ['coordinator', 'delegate']:
           logger.error(f"Invalid category provided: {category}")
           raise ValueError("Invalid category. Must be 'coordinator' or 'delegate'")
       if file_type not in ['json', 'txt']:
           logger.error(f"Invalid file_type provided: {file_type}")
           raise ValueError("Invalid file_type. Must be 'json' or 'txt'")
       
       # Construct directory path with subfolder for both categories
       dir_path = os.path.join(base_dir, category, response_type)
       ensure_directory_exists(dir_path)
       
       # Generate simple filename
       filename = f"{response_type}.{file_type}"
       file_path = os.path.join(dir_path, filename)
       
       # Save content based on file type
       if file_type == 'json':
           with open(file_path, 'w') as f:
               json.dump(content, f, indent=2)
       elif file_type == 'txt':
           with open(file_path, 'w') as f:
               f.write(content)
       
       logger.info(f"Saved {category} {response_type} response as {file_type.upper()} to {file_path}")
   
   except (OSError, ValueError, TypeError) as e:
       logger.error(f"Failed to save response: {str(e)}")
       raise


def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts JSON content from a response text using a regular expression.

    Args:
        response_text (str): The text containing JSON wrapped in <JSON>...</JSON> tags.

    Returns:
        Optional[Dict[str, Any]]: Extracted JSON data as a dictionary, or None if extraction fails.
    """
    try:
        json_match = re.search(r'<JSON>(.*?)</JSON>', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
            return json.loads(json_str)
        else:
            logger.error("No JSON content found in LLM response.")
            return None
    except JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        return None