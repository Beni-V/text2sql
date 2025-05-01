from typing import Dict, Any

from src2.infrastructure.database_facade import DatabaseFacade
from src2.infrastructure.exceptions import SchemaError
from src2.infrastructure.config import EnvConfig


class DatabaseSchemaService:
    """Service for retrieving and managing database schema information."""

    def __init__(self):
        self.database_facade = DatabaseFacade()
        self._cached_schema = None
        self.config = EnvConfig()

    def get_schema_information(self, use_cache: bool = True) -> Dict[str, Any]:
        try:
            if use_cache and self._cached_schema is not None:
                return self._cached_schema

            # SQL query to get schema information
            query = """
            SELECT 
                TABLE_SCHEMA, 
                TABLE_NAME, 
                COLUMN_NAME, 
                DATA_TYPE, 
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE, 
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
            """

            # Execute the query using the DatabaseFacade
            result = self.database_facade.execute_query(query)

            # Process the results into a structured schema
            schema = {}
            for row in result["rows"]:
                table_name = row["TABLE_NAME"]
                table_schema_name = row["TABLE_SCHEMA"]
                column_name = row["COLUMN_NAME"]
                data_type = row["DATA_TYPE"]
                char_max_len = row["CHARACTER_MAXIMUM_LENGTH"]
                is_nullable = row["IS_NULLABLE"]
                column_default = row["COLUMN_DEFAULT"]

                # Initialize table if it doesn't exist yet
                if table_name not in schema:
                    schema[table_name] = {
                        "table_schema_name": table_schema_name,
                        "columns": {},
                    }

                # Add column information
                schema[table_name]["columns"][column_name] = {
                    "data_type": data_type,
                    "character_maximum_length": char_max_len,
                    "is_nullable": is_nullable,
                    "column_default": column_default,
                }

            # Cache the schema
            self._cached_schema = schema
            return schema

        except Exception as e:
            raise SchemaError(
                f"Failed to retrieve schema information: {str(e)}", original_error=e
            )