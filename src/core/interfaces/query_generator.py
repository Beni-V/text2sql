"""
Query generation interfaces.
Following Interface Segregation and Dependency Inversion Principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class SQLQueryGenerator(ABC):
    """
    Abstract interface for SQL query generation.
    Provides a standard interface for different generation strategies.
    """

    @abstractmethod
    def generate_sql_query(
        self, natural_language_question: str, schema_info: Dict[str, Any]
    ) -> str:
        """
        Generate SQL query from natural language.

        Args:
            natural_language_question: User's question in natural language
            schema_info: Database schema information

        Returns:
            Generated SQL query string

        Raises:
            QueryGenerationError: If generation fails
        """
        pass
