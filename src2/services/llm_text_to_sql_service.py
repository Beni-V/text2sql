from typing import Dict, Any
import json

from src2.infrastructure.database_facade import DatabaseFacade
from src2.infrastructure.llm_facade import LLMFacade
from src2.infrastructure.exceptions import QueryGenerationError
from src2.infrastructure.config import EnvConfig
from src2.services.database_schema_service import DatabaseSchemaService


class LLMTextToSQLService:
    """
    Service for generating SQL queries from natural language questions.
    Uses LLM to generate SQL and executes it against the database.
    """

    DEFAULT_PROMPT_TEMPLATE = """
                You are an expert SQL assistant for Microsoft SQL Server.
                Given a natural language question, generate an accurate SQL query.
                
                Database schema (JSON format):
                {schema_json}
                
                Rules:
                1. Return ONLY the raw SQL query
                2. Don't include any explanations or markdown formatting
                3. Use proper JOINs and WHERE clauses as needed
                4. Include all relevant columns
                
                Question: "{question}"
                
                SQL:
                """

    def __init__(self, prompt_template: str = None):
        """Initialize the service with required dependencies."""
        self.llm_facade = LLMFacade()
        self.database_facade = DatabaseFacade()
        self.schema_service = DatabaseSchemaService()
        self.config = EnvConfig()
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE

    def generate_sql(self, natural_language_question: str) -> str:
        """
        Generate SQL query from a natural language question.

        Args:
            natural_language_question: User question in natural language

        Returns:
            Generated SQL query
        """
        try:
            # Get schema information
            schema_info = self.schema_service.get_schema_information()

            # Format the schema as JSON if it's not already a string
            schema_json = (
                json.dumps(schema_info, indent=2)
                if not isinstance(schema_info, str)
                else schema_info
            )

            # Format the prompt with schema info and question
            prompt = self.prompt_template.format(
                schema_json=schema_json, question=natural_language_question
            )

            # Generate SQL using LLM
            generated_sql = self.llm_facade.generate_text(prompt)

            return generated_sql

        except Exception as e:
            raise QueryGenerationError(
                f"Failed to generate SQL: {str(e)}", original_error=e
            )

    def get_model_name(self) -> str:
        """Get the name of the LLM model being used."""
        return self.llm_facade.get_model_name()
