from typing import Dict, Any, Optional
import os

from openai import OpenAI
from src.config.app_config import AppConfig
from src.utils.exceptions import LLMServiceError


class OpenAIService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.llm_config = config.llm_config

        try:
            self.client = OpenAI(api_key=self.llm_config["api_key"])
            self.model = self.llm_config["model"]
            self.default_temperature = self.llm_config["temperature"]
        except Exception as e:
            raise LLMServiceError(
                f"Failed to initialize OpenAI service: {str(e)}", original_error=e
            )

    def generate_text(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            # Merge options with defaults
            opts = {"temperature": self.default_temperature}
            if options:
                opts.update(options)

            # Create messages for the chat completion
            messages = [
                {"role": "system", "content": "You are a SQL expert"},
                {"role": "user", "content": prompt},
            ]

            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=opts["temperature"],
            )

            # Extract and clean up the response
            generated_text = response.choices[0].message.content
            # Remove markdown code blocks if present
            generated_text = (
                generated_text.replace("```sql", "").replace("```", "").strip()
            )

            return generated_text

        except Exception as e:
            raise LLMServiceError(f"Text generation failed: {str(e)}", original_error=e)

    def get_model_name(self) -> str:
        return self.model
