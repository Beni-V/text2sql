"""
LLM factory for creating LLM-related objects.
Implements Factory Method pattern.
"""

from src.config.app_config import AppConfig
from src.infrastructure.llm.openai_service import OpenAIService
from src.infrastructure.llm.prompt_templates import SQLGenerationPrompt
from src.services.sql_generation_service import LLMSQLGenerator


class LLMFactory:
    """
    Factory for creating LLM-related objects.
    Implements Factory Method pattern.
    """

    @staticmethod
    def create_llm_service(config: AppConfig):
        """
        Create an LLM service.

        Args:
            config: Application configuration

        Returns:
            LLMService implementation
        """
        return OpenAIService(config)

    @staticmethod
    def create_sql_prompt_template():
        """
        Create a SQL generation prompt template.

        Returns:
            PromptTemplate implementation
        """
        return SQLGenerationPrompt()

    @staticmethod
    def create_sql_generator(llm_service, prompt_template) -> LLMSQLGenerator:
        """
        Create a SQL generator.

        Args:
            llm_service: LLM service
            prompt_template: Prompt template

        Returns:
            LLMSQLGenerator implementing SQLQueryGenerator
        """
        return LLMSQLGenerator(llm_service, prompt_template)
