"""
Database Service.
Implements high-level database operations, following Facade pattern.
"""

from typing import Any

from src.dataclasses.query_result import QueryResult
from src.infrastructure.database.mssql_service import QueryExecutor
from src.utils.exceptions import QueryError


class DatabaseService:

    def __init__(self, query_executor: QueryExecutor) -> None:
        self.query_executor = query_executor

    def execute_sql(
        self, sql_query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        try:
            result = self.query_executor.execute_query(sql_query, parameters)
            return result.rows
        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}", original_error=e)

    def execute_query(
        self, sql_query: str, parameters: dict[str, Any] | None = None
    ) -> QueryResult:
        return self.query_executor.execute_query(sql_query, parameters)
