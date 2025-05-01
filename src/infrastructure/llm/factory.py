from src.config.app_config import AppConfig
from src.infrastructure.llm.openai_service import OpenAIService
from src.infrastructure.llm.prompt_templates import SQLGenerationPrompt
from src.services.sql_generation_service import LLMSQLGenerator


class LLMFactory:

    @staticmethod
    def create_llm_service(config: AppConfig):
        return OpenAIService(config)

    @staticmethod
    def create_sql_prompt_template():
        return SQLGenerationPrompt()

    @staticmethod
    def create_sql_generator(llm_service, prompt_template) -> LLMSQLGenerator:
        return LLMSQLGenerator(llm_service, prompt_template)
