class BaseError(Exception):
    """Base class for all application exceptions."""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class QueryError(BaseError):
    """Exception raised for errors during query execution."""

    pass


class SchemaError(BaseError):
    """Exception raised for errors related to database schema operations."""

    pass


class LLMServiceError(BaseError):
    """Exception raised for errors related to LLM service operations."""

    pass


class QueryGenerationError(BaseError):
    """Exception raised for errors during query generation."""

    pass
