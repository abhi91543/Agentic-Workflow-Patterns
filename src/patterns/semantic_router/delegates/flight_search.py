from src.patterns.web_access.pipeline import run as web_search
from src.patterns.semantic_router.agent import Agent
from src.commons.message import Message
from src.utils.io import save_response
from src.config.logging import logger
from typing import Optional
import json


class FlightSearchAgent(Agent):
    """
    Agent responsible for handling flight search queries, generating a web search query, 
    and returning summarized results.
    """

    def process(self, message: Message) -> Message:
        """
        Processes flight search queries by generating a web search query and returning summarized results.

        :param message: The incoming message containing the flight query.
        :return: A response message with the flight search results or an error message.
        """
        logger.info(f"{self.name} processing message: '{message.content}'")
        query = message.content
        try:
            template = self.template_manager.create_template('delegate', 'flight_search')
            system_instructions = template.get('system', '')
            response_schema = template.get('schema', '')
            user_instructions = self.template_manager.fill_template(template.get('user', ''), query=query)
            contents = [user_instructions]

            logger.info(f"Generating response for flight query: '{query}'")
            response = self.response_generator.generate_response(
                'gemini-1.5-flash-001', system_instructions, contents, response_schema
            )
            
            try:
                out_dict = json.loads(response.text.strip())
            except json.JSONDecodeError as decode_error:
                logger.error(f"Failed to decode JSON response: {decode_error}")
                return Message(
                    content="Error in parsing response. Please try again later.",
                    sender=self.name,
                    recipient="TravelPlannerAgent"
                )

            web_search_query: Optional[str] = out_dict.get('web_search_query')
            save_response('./data/patterns/semantic_router/output', 'delegate', 'flight_search', out_dict, 'json')
            if not web_search_query:
                logger.warning("Web search query missing from the response.")
                return Message(
                    content="Unable to find relevant flight information at this time.",
                    sender=self.name,
                    recipient="TravelPlannerAgent"
                )

            logger.info(f"Running web search for query: '{web_search_query}'")
            web_search_results_summary = web_search(web_search_query)
            save_response('./data/patterns/semantic_router/output', 'delegate', 'flight_search', web_search_results_summary, 'txt')
            return Message(content=web_search_results_summary, sender=self.name, recipient="TravelPlannerAgent")

        except Exception as e:
            logger.error(f"Error in FlightSearchAgent: {e}")
            return Message(
                content="I apologize, but I couldn't process the flight information at this time.",
                sender=self.name,
                recipient="TravelPlannerAgent"
            )
