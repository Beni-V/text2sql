from src.infrastructure.config import EnvConfig
from src.infrastructure.database import Database
from src.infrastructure.exceptions import QueryGenerationError, QueryError
from src.infrastructure.open_ai_llm import OpenAILLM
from src.services.database_schema_service import DatabaseSchemaService
from src.services.schema_retrieval_service import SchemaRetrievalService


class LLMTextToSQLService:
    """Service for generating SQL queries from natural language questions using OpenAI LLM."""

    _DEFAULT_PROMPT_TEMPLATE = """
                                You are an expert SQL assistant for Microsoft SQL Server.
                                Given a natural language question, generate an accurate SQL query.
                                
                                Below is the relevant part of the database schema (JSON format) for your reference:
                                {database_schema}
                                
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
                                6. The db schema format has table names as keys, which values include:
                                   - "table_schema_name": The schema the table belongs to
                                   - "columns": Column definitions
                                   - "relationships": Foreign key relationships with other tables
                                
                                Question: "{question}"
                            """
                            
    _REFINE_PROMPT_TEMPLATE = """
                                You are an expert SQL assistant for Microsoft SQL Server.
                                I previously asked you to generate a SQL query for the following question:
                                
                                Question: "{question}"
                                
                                You generated this SQL query:
                                ```sql
                                {original_query}
                                ```
                                
                                But when executing it, the following error occurred:
                                ```
                                {error_message}
                                ```
                                
                                Please fix the SQL query to address this error.
                                Pay special attention to the "relationships" section for each table in the schema. It contains:
                                - "foreign_keys": Foreign keys in this table that reference other tables
                                - "referenced_by": Other tables that have foreign keys referencing this table
                                
                                Use these relationships to determine the correct JOIN conditions between tables.
                                
                                Only return the corrected SQL query with no explanations or markdown.
                                
                                Below is the relevant part of the database schema (JSON format) for your reference:
                                {database_schema}
                            """

    def __init__(self, prompt_template: str = None):
        self._open_ai_llm = OpenAILLM()
        self._database = Database()
        self._database_schema_service = DatabaseSchemaService()
        self._schema_retrieval_service = SchemaRetrievalService()
        self._config = EnvConfig()
        self._prompt_template = prompt_template or self._DEFAULT_PROMPT_TEMPLATE
        self._max_refinement_attempts = 3

    def generate_and_execute_sql(self, natural_language_question: str) -> dict:
        """Generate SQL from natural language, execute it, and refine if there are errors."""
        sql_query = self.generate_sql(natural_language_question)
        
        # Try to execute the query
        try:
            result = self._database.execute_query(sql_query)
            return {
                "query": sql_query,
                "result": result,
                "refined": False,
                "refinement_attempts": 0
            }
        except QueryError as error:
            # If execution fails, try to refine the query
            return self._refine_and_execute(natural_language_question, sql_query, str(error))
    
    def _refine_and_execute(self, question: str, original_query: str, error_message: str, attempt: int = 1) -> dict:
        """Refine the SQL query based on error feedback and execute it again."""
        if attempt > self._max_refinement_attempts:
            raise QueryGenerationError(
                f"Failed to generate a working SQL query after {self._max_refinement_attempts} refinement attempts. "
                f"Last error: {error_message}"
            )
        
        # Generate a refined query
        refined_query = self._refine_sql(question, original_query, error_message)
        
        # Try to execute the refined query
        try:
            result = self._database.execute_query(refined_query)
            return {
                "query": refined_query,
                "result": result,
                "refined": True,
                "refinement_attempts": attempt,
                "original_query": original_query,
                "error_message": error_message
            }
        except QueryError as error:
            # If still failing, try to refine again recursively
            return self._refine_and_execute(question, refined_query, str(error), attempt + 1)

    def generate_sql(self, natural_language_question: str) -> str:
        try:
            # Retrieve relevant schema using RAG
            relevant_schema = self._schema_retrieval_service.retrieve_relevant_schema(
                natural_language_question
            )
            
            # Construct prompt with only relevant schema
            prompt = self._construct_prompt(
                relevant_schema, natural_language_question
            )
            
            return (
                self._open_ai_llm.generate_text(prompt)
                .replace("```sql", "")
                .replace("```", "")
                .strip()
            )

        except Exception as e:
            raise QueryGenerationError(f"Failed to generate SQL: {str(e)}")
            
    def _refine_sql(self, question: str, original_query: str, error_message: str) -> str:
        """Refine an SQL query using LLM based on execution error feedback."""
        try:
            # For refinement, retrieve schema that might be more relevant based on the error
            combined_query = f"{question} {error_message} {original_query}"
            relevant_schema = self._schema_retrieval_service.retrieve_relevant_schema(
                combined_query, top_k=15  # Increase top_k for refinement
            )
            
            prompt = self._construct_refine_prompt(
                relevant_schema, 
                question,
                original_query,
                error_message
            )
            return (
                self._open_ai_llm.generate_text(prompt)
                .replace("```sql", "")
                .replace("```", "")
                .strip()
            )
        except Exception as e:
            raise QueryGenerationError(f"Failed to refine SQL: {str(e)}")

    def _construct_prompt(
        self, database_schema: dict, natural_language_question: str
    ) -> str:
        return self._prompt_template.format(
            database_schema=database_schema, question=natural_language_question
        )
        
    def _construct_refine_prompt(
        self, database_schema: dict, question: str, original_query: str, error_message: str
    ) -> str:
        return self._REFINE_PROMPT_TEMPLATE.format(
            database_schema=database_schema,
            question=question,
            original_query=original_query,
            error_message=error_message
        )
