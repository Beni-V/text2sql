import json
from src.infrastructure.config import EnvConfig
from src.infrastructure.database import Database
from src.infrastructure.exceptions import QueryGenerationError, QueryError
from src.infrastructure.open_ai_llm import OpenAILLM
from src.services.database_schema_service import DatabaseSchemaService
from src.services.schema_excerption_service import SchemaExcerptionService

_GENERATION_RULES = """
Pay special attention to the "relationships" section for each table. It contains:
- "foreign_keys": Foreign keys in this table that reference other tables
- "referenced_by": Other tables that have foreign keys referencing this table

Use these relationships to determine the correct JOIN conditions between tables.

Rules:
1. Return ONLY the raw SQL query
2. Don't include any explanations or markdown formatting
3. Use proper JOINs and WHERE clauses as needed
4. Include all relevant columns
5. Pay careful attention to the database schema
6. The db schema format has table names as keys (format: schema_name.table_name),
 which values include:
   - "columns": Column definitions
   - "relationships": Foreign key relationships with other tables
7. Only SELECT queries are allowed
"""

_DEFAULT_PROMPT_TEMPLATE = """
You are an expert SQL assistant for Microsoft SQL Server.
Given a natural language query, generate an accurate SQL query.

Below is the relevant part of the database schema (JSON format) for your reference:
{database_schema}

{generation_rules}

Natural Language Query: "{natural_language_query}"
"""

_REFINE_PROMPT_TEMPLATE = """
You are an expert SQL assistant for Microsoft SQL Server.
I previously asked you to generate an SQL query for the following natural language query:

Natural Language Query: "{natural_language_query}"

You generated this SQL query:
```
{original_query}
```

But when executing it, the following error occurred:
```
{error_message}
```

Please fix the SQL query to address this error.

{generation_rules}

Below is the relevant part of the database schema (JSON format) for your reference:
{database_schema}
"""


class LLMTextToSQLService:
    """Service for generating SQL queries from natural language quries using OpenAI LLM."""

    def __init__(self, prompt_template: str = None, use_rag: bool = True):
        self._open_ai_llm = OpenAILLM()
        self._database = Database()
        self._database_schema_service = DatabaseSchemaService()
        self._schema_excerption_service = SchemaExcerptionService()
        self._config = EnvConfig()
        self._use_rag = use_rag
        self._last_executed_prompt = None

    def generate_and_execute_sql(self, natural_language_query: str) -> dict:
        """Generate SQL from natural language, execute it, and refine if there are errors."""
        sql_query = self.generate_sql(natural_language_query)

        try:
            result = self._database.execute_query(sql_query)
            return {
                "query": sql_query,
                "result": result,
                "refined": False,
                "refinement_attempts": 0,
            }
        except QueryError as error:
            # If execution fails, try to refine the query
            return self._refine_and_execute(
                natural_language_query, sql_query, str(error)
            )

    def _refine_and_execute(
        self, natural_language_query: str, original_query: str, error_message: str, attempt: int = 1
    ) -> dict:
        """Refine the SQL query based on error feedback and execute it again."""
        if attempt > self._max_refinement_attempts:
            raise QueryGenerationError(
                f"Failed to generate a working SQL query after {self._max_refinement_attempts} refinement attempts. "
                f"Last error: {error_message}"
            )

        # Generate a refined query
        refined_query = self._refine_sql(
            natural_language_query, original_query, error_message, attempt
        )

        # Try to execute the refined query
        try:
            result = self._database.execute_query(refined_query)
            return {
                "query": refined_query,
                "result": result,
                "refined": True,
                "refinement_attempts": attempt,
                "original_query": original_query,
                "error_message": error_message,
            }
        except QueryError as error:
            # If still failing, try to refine again recursively
            return self._refine_and_execute(
                natural_language_query, refined_query, str(error), attempt + 1
            )

    def generate_sql(self, natural_language_query: str) -> str:
        try:
            relevant_schema = self._get_schema(natural_language_query)

            # Construct prompt with schema
            prompt = LLMTextToSQLService._construct_prompt(
                relevant_schema, natural_language_query
            )

            # Update the last executed prompt
            self._last_executed_prompt = prompt

            return self._cleanup_generated_query(
                self._open_ai_llm.generate_text(prompt)
            )

        except Exception as e:
            raise QueryGenerationError(f"Failed to generate SQL: {str(e)}")

    def _get_schema(self, natural_language_query: str) -> dict:
        """Retrieve the relevant schema if RAG is enabled, otherwise use the full schema."""
        if self._use_rag:
            # Retrieve relevant schema using RAG
            return self._schema_excerption_service.retrieve_relevant_schema(
                natural_language_query,
                self._initial_amount_of_top_k_for_similarity_search,
            )
        else:
            # Use the full schema for regular generation
            return self._database_schema_service.retrieve(use_cache=True)

    def _refine_sql(
        self, natural_language_query: str, original_query: str, error_message: str, attempt: int
    ) -> str:
        """Refine an SQL query using LLM based on execution error feedback."""
        try:
            combined_query = f"{natural_language_query} {error_message} {original_query}"

            relevant_schema = self._get_schema(combined_query)

            prompt = LLMTextToSQLService._construct_refine_prompt(
                relevant_schema, natural_language_query, original_query, error_message
            )

            # Update the last executed prompt
            self._last_executed_prompt = prompt

            return self._cleanup_generated_query(
                self._open_ai_llm.generate_text(prompt)
            )

        except Exception as e:
            raise QueryGenerationError(f"Failed to refine SQL: {str(e)}")

    @staticmethod
    def _construct_prompt(database_schema: dict, natural_language_query: str) -> str:
        return _DEFAULT_PROMPT_TEMPLATE.format(
            database_schema=(json.dumps(database_schema, indent=2)),
            natural_language_query=natural_language_query,
            generation_rules=_GENERATION_RULES,
        )

    @staticmethod
    def _construct_refine_prompt(
        database_schema: dict,
        natural_language_query: str,
        original_query: str,
        error_message: str,
    ) -> str:
        return _REFINE_PROMPT_TEMPLATE.format(
            database_schema=(json.dumps(database_schema, indent=2)),
            natural_language_query=natural_language_query,
            original_query=original_query,
            error_message=error_message,
            generation_rules=_GENERATION_RULES,
        )

    @staticmethod
    def _cleanup_generated_query(generated_query: str) -> str:
        return generated_query.replace("```sql", "").replace("```", "").strip()

    def set_generation_mode(self, use_rag: bool) -> None:
        self._use_rag = use_rag

    def get_last_executed_prompt(self) -> str:
        return self._last_executed_prompt

    @property
    def _initial_amount_of_top_k_for_similarity_search(self) -> int:
        return 5

    @property
    def _max_refinement_attempts(self) -> int:
        return 3
