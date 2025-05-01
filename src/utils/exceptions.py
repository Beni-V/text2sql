from typing import Optional, Any


class SQL2TextError(Exception):
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message)


class ConfigurationError(SQL2TextError):
    pass


class DatabaseError(SQL2TextError):
    pass


class ConnectionError(DatabaseError):
    pass


class QueryError(DatabaseError):
    pass


class SchemaError(DatabaseError):
    pass


class LLMServiceError(SQL2TextError):
    pass


class QueryGenerationError(SQL2TextError):
    pass


class ValidationError(SQL2TextError):
    pass
