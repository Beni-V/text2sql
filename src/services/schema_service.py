from typing import Any, Protocol

from src.infrastructure.database.query_executor import QueryExecutor
from src.utils.exceptions import SchemaError


class SchemaService:

    def __init__(self, schema_provider: QueryExecutor) -> None:
        self.schema_provider = schema_provider
        self._cached_schema: dict[str, Any] | None = None
        self._cached_detailed_schema: dict[str, Any] | None = None

    def get_detailed_schema_information(self, use_cache: bool = True) -> dict[str, Any]:
        try:
            if use_cache and self._cached_detailed_schema is not None:
                return self._cached_detailed_schema

            schema = self.schema_provider.get_detailed_schema_information()
            self._cached_detailed_schema = schema
            return schema
        except Exception as e:
            raise SchemaError(
                f"Failed to retrieve detailed schema information: {str(e)}",
                original_error=e,
            )
