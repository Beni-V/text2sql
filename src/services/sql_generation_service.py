from typing import Dict, Any

from src.utils.exceptions import QueryGenerationError


class LLMSQLGenerator:

    def __init__(self, llm_service, prompt_template):
        self.llm_service = llm_service
        self.prompt_template = prompt_template

    def generate_sql_query(
        self, natural_language_question: str, schema_info: Dict[str, Any]
    ) -> str:
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
