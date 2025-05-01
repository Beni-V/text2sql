from typing import Any, Dict
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from src.infrastructure.config import EnvConfig
from src.infrastructure.exceptions import LLMServiceError


class OpenAILLM:
    """Open AI LLM Service"""

    def __init__(self):
        self._config = EnvConfig()
        try:
            self.client = OpenAI(api_key=self._config.openai_api_key)
        except Exception as e:
            raise LLMServiceError(f"Failed to initialize OpenAI service: {str(e)}")

    def generate_text(self, prompt: str, options: Dict[str, Any] = None) -> str:
        """Generate text using the LLM based on the given prompt."""
        try:
            opts = {"temperature": self._config.openai_temperature}
            if options:
                opts.update(options)

            messages = [
                ChatCompletionSystemMessageParam(
                    role="system", content="You are a SQL expert"
                ),
                ChatCompletionUserMessageParam(role="user", content=prompt),
            ]

            response = self.client.chat.completions.create(
                model=self._config.openai_model,
                messages=messages,
                temperature=opts["temperature"],
            )

            return response.choices[0].message.content

        except Exception as e:
            raise LLMServiceError(f"Text generation failed: {str(e)}")
