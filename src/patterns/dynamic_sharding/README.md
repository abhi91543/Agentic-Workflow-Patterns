# Pattern 5 - Dynamic Sharding Pattern 

## Overview

The Dynamic Sharding Pattern is an architectural approach designed to efficiently process large datasets by dynamically dividing the workload into smaller, manageable shards and processing them in parallel. This pattern enhances scalability, optimizes resource utilization, and improves the overall performance of systems handling extensive data or requests.
This pattern can be demonstrated through a practical example of fetching biographies of celebrities using web search. The coordinator agent dynamically shards the list of celebrity names and processes each shard concurrently through dynamically created sub-agents.
The coordinator agent in this example represents a basic implementation where it is used to spawn (create) the sub-agents based on the shard size and the size of the items to be processed. 

💡 In a more advanced implementation, this agent can leverage an LLM to deduce patterns and allocate sub-agents by identified classes or groups of shards of varying sizes.

<p align="center">
    <img src="../../../img/framework/dynamic_sharding.png" alt="Dynamic Sharding" width="800"/>
</p>

## Architecture Pattern Explained

### Key Components

1. **Coordinator Agent**:
   - **Role**: Orchestrates the entire data processing workflow.
   - **Responsibilities**:
     - Receives the complete list of items to process (e.g., celebrity names in our example implementation) along with the desired shard size.
     - Dynamically divides the list into smaller shards based on the shard size.
     - Creates sub-agents dynamically for each shard.
     - Initiates parallel processing by assigning shards to sub-agents.
     - Aggregates results from all sub-agents into a final consolidated response.
   - **Benefits**:
     - Decouples task management from execution.
     - Enhances scalability by adjusting the number of shards and sub-agents based on workload.
     - Improves system responsiveness and throughput.

2. **Shard Processing Agents**:
   - **Role**: Handle the processing of individual shards.
   - **Responsibilities**:
     - Receive a shard (subset) of data from the coordinator agent.
     - Process each item within the shard, such as fetching biographies for each celebrity.
     - Perform item-level processing concurrently to maximize efficiency.
     - Return processed results back to the coordinator agent.
   - **Benefits**:
     - Enable fine-grained parallelism within shards.
     - Simplify error handling and retry mechanisms at the shard level.
     - Allow for resource isolation and management per shard.

### Workflow

1. **Input Reception**:
   - The **Coordinator Agent** receives a request containing:
     - A list of celebrity names.
     - The desired shard size (number of items per shard).

2. **Dynamic Sharding**:
   - The coordinator dynamically divides the list of celebrity names into multiple shards based on the specified shard size.
   - For example, a list of 100 celebrities with a shard size of 10 will result in 10 shards.

3. **Dynamic Agent Creation**:
   - For each shard, the coordinator agent creates a new **Shard Processing Agent** dynamically.
   - Each agent is responsible for processing its assigned shard independently.

4. **Parallel Shard Processing**:
   - The coordinator dispatches all shard processing agents concurrently.
   - Shard processing agents begin processing their respective shards in parallel.

5. **Concurrent Item Processing**:
   - Within each shard processing agent:
     - Each item (celebrity name) is processed concurrently using asynchronous tasks.
     - For example, fetching the biography of each celebrity using our previously created web access pipeline (**Pattern 2**).

6. **Result Collection**:
   - Shard processing agents collect the results of processing each item in their shard.
   - Each agent returns its results back to the coordinator agent upon completion.

7. **Result Aggregation**:
   - The coordinator agent waits for all shard processing agents to complete.
   - Aggregates the results from all shards into a single, consolidated response.

8. **Response Delivery**:
   - The consolidated results are sent back to the original requester (e.g., the user or another system component).

