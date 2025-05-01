"""
Database Service.
Implements high-level database operations, following Facade pattern.
"""

from typing import List, Dict, Any, Optional

from src.core.interfaces.database import QueryExecutor
from src.core.models.query_result import QueryResult
from src.utils.exceptions import QueryError


class DatabaseService:
    """
    High-level service for database operations.
    Implements Facade pattern to simplify database operations.
    """

    def __init__(self, query_executor: QueryExecutor):
        """
        Initialize with query executor.

        Args:
            query_executor: Implementation of QueryExecutor interface
        """
        self.query_executor = query_executor

    def execute_sql(
        self, sql_query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as a list of dictionaries.
        Maintains backward compatibility with original interface.

        Args:
            sql_query: SQL query string
            parameters: Optional query parameters

        Returns:
            List of dictionaries with query results

        Raises:
            QueryError: If query execution fails
        """
        try:
            result = self.query_executor.execute_query(sql_query, parameters)
            return result.rows
        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}", original_error=e)

    def execute_query(
        self, sql_query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """
        Execute a SQL query and return results as a QueryResult object.
        Enhanced version providing more information.

        Args:
            sql_query: SQL query string
            parameters: Optional query parameters

        Returns:
            QueryResult with the query results

        Raises:
            QueryError: If query execution fails
        """
        return self.query_executor.execute_query(sql_query, parameters)

    def execute_non_query(
        self, sql_query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Execute a non-query SQL statement (INSERT, UPDATE, DELETE).

        Args:
            sql_query: SQL query string
            parameters: Optional query parameters

        Returns:
            Number of affected rows

        Raises:
            QueryError: If execution fails
        """
        return self.query_executor.execute_non_query(sql_query, parameters)
