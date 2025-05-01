"""
SQL Generation Service.
Implements the high-level service for SQL query generation.
"""

from typing import Dict, Any

from src.utils.exceptions import QueryGenerationError


class LLMSQLGenerator:
    """
    Implementation of SQLQueryGenerator using a language model.
    Uses Strategy pattern for different LLM services.
    """

    def __init__(self, llm_service, prompt_template):
        """
        Initialize with LLM service and prompt template.

        Args:
            llm_service: Language model service
            prompt_template: Prompt template for generation
        """
        self.llm_service = llm_service
        self.prompt_template = prompt_template

    def generate_sql_query(
        self, natural_language_question: str, schema_info: Dict[str, Any]
    ) -> str:
        """
        Generate SQL query from natural language using LLM.

        Args:
            natural_language_question: User's question in natural language
            schema_info: Database schema information

        Returns:
            Generated SQL query string

        Raises:
            QueryGenerationError: If generation fails
        """
        try:
            # Format the prompt with schema info and question
            prompt = self.prompt_template.format(
                schema_json=schema_info, question=natural_language_question
            )

            # Generate SQL using the LLM service
            return self.llm_service.generate_text(prompt)

        except Exception as e:
            raise QueryGenerationError(
                f"Failed to generate SQL query: {str(e)}", original_error=e
            )
