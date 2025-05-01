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
        """
        Get detailed schema information from the database.

        Args:
            use_cache: Whether to use cached schema if available

        Returns:
            Dictionary containing the database schema
        """
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
            tables = {}
            for row in result["rows"]:
                schema_name = row["TABLE_SCHEMA"]
                table_name = row["TABLE_NAME"]
                column_name = row["COLUMN_NAME"]
                data_type = row["DATA_TYPE"]
                char_max_len = row["CHARACTER_MAXIMUM_LENGTH"]
                is_nullable = row["IS_NULLABLE"]
                column_default = row["COLUMN_DEFAULT"]

                # Initialize table if it doesn't exist yet
                table_key = f"{schema_name}.{table_name}"
                if table_key not in tables:
                    tables[table_key] = {
                        "name": table_name,
                        "schema": schema_name,
                        "columns": {},
                    }

                # Add column information
                tables[table_key]["columns"][column_name] = {
                    "name": column_name,
                    "data_type": data_type,
                    "character_maximum_length": char_max_len,
                    "is_nullable": is_nullable,
                    "column_default": column_default,
                }

            # Create the final schema structure
            schema = {"tables": list(tables.values())}

            # Cache the schema
            self._cached_schema = schema
            return schema

        except Exception as e:
            raise SchemaError(
                f"Failed to retrieve schema information: {str(e)}", original_error=e
            )
