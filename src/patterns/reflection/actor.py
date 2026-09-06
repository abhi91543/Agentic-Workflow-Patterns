from src.patterns.reflection.agent import ContentGenerator
from src.patterns.reflection.agent import Agent
from src.config.logging import logger


class DraftGenerator(ContentGenerator):
    """
    DraftGenerator is responsible for generating the initial draft using a given topic.
    
    Methods:
    --------
    generate(model_name, template_manager, response_generator, topic: str) -> str:
        Generates the initial draft based on the provided topic.
    """

    def generate(self, model_name, template_manager, response_generator, topic: str) -> str:
        """
        Generate an initial draft using the provided topic.

        Parameters:
        -----------
        model_name : str
            The name of the model to be used for generating the draft.
        template_manager : TemplateManager
            The manager responsible for handling templates.
        response_generator : ResponseGenerator
            The generator that produces the response based on the instructions.
        topic : str
            The topic for which the draft is being generated.

        Returns:
        --------
        str
            The generated draft content.
        """
        template = template_manager.create_template('actor', 'draft')
        system_instruction = template_manager.fill_template(template['system'], topic=topic)
        user_instruction = template_manager.fill_template(template['user'], topic=topic)
        return response_generator.generate_response(model_name, system_instruction, [user_instruction], template['schema'])


class RevisionGenerator(ContentGenerator):
    """
    RevisionGenerator is responsible for generating a revised draft based on the previous draft state.
    
    Methods:
    --------
    generate(model_name, template_manager, response_generator, state: str) -> str:
        Generates a revised draft based on the provided previous draft state.
    """

    def generate(self, model_name, template_manager, response_generator, state: str) -> str:
        """
        Generate a revised draft using the previous draft state.

        Parameters:
        -----------
        model_name : str
            The name of the model to be used for generating the revised draft.
        template_manager : TemplateManager
            The manager responsible for handling templates.
        response_generator : ResponseGenerator
            The generator that produces the response based on the instructions.
        state : str
            The previous draft state that is to be revised.

        Returns:
        --------
        str
            The revised draft content.
        """
        template = template_manager.create_template('actor', 'revise')
        system_instruction = template['system']
        user_instruction = template_manager.fill_template(template['user'], history=state)
        return response_generator.generate_response(model_name, system_instruction, [user_instruction], template['schema'])


class Actor(Agent):
    """
    Actor is responsible for generating and revising content drafts.
    
    Methods:
    --------
    generate_initial_draft() -> str:
        Generates the initial content draft and saves it.
    revise_draft(state: str, version: int) -> str:
        Revises an existing draft and saves the revised version.
    """

    def generate_initial_draft(self) -> str:
        """
        Generate the initial draft and save it.

        Returns:
        --------
        str
            The generated initial draft content.

        Raises:
        -------
        Exception
            If an error occurs during draft generation.
        """
        try:
            draft = self._generate_content(DraftGenerator(), topic=self.topic)
            self._save_content(draft.text, "draft", 0)
            return draft
        except Exception as e:
            logger.error(f"Error generating initial draft: {e}")
            raise

    def revise_draft(self, state: str, version: int) -> str:
        """
        Revise an existing draft based on its current state and save the revised version.

        Parameters:
        -----------
        state : str
            The current state of the draft to be revised.
        version : int
            The version number for the revised draft.

        Returns:
        --------
        str
            The revised draft content.

        Raises:
        -------
        Exception
            If an error occurs during draft revision.
        """
        try:
            revised_draft = self._generate_content(RevisionGenerator(), state=state)
            self._save_content(revised_draft.text, "draft", version)
            return revised_draft
        except Exception as e:
            logger.error(f"Error revising draft: {e}")
            raise
