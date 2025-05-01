"""
OpenAI service implementation.
Implements the LLMService interface.
"""

from typing import Dict, Any, Optional
import os

from openai import OpenAI
from src.core.interfaces.llm import LLMService
from src.config.app_config import AppConfig
from src.utils.exceptions import LLMServiceError


class OpenAIService(LLMService):
    """
    OpenAI implementation of the LLMService interface.
    Uses OpenAI's API for language model interactions.
    """

    def __init__(self, config: AppConfig):
        """
        Initialize with application configuration.

        Args:
            config: Application configuration with LLM settings
        """
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
        """
        Generate text using OpenAI's API.

        Args:
            prompt: The prompt text to send to the LLM
            options: Additional generation options

        Returns:
            Generated text response

        Raises:
            LLMServiceError: If generation fails
        """
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
        """
        Get the name of the currently used model.

        Returns:
            Model name
        """
        return self.model
