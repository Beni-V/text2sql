"""
Custom exceptions for the application.
Improves error handling and makes exceptions more specific and meaningful.
"""

from typing import Optional, Any


class SQL2TextError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message)


class ConfigurationError(SQL2TextError):
    """Raised when there's an error in configuration."""

    pass


class DatabaseError(SQL2TextError):
    """Base exception for database errors."""

    pass


class ConnectionError(DatabaseError):
    """Raised when a database connection fails."""

    pass


class QueryError(DatabaseError):
    """Raised when a query execution fails."""

    pass


class SchemaError(DatabaseError):
    """Raised when schema retrieval fails."""

    pass


class LLMServiceError(SQL2TextError):
    """Raised when LLM service encounters an error."""

    pass


class QueryGenerationError(SQL2TextError):
    """Raised when SQL query generation fails."""

    pass


class ValidationError(SQL2TextError):
    """Raised when validation fails."""

    pass
