import os
from typing import Any, Dict

from openai import OpenAI

from src.infrastructure.exceptions import LLMServiceError
from src.infrastructure.config import EnvConfig


class OpenAILLM:
    """A facade for LLM operations, providing text generation capabilities."""

    def __init__(self):
        self.config = EnvConfig()
        self.api_key = self.config.openai_api_key
        self.model = self.config.openai_model
        self.temperature = self.config.openai_temperature

        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            raise LLMServiceError(
                f"Failed to initialize OpenAI service: {str(e)}", original_error=e
            )

    def generate_text(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """
        Generate text using the LLM based on the given prompt.

        Args:
            prompt: The prompt to send to the LLM
            options: Optional configuration overrides

        Returns:
            Generated text as a string
        """
        try:
            # Merge options with defaults
            opts = {"temperature": self.temperature}
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
        """Get the name of the current LLM model being used."""
        return self.model
