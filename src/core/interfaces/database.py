"""
Database interfaces for the application.
Following Interface Segregation Principle by creating focused interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class QueryExecutor(ABC):
    """
    Abstract interface for executing SQL queries.
    Separated from connection management according to SRP.
    """

    @abstractmethod
    def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query with optional parameters.

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            List of dictionaries with query results

        Raises:
            QueryError: If query execution fails
        """
        pass

    @abstractmethod
    def execute_non_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Execute a non-query SQL statement (INSERT, UPDATE, DELETE).

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            Number of affected rows

        Raises:
            QueryError: If execution fails
        """
        pass


class SchemaProvider(ABC):
    """
    Abstract interface for database schema operations.
    Separate interface according to ISP.
    """

    @abstractmethod
    def get_schema_information(self) -> Dict[str, Any]:
        """
        Get database schema information.

        Returns:
            Dictionary with schema information

        Raises:
            SchemaError: If schema retrieval fails
        """
        pass

    @abstractmethod
    def get_detailed_schema_information(self) -> Dict[str, Any]:
        """
        Get detailed database schema information.

        Returns:
            Dictionary with detailed schema information

        Raises:
            SchemaError: If detailed schema retrieval fails
        """
        pass
