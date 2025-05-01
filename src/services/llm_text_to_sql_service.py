import json

from src.infrastructure.config import EnvConfig
from src.infrastructure.database_facade import DatabaseFacade
from src.infrastructure.exceptions import QueryGenerationError
from src.infrastructure.llm_facade import LLMFacade
from src.services.database_schema_service import DatabaseSchemaService


class LLMTextToSQLService:
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
                                5. Pay careful attention to the database schema
                                6. the db schema format are table names as keys, which values are its 
                                    schema name and columns, columns value will be another dict with the column data.

                                Question: "{question}"
                            """

    def __init__(self, prompt_template: str = None):
        self.llm_facade = LLMFacade()
        self.database_facade = DatabaseFacade()
        self.schema_service = DatabaseSchemaService()
        self.config = EnvConfig()
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE

    def generate_sql(self, natural_language_question: str) -> str:
        try:
            schema_info = self.schema_service.get_schema_information()

            schema_json = (
                json.dumps(schema_info, indent=2)
                if not isinstance(schema_info, str)
                else schema_info
            )

            prompt = self.prompt_template.format(
                schema_json=schema_json, question=natural_language_question
            )

            generated_sql = self.llm_facade.generate_text(prompt)

            return generated_sql

        except Exception as e:
            raise QueryGenerationError(
                f"Failed to generate SQL: {str(e)}", original_error=e
            )

    def get_model_name(self) -> str:
        """Get the name of the LLM model being used."""
        return self.llm_facade.get_model_name()
