# Pattern 6 - Task Decomposition

## Overview

The **Task Decomposition** is a design pattern where a *Coordinator Agent* manages the execution of a complex task by dividing it into multiple independent subtasks. In this pattern, the tasks are provided by the user rather than being automatically deduced by the coordinator. Each subtask is then processed by a separate *Sub-Task Agent* in parallel. After all subtasks are completed, the coordinator gathers and combines the results to produce the final output.

This pattern is beneficial for enhancing efficiency and scalability, especially for tasks that can be divided into smaller, independently executable units.

<p align="center">
    <img src="../../../img/framework/task_decomposition.png" alt="Task Decomposition" width="775"/>
</p>

## Key Components

### CoordinatorAgent

- Receives the complex task input and subtask definitions from the user
- Manages the decomposition of the task based on user-provided subtasks
- Spawns sub-agents for each subtask
- Waits until all sub-agents complete their assigned tasks
- Combines results from all sub-agents into the final output

### SubTaskAgent

- Receives a specific subtask from the coordinator
- Processes the subtask independently
- Returns the result to the coordinator

## Process Flow

1. The CoordinatorAgent receives an input message containing the document content.
2. The coordinator decomposes the task into subtasks.
3. For each subtask:
   - The coordinator creates a SubTaskAgent.
   - The coordinator sends a message to the SubTaskAgent with the subtask details.
4. The coordinator creates tasks for all SubTaskAgents to process their subtasks concurrently.
5. Each SubTaskAgent:
   - Extracts the document and task from the received message.
   - Calls the LLM to process the subtask.
   - Returns the extraction result as a message.
6. The coordinator waits for all SubTaskAgents to complete their tasks.
7. Once all results are collected, the coordinator combines them into a structured summary.
8. The coordinator returns the final combined result as a message to the original sender.