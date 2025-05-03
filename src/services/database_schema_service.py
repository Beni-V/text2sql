from src.infrastructure.config import EnvConfig
from src.infrastructure.database import Database
from src.infrastructure.exceptions import SchemaError
from src.utils import Singleton


class DatabaseSchemaService(metaclass=Singleton):
    """Service for retrieving and managing database schema information."""

    def __init__(self):
        self._database = Database()
        self._cached_schema = None
        self._config = EnvConfig()
        self._schema_retrieval_query_result = None

    def retrieve(self, use_cache: bool = True) -> dict:
        """Query the database for schema information. Cache it and return as a dictionary."""
        try:
            if use_cache and self._cached_schema is not None:
                return self._cached_schema

            query_result = self._database.execute_query(self._schema_retrieval_query)
            schema = self._construct_schema_as_dict(query_result)
            self._cached_schema = schema
            return schema

        except Exception as e:
            raise SchemaError(f"Failed to retrieve schema information: {str(e)}")

    @staticmethod
    def _construct_schema_as_dict(query_result: dict) -> dict:
        """Construct the schema as a dictionary from the query result."""
        schema = {}

        for row in query_result["rows"]:
            table_name = row["TABLE_NAME"]
            table_schema_name = row["TABLE_SCHEMA"]
            column_name = row["COLUMN_NAME"]
            data_type = row["DATA_TYPE"]
            char_max_len = row["CHARACTER_MAXIMUM_LENGTH"]
            is_nullable = row["IS_NULLABLE"]
            column_default = row["COLUMN_DEFAULT"]

            if table_name not in schema:
                schema[table_name] = {
                    "table_schema_name": table_schema_name,
                    "columns": {},
                }

            schema[table_name]["columns"][column_name] = {
                "data_type": data_type,
                "character_maximum_length": char_max_len,
                "is_nullable": is_nullable,
                "column_default": column_default,
            }

        return schema

    @property
    def _schema_retrieval_query(self) -> str:
        """SQL query to retrieve schema information."""
        return """
               SELECT TABLE_SCHEMA,
                      TABLE_NAME,
                      COLUMN_NAME,
                      DATA_TYPE,
                      CHARACTER_MAXIMUM_LENGTH,
                      IS_NULLABLE,
                      COLUMN_DEFAULT
               FROM INFORMATION_SCHEMA.COLUMNS
               ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION; \
               """
