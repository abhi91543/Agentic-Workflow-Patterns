from src.patterns.parallel_delegation.agent import Agent
from src.commons.message import Message
from src.utils.io import save_response
from src.config.logging import logger
from typing import List
from typing import Dict 
from enum import Enum
import asyncio


class EntityType(Enum):
    """
    Enum to represent different entity types that can be identified in a travel planning context.
    """
    FLIGHT = 1
    HOTEL = 2
    CAR_RENTAL = 3
    UNKNOWN = 4


class TravelPlannerAgent(Agent):
    """
    An agent that coordinates travel-related queries, performing Named Entity Recognition (NER)
    to identify query components, routing them to specific sub-agents, and consolidating the results.
    """

    def __init__(self, name: str, sub_agents: List[Agent]) -> None:
        """
        Initializes the TravelPlannerAgent with a list of sub-agents.
        """
        super().__init__(name)
        self.sub_agents: Dict[str, Agent] = {agent.name: agent for agent in sub_agents}
        logger.info(f"{self.name} initialized with {len(self.sub_agents)} sub-agents.")

    async def perform_ner(self, query: str) -> Dict[EntityType, List[str]]:
        """
        Performs Named Entity Recognition (NER) on the query to identify relevant entities.
        """
        try:
            template = self.template_manager.create_template('coordinator', 'ner')
            system_instructions = template['system']
            user_instructions = self.template_manager.fill_template(template['user'], query=query)
            response_schema = template['schema']
            contents = [user_instructions]

            logger.info(f"Performing NER for query: {query}")
            response = await asyncio.to_thread(
                self.response_generator.generate_response,
                'gemini-1.5-flash-001',
                system_instructions,
                contents,
                response_schema
            )

            entities = eval(response.text.strip())  # Caution: Ensure safe eval usage
            entities = entities['entities']
            save_response('./data/patterns/parallel_delegation/output', 'coordinator', 'ner', entities, 'json')
            return {EntityType[k.upper()]: v for k, v in entities.items() if v}
        except Exception as e:
            logger.error(f"Error during NER: {e}")
            return {}

    async def route_to_agents(self, entities: Dict[EntityType, List[str]]) -> List[Message]:
        """
        Routes entities to the appropriate sub-agents and processes them in parallel.
        """
        tasks = []
        for entity_type, entity_values in entities.items():
            agent = None
            if entity_type == EntityType.FLIGHT:
                agent = self.sub_agents.get("FlightSearchAgent")
            elif entity_type == EntityType.HOTEL:
                agent = self.sub_agents.get("HotelSearchAgent")
            elif entity_type == EntityType.CAR_RENTAL:
                agent = self.sub_agents.get("CarRentalSearchAgent")

            if agent:
                task = asyncio.create_task(self.process_entity(agent, entity_type, entity_values))
                tasks.append(task)

        return await asyncio.gather(*tasks)

    async def process_entity(self, agent: Agent, entity_type: EntityType, entity_values: List[str]) -> Message:
        """
        Processes an entity by creating a query message and sending it to the respective agent.
        """
        query = f"{entity_type.name}: {str(entity_values)}"
        message = Message(content=query, sender=self.name, recipient=agent.name, metadata={"entity_type": entity_type.name})
        return await agent.process(message)

    async def consolidate_responses(self, query: str, sub_responses: List[Message]) -> str:
        """
        Consolidates the responses from all sub-agents into a final summarized response.
        """
        template = self.template_manager.create_template('coordinator', 'consolidate')
        system_instructions = template['system']
        user_instructions = self.template_manager.fill_template(
            template['user'],
            query=query,
            flight_summary=next((r.content for r in sub_responses if r.metadata["entity_type"] == "FLIGHT"), ""),
            hotel_summary=next((r.content for r in sub_responses if r.metadata["entity_type"] == "HOTEL"), ""),
            car_rental_summary=next((r.content for r in sub_responses if r.metadata["entity_type"] == "CAR_RENTAL"), "")
        )
        contents = [user_instructions]

        logger.info("Generating final consolidated response for the user.")
        final_response = await asyncio.to_thread(
            self.response_generator.generate_response,
            'gemini-1.5-pro-001',
            system_instructions,
            contents
        )
        summary = final_response.text.strip()
        save_response('./data/patterns/parallel_delegation/output', 'coordinator', 'consolidate', summary, 'txt')
        return summary

    async def process(self, message: Message) -> Message:
        """
        Processes an incoming travel query by performing NER, routing to sub-agents, and consolidating responses.
        """
        logger.info(f"{self.name} processing message: {message.content}")

        try:
            query = message.content

            # Perform Named Entity Recognition
            entities = await self.perform_ner(query)

            # Route to appropriate sub-agents and process in parallel
            sub_responses = await self.route_to_agents(entities)

            # Consolidate the final response
            final_response_text = await self.consolidate_responses(query, sub_responses)

            return Message(content=final_response_text, sender=self.name, recipient="User")
        except Exception as e:
            logger.error(f"Unexpected error during processing: {e}")
            return Message(
                content="I encountered an error while processing your request. Please try again later.",
                sender=self.name,
                recipient="User"
            )
