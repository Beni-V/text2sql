"""
Schema Service.
Implements high-level schema operations, following Facade pattern.
"""

from typing import Dict, Any

from src.core.interfaces.database import SchemaProvider
from src.utils.exceptions import SchemaError


class SchemaService:
    """
    High-level service for schema operations.
    Implements Facade pattern to simplify schema retrievals.
    """

    def __init__(self, schema_provider: SchemaProvider):
        """
        Initialize with schema provider.

        Args:
            schema_provider: Implementation of SchemaProvider interface
        """
        self.schema_provider = schema_provider
        self._cached_schema = None
        self._cached_detailed_schema = None

    def get_schema_information(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get database schema information.

        Args:
            use_cache: Whether to use cached schema if available

        Returns:
            Dictionary with schema information

        Raises:
            SchemaError: If schema retrieval fails
        """
        try:
            if use_cache and self._cached_schema is not None:
                return self._cached_schema

            schema = self.schema_provider.get_schema_information()
            self._cached_schema = schema
            return schema
        except Exception as e:
            raise SchemaError(
                f"Failed to retrieve schema information: {str(e)}", original_error=e
            )

    def get_detailed_schema_information(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get detailed database schema information.

        Args:
            use_cache: Whether to use cached schema if available

        Returns:
            Dictionary with detailed schema information

        Raises:
            SchemaError: If schema retrieval fails
        """
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

    def clear_cache(self) -> None:
        """
        Clear the schema cache.
        """
        self._cached_schema = None
        self._cached_detailed_schema = None
