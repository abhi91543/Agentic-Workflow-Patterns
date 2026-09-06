from src.patterns.reflection.agent import ContentGenerator
from src.patterns.reflection.agent import Agent
from src.config.logging import logger 


class DraftReviewGenerator(ContentGenerator):
    """
    DraftReviewGenerator is responsible for generating a review for an initial draft.
    
    Methods:
    --------
    generate(model_name, template_manager, response_generator, draft: str) -> str:
        Generates a review based on the provided draft content.
    """

    def generate(self, model_name, template_manager, response_generator, draft: str) -> str:
        """
        Generate a review for the given draft.

        Parameters:
        -----------
        model_name : str
            The name of the model to be used for generating the review.
        template_manager : TemplateManager
            The manager responsible for handling templates.
        response_generator : ResponseGenerator
            The generator that produces the response based on the instructions.
        draft : str
            The draft content that needs to be reviewed.

        Returns:
        --------
        str
            The generated review content.
        """
        template = template_manager.create_template('critic', 'review')
        system_instruction = template['system']
        user_instruction = template_manager.fill_template(template['user'], article=draft)
        return response_generator.generate_response(model_name, system_instruction, [user_instruction], template['schema'])


class ReviewRevisionGenerator(ContentGenerator):
    """
    ReviewRevisionGenerator is responsible for generating a revised review based on the previous review state.
    
    Methods:
    --------
    generate(model_name, template_manager, response_generator, state: str) -> str:
        Generates a revised review based on the provided previous review state.
    """

    def generate(self, model_name, template_manager, response_generator, state: str) -> str:
        """
        Generate a revised review using the previous review state.

        Parameters:
        -----------
        model_name : str
            The name of the model to be used for generating the revised review.
        template_manager : TemplateManager
            The manager responsible for handling templates.
        response_generator : ResponseGenerator
            The generator that produces the response based on the instructions.
        state : str
            The previous review state that is to be revised.

        Returns:
        --------
        str
            The revised review content.
        """
        template = template_manager.create_template('critic', 'revise')
        system_instruction = template['system']
        user_instruction = template_manager.fill_template(template['user'], history=state)
        return response_generator.generate_response(model_name, system_instruction, [user_instruction], template['schema'])


class Critic(Agent):
    """
    Critic is responsible for reviewing and revising content drafts.
    
    Methods:
    --------
    review_draft(draft: str) -> str:
        Reviews the provided draft and saves the review.
    revise_review(state: str, version: int) -> str:
        Revises an existing review and saves the revised version.
    """

    def review_draft(self, draft: str) -> str:
        """
        Review the provided draft and save the review.

        Parameters:
        -----------
        draft : str
            The draft content that needs to be reviewed.

        Returns:
        --------
        str
            The generated review content.

        Raises:
        -------
        Exception
            If an error occurs during the review process.
        """
        try:
            review = self._generate_content(DraftReviewGenerator(), draft=draft)
            self._save_content(review.text, "feedback", 0)
            return review
        except Exception as e:
            logger.error(f"Error reviewing draft: {e}")
            raise

    def revise_review(self, state: str, version: int) -> str:
        """
        Revise an existing review based on its current state and save the revised version.

        Parameters:
        -----------
        state : str
            The current state of the review to be revised.
        version : int
            The version number for the revised review.

        Returns:
        --------
        str
            The revised review content.

        Raises:
        -------
        Exception
            If an error occurs during the review revision process.
        """
        try:
            revised_review = self._generate_content(ReviewRevisionGenerator(), state=state)
            self._save_content(revised_review.text, "feedback", version)
            return revised_review
        except Exception as e:
            logger.error(f"Error revising review: {e}")
            raise
