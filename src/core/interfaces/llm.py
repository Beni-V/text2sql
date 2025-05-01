"""
Language Model service interfaces.
Following Interface Segregation Principle by creating focused interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMService(ABC):
    """
    Abstract interface for language model services.
    Provides a standard interface for different LLM implementations.
    """

    @abstractmethod
    def generate_text(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text using the language model.

        Args:
            prompt: The prompt text to send to the LLM
            options: Additional generation options

        Returns:
            Generated text response

        Raises:
            LLMServiceError: If generation fails
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the currently used model.

        Returns:
            Model name
        """
        pass


class PromptTemplate(ABC):
    """
    Abstract interface for prompt templates.
    Separates prompt management from LLM service.
    """

    @abstractmethod
    def format(self, **kwargs) -> str:
        """
        Format the prompt template with variable values.

        Args:
            **kwargs: Variables to inject into template

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def get_raw_template(self) -> str:
        """
        Get the raw template string.

        Returns:
            Raw template string
        """
        pass
