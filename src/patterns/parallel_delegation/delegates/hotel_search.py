from src.patterns.parallel_delegation.agent import Agent
from src.patterns.web_access.pipeline import run
from src.commons.message import Message
from src.utils.io import save_response
from src.config.logging import logger
from typing import Dict
from typing import Any 
import asyncio
import json


class HotelSearchAgent(Agent):
    """
    An agent that processes hotel search queries, generating a structured response 
    based on the input query, performing a web search, and returning a summarized result.
    
    Attributes:
        name (str): The name of the agent.
        template_manager (TemplateManager): Manages templates for generating queries and instructions.
        response_generator (ResponseGenerator): Generates responses using an LLM.
    """

    async def process(self, message: Message) -> Message:
        """
        Processes a hotel search message by generating a structured response based on
        the input query, conducting a web search, and returning a summarized result.
        
        Args:
            message (Message): The incoming message containing the search query.
        
        Returns:
            Message: A message with the summarized hotel search results or an error response.
        """
        logger.info(f"{self.name} processing message: {message.content}")
        query = message.content
        
        try:
            # Create template for processing the query
            template: Dict[str, Any] = self.template_manager.create_template('delegate', 'hotel_search')
            system_instructions: str = template['system']
            response_schema: Dict[str, Any] = template['schema']
            user_instructions: str = self.template_manager.fill_template(template['user'], query=query)
            contents = [user_instructions]

            # Generate response based on the template and query
            logger.info(f"Generating response for hotel query: {query}")
            response = await asyncio.to_thread(
                self.response_generator.generate_response,
                'gemini-1.5-flash-001',
                system_instructions,
                contents,
                response_schema
            )
            
            # Parse the response for a web search query
            out_dict: Dict[str, Any] = json.loads(response.text.strip())
            save_response('./data/patterns/parallel_delegation/output', 'delegate', 'hotel_search', out_dict, 'json')
            web_search_query: str = out_dict.get('web_search_query', '')
            if not web_search_query:
                raise ValueError("Web search query missing from the response.")

            # Run the web search based on the extracted query
            logger.info(f"Running web search for query: {web_search_query}")
            web_search_results_summary: str = await asyncio.to_thread(run, web_search_query)
            save_response('./data/patterns/parallel_delegation/output', 'delegate', 'hotel_search', web_search_results_summary, 'txt')
            return Message(
                content=web_search_results_summary,
                sender=self.name, 
                recipient="TravelPlannerAgent",
                metadata={"entity_type": "HOTEL"}
            )

        except Exception as e:
            # Log and return error message
            logger.error(f"Error in {self.name}: {e}")
            return Message(
                content="I apologize, but I couldn't process the hotel information at this time.", 
                sender=self.name,
                recipient="TravelPlannerAgent",
                metadata={"entity_type": "HOTEL"}
            )
