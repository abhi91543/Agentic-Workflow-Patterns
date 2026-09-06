from src.patterns.semantic_router.agent import Agent
from src.commons.message import Message
from src.utils.io import save_response
from src.config.logging import logger
from typing import Optional
from typing import List
from enum import Enum


class Intent(Enum):
    """
    Enum to define possible user intents for travel planning.
    """
    FLIGHT = 1
    HOTEL = 2
    CAR_RENTAL = 3
    UNKNOWN = 4
    

class TravelPlannerAgent(Agent):
    """
    Travel Planner agent responsible for routing travel-related queries to sub-agents 
    based on detected intent and generating a consolidated response.
    """

    def __init__(self, name: str, sub_agents: List[Agent]):
        """
        Initializes the TravelPlannerAgent with a set of sub-agents and shared resources.

        :param name: Name of the agent.
        :param sub_agents: List of sub-agents responsible for specific tasks like flights, hotels, etc.
        """
        super().__init__(name)
        self.sub_agents = {agent.name: agent for agent in sub_agents}
        logger.info(f"{self.name} initialized with {len(self.sub_agents)} sub-agents.")

    def determine_intent(self, query: str) -> Intent:
        """
        Determines the user's intent based on their query using a response generation model.

        :param query: User's query string.
        :return: Detected intent as an Intent enum value.
        """
        try:
            template = self.template_manager.create_template('coordinator', 'route')
            system_instructions = template.get('system', '')
            user_instructions = self.template_manager.fill_template(template.get('user', ''), query=query)
            response_schema = template.get('schema', '')
            contents = [user_instructions]

            logger.info(f"Generating response to determine intent for query: '{query}'")
            response = self.response_generator.generate_response('gemini-1.5-flash-001', system_instructions, contents, response_schema)
            out_dict = eval(response.text.strip())  # Ensure safe eval usage
            save_response('./data/patterns/semantic_router/output', 'coordinator', 'route', out_dict, 'json')
            intent_str = out_dict.get('intent', 'UNKNOWN').upper()
            logger.info(f"Determined intent: {intent_str}")
            return Intent[intent_str]

        except KeyError as e:
            logger.error(f"Key error while determining intent: {e}")
            return Intent.UNKNOWN
        except Exception as e:
            logger.error(f"Unexpected error while determining intent: {e}")
            return Intent.UNKNOWN

    def route_to_agent(self, intent: Intent) -> Optional[Agent]:
        """
        Routes the query to the appropriate sub-agent based on the determined intent.

        :param intent: The user's detected intent.
        :return: The corresponding sub-agent for the intent or None if not applicable.
        """
        intent_to_agent = {
            Intent.FLIGHT: "FlightSearchAgent",
            Intent.HOTEL: "HotelSearchAgent",
            Intent.CAR_RENTAL: "CarRentalSearchAgent",
            Intent.UNKNOWN: None
        }

        agent_name = intent_to_agent.get(intent)
        if not agent_name:
            logger.error(f"No valid agent found for intent: {intent}")
            return None

        logger.info(f"Routing to agent: '{agent_name}'")
        return self.sub_agents.get(agent_name)

    def process(self, message: Message) -> Message:
        """
        Processes the incoming message, determines intent, routes to the appropriate sub-agent, 
        and returns a consolidated response.

        :param message: The incoming message to process.
        :return: A response message after processing by the sub-agent and consolidation.
        """
        logger.info(f"{self.name} processing message: '{message.content}'")
        
        try:
            query = message.content

            # Determine the user's intent
            intent = self.determine_intent(query)
            
            # Route to the appropriate sub-agent
            sub_agent = self.route_to_agent(intent)
            if sub_agent is None:
                raise ValueError(f"Unknown intent: {intent}")

            sub_message = Message(content=query, sender=self.name, recipient=sub_agent.name, metadata={"intent": intent.name})
            logger.info(f"Delegating message to '{sub_agent.name}'")

            # Get the response from the sub-agent
            sub_response = sub_agent.process(sub_message)
            summary = sub_response.content

            # Consolidate the final response
            template = self.template_manager.create_template('coordinator', 'consolidate')
            system_instructions = self.template_manager.fill_template(template.get('system', ''), query=query, summary=summary)
            user_instructions = self.template_manager.fill_template(template.get('user', ''), query=query, summary=summary)
            contents = [user_instructions]

            logger.info("Generating final response for the user.")
            final_response = self.response_generator.generate_response('gemini-1.5-flash-001', system_instructions, contents)
            final_response_text = final_response.text.strip()
            save_response('./data/patterns/semantic_router/output', 'coordinator', 'consolidate', final_response_text, 'txt')
            return Message(content=final_response_text, sender=self.name, recipient="User")

        except ValueError as e:
            logger.error(f"ValueError occurred: {e}")
            return Message(content="I'm sorry, I could not process your request. Please try again later.", sender=self.name, recipient="User")
        except Exception as e:
            logger.error(f"Unexpected error during processing: {e}")
            return Message(content="I encountered an error while processing your request. Please try again later.", sender=self.name, recipient="User")
