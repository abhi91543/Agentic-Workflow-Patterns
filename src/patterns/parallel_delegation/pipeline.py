from src.patterns.parallel_delegation.delegates.car_rental_search import CarRentalSearchAgent
from src.patterns.parallel_delegation.delegates.flight_search import FlightSearchAgent
from src.patterns.parallel_delegation.delegates.hotel_search import HotelSearchAgent
from src.patterns.parallel_delegation.coordinator import TravelPlannerAgent
from src.commons.message import Message
from src.config.logging import logger
from typing import Optional
import asyncio


async def pipeline() -> None:
    """
    Initializes sub-agents (flight, hotel, car rental) and the TravelPlannerAgent,
    then processes a user query to find travel arrangements. Logs the response or any error encountered.
    """
    # Initialize sub-agents
    flight_agent = FlightSearchAgent(name="FlightSearchAgent")
    hotel_agent = HotelSearchAgent(name="HotelSearchAgent")
    car_rental_agent = CarRentalSearchAgent(name="CarRentalSearchAgent")

    # Instantiate the TravelPlannerAgent with sub-agents
    travel_planner = TravelPlannerAgent(
        name="TravelPlannerAgent",
        sub_agents=[flight_agent, hotel_agent, car_rental_agent]
    )

    # Define the user query
    user_query: str = "I need a flight from New York to Dallas, a hotel in downtown Dallas, and a rental car for next week."
    initial_message = Message(content=user_query, sender="User", recipient="TravelPlannerAgent")

    # Process the query asynchronously
    try:
        response: Optional[Message] = await travel_planner.process(initial_message)
        if response:
            logger.info(f"Query: {user_query}")
            logger.info(f"Response: {response.content}")
        else:
            logger.warning("No response generated from the travel planner agent.")
    
    except Exception as e:
        logger.error(f"Error processing query '{user_query}': {e}")


if __name__ == "__main__":
    # Execute the async pipeline
    asyncio.run(pipeline())
