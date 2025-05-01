"""
Prompt templates for LLM services.
Implements the PromptTemplate interface, following SRP.
"""

import json


class SQLGenerationPrompt:
    """
    Prompt template for SQL generation.
    """

    DEFAULT_TEMPLATE = """
                    You are an expert SQL assistant for Microsoft SQL Server.
                    Given a natural language question, generate an accurate SQL query.
                    
                    Database schema (JSON format):
                    {schema_json}
                    
                    Rules:
                    1. Return ONLY the raw SQL query
                    2. Don't include any explanations or markdown formatting
                    3. Use proper JOINs and WHERE clauses as needed
                    4. Include all relevant columns
                    
                    Question: "{question}"
                    
                    SQL:
                    """

    def __init__(self, template: str = None):
        """
        Initialize with optional custom template.

        Args:
            template: Custom prompt template (uses default if None)
        """
        self._template = template or self.DEFAULT_TEMPLATE

    def format(self, **kwargs) -> str:
        """
        Format the prompt template with variable values.

        Args:
            **kwargs: Variables to inject into template

        Returns:
            Formatted prompt string
        """
        # Schema can be a dict that needs JSON conversion
        if "schema_json" in kwargs and not isinstance(kwargs["schema_json"], str):
            kwargs["schema_json"] = json.dumps(kwargs["schema_json"], indent=2)

        return self._template.format(**kwargs)

    def get_raw_template(self) -> str:
        """
        Get the raw template string.

        Returns:
            Raw template string
        """
        return self._template
