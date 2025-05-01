from src.infrastructure.config import EnvConfig
from src.infrastructure.database import Database
from src.infrastructure.exceptions import QueryGenerationError
from src.open_ai_llm.open_ai_llm import OpenAILLM
from src.services.database_schema_service import DatabaseSchemaService


class LLMTextToSQLService:
    """Service for generating SQL queries from natural language questions using OpenAI LLM."""

    _DEFAULT_PROMPT_TEMPLATE = """
                                You are an expert SQL assistant for Microsoft SQL Server.
                                Given a natural language question, generate an accurate SQL query.
                                
                                Database schema (JSON format):
                                {database_schema}
                                
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
        self._open_ai_llm = OpenAILLM()
        self._database = Database()
        self._database_schema_service = DatabaseSchemaService()
        self._config = EnvConfig()
        self._prompt_template = prompt_template or self._DEFAULT_PROMPT_TEMPLATE

    def generate_sql(self, natural_language_question: str) -> str:
        try:
            prompt = self._construct_prompt(
                self._database_schema_service.retrieve(), natural_language_question
            )
            return self._open_ai_llm.generate_text(prompt)

        except Exception as e:
            raise QueryGenerationError(f"Failed to generate SQL: {str(e)}")

    def _construct_prompt(self, database_schema: dict, natural_language_question: str) -> str:
        return self._prompt_template.format(
            database_schema=database_schema, question=natural_language_question
        )
