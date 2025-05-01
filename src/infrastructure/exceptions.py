class QueryError(Exception):
    """Exception raised for errors during query execution."""

    pass


class SchemaError(Exception):
    """Exception raised for errors related to database schema operations."""

    pass


class LLMServiceError(Exception):
    """Exception raised for errors related to LLM service operations."""

    pass


class QueryGenerationError(Exception):
    """Exception raised for errors during query generation."""

    pass
