from typing import Any, Protocol

from src.infrastructure.llm.openai_service import OpenAIService
from src.infrastructure.llm.prompt_templates import SQLGenerationPrompt
from src.utils.exceptions import QueryGenerationError


class LLMSQLGenerator:

    def __init__(
        self, llm_service: OpenAIService, prompt_template: SQLGenerationPrompt
    ) -> None:
        self.llm_service = llm_service
        self.prompt_template = prompt_template

    def generate_sql_query(
        self, natural_language_question: str, schema_info: dict[str, Any]
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
