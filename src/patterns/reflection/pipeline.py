from src.patterns.reflection.critic import Critic
from src.patterns.reflection.actor import Actor
from src.memory.manage import StateManager
from src.config.logging import logger

# Static configuration variables
CONFIG_PATH: str = './config/patterns/reflection.yml'
OUTPUT_DIR: str = './data/patterns/reflection/output'


class Runner:
    """
    The Pipeline class orchestrates the Actor-Critic workflow for generating and revising content based on a given topic.
    
    Attributes:
        topic (str): The topic for content generation.
        num_cycles (int): The number of cycles to run the actor-critic loop.
        state_manager (StateManager): Manages the state and history of the workflow.
        actor (Actor): The actor responsible for generating initial and revised drafts.
        critic (Critic): The critic responsible for reviewing drafts and providing feedback.
    """

    def __init__(self, model_names: dict, topic: str, num_cycles: int):
        """
        Initializes the Pipeline with a topic and number of cycles.

        Args:
            model_names (dict): A dictionary containing model names for 'actor' and 'critic'.
            topic (str): The topic for content generation.
            num_cycles (int): The number of cycles to run the actor-critic loop.
        """
        self.num_cycles = num_cycles
        self.state_manager = StateManager()
        self.actor = Actor(model_names['actor'], topic, CONFIG_PATH, OUTPUT_DIR)
        self.critic = Critic(model_names['critic'], topic, CONFIG_PATH, OUTPUT_DIR)
        logger.info(f"Pipeline initialized with topic: '{topic}', num_cycles: {num_cycles}")

    def run(self) -> str:
        """
        Runs the pipeline for the specified number of cycles.

        Returns:
            str: The final state in markdown format.
        """
        try:
            for cycle in range(self.num_cycles):
                self._run_cycle(cycle)
            logger.info("Pipeline completed all cycles successfully.")
            return self.state_manager.to_markdown()
        except Exception as e:
            logger.error(f"Error in Pipeline.run: {e}")
            raise

    def _run_cycle(self, cycle: int) -> None:
        """
        Runs a single cycle of the actor-critic loop.

        Args:
            cycle (int): The current cycle number.
        """
        try:
            logger.info(f"Running cycle {cycle + 1} of {self.num_cycles}")
            if cycle == 0:
                self._run_initial_cycle()
            else:
                self._run_revised_cycle(cycle)
            logger.info(f"Completed cycle {cycle + 1}")
        except Exception as e:
            logger.error(f"Error in Pipeline._run_cycle (cycle {cycle + 1}): {e}")
            raise

    def _run_initial_cycle(self) -> None:
        """
        Runs the initial cycle, where the actor generates the first draft, and the critic reviews it.
        """
        try:
            logger.info("Running initial cycle")
            initial_draft = self.actor.generate_initial_draft()
            self.state_manager.add_entry("Initial Draft v0", initial_draft)

            initial_review = self.critic.review_draft(initial_draft)
            self.state_manager.add_entry("Initial Review", initial_review)
        except Exception as e:
            logger.error(f"Error in Pipeline._run_initial_cycle: {e}")
            raise

    def _run_revised_cycle(self, cycle: int) -> None:
        """
        Runs a revised cycle, where the actor and critic revise their drafts and reviews.

        Args:
            cycle (int): The current cycle number.
        """
        try:
            logger.info(f"Running revised cycle {cycle + 1}")
            revised_draft = self.actor.revise_draft(self.state_manager.to_markdown(), cycle)
            self.state_manager.add_entry(f"Revised Draft v{cycle}", revised_draft)

            revised_review = self.critic.revise_review(self.state_manager.to_markdown(), cycle)
            self.state_manager.add_entry(f"Revised Review v{cycle}", revised_review)
        except Exception as e:
            logger.error(f"Error in Pipeline._run_revised_cycle (cycle {cycle + 1}): {e}")
            raise


if __name__ == "__main__":
    try:
        model_names = {
            'actor': 'gemini-1.5-flash-001',
            'critic': 'gemini-1.5-pro-001'
        }
        topic = 'perplexity'
        num_cycles = 3

        runner = Runner(model_names=model_names, topic=topic, num_cycles=num_cycles)
        final_state = runner.run()
        logger.info("Actor-Critic pipeline completed successfully.")
        print(final_state)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
