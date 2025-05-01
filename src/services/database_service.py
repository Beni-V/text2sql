"""
Database Service.
Implements high-level database operations, following Facade pattern.
"""

from typing import List, Dict, Any, Optional
from src.dataclasses.query_result import QueryResult
from src.utils.exceptions import QueryError


class DatabaseService:

    def __init__(self, query_executor):
        self.query_executor = query_executor

    def execute_sql(
        self, sql_query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            result = self.query_executor.execute_query(sql_query, parameters)
            return result.rows
        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}", original_error=e)

    def execute_query(
        self, sql_query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        return self.query_executor.execute_query(sql_query, parameters)

    def execute_non_query(
        self, sql_query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> int:
        return self.query_executor.execute_non_query(sql_query, parameters)
