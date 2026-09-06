# Pattern 4 - Parallel Delegation

## Overview

The **Parallel Delegation** pattern implements an agentic workflow that processes complex queries by first identifying distinct entities through Named Entity Recognition (NER), then delegating these entities to specialized agents for parallel processing. This pattern is particularly effective for scenarios where multiple independent sub-tasks can be executed concurrently, such as travel planning where flight, hotel, and car rental searches can be performed simultaneously. This is a natural variant of Pattern 3, where we reuse the same use case except the functionality of the coordinator is different - instead of routing based on identified intent, the identified pieces of information after initial query analysis are directly passed on to all subagents that the coordinator controls directly. Similar to Pattern 3, all subagents use the web access pipeline covered in Pattern 2. The pattern leverages asynchronous processing and parallel execution to optimize performance while maintaining a coordinated workflow through a central coordinator agent.

<p align="center">
    <img src="../../../img/framework/parallel_delegation.png" alt="Parallel Delegation" width="800"/>
</p>

## Key Components

### TravelPlannerAgent (Coordinator)
- Performs Named Entity Recognition (NER) on incoming queries
- Identifies distinct entities for parallel processing
- Coordinates asynchronous delegation to specialized agents
- Consolidates parallel results into a coherent response
- Manages entity types:
  - FLIGHT
  - HOTEL
  - CAR_RENTAL
  - UNKNOWN

### Specialized Sub-Agents
- **FlightSearchAgent**
  - Processes flight-related entities asynchronously
  - Generates optimized flight search queries
  - Returns flight information independently

- **HotelSearchAgent**
  - Handles hotel-related entities asynchronously
  - Processes accommodation requests
  - Returns hotel information independently

- **CarRentalSearchAgent**
  - Manages car rental entities asynchronously
  - Processes vehicle rental requests
  - Returns car rental options independently
  


### Asynchronous Pipeline
- Orchestrates the parallel workflow
- Initializes all agents
- Manages asynchronous message flow
- Handles concurrent processing of entities

## Process Flow

1. **Entity Recognition**
   - User query is received by TravelPlannerAgent
   - NER is performed to identify distinct entities
   - Entities are categorized by type (flight, hotel, car rental)

2. **Parallel Delegation**
   - Identified entities are distributed to specialized agents
   - Each agent receives relevant entities asynchronously
   - All agents begin processing concurrently
   - No waiting for other agents to complete

3. **Concurrent Processing**
   - Each sub-agent independently:
     - Generates optimized search queries
     - Performs web searches
     - Processes results
     - Returns findings

4. **Response Consolidation**
   - Coordinator awaits all parallel processes
   - Collects results as they complete
   - Consolidates information into coherent response
   - Returns unified result to user