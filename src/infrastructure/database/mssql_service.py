import json
import time
from typing import List, Dict, Any, Optional

from src.dataclasses.database_schema import Column, DatabaseSchema, Table
from src.dataclasses.query_result import QueryResult
from src.infrastructure.database.connection import ConnectionManager
from src.utils.exceptions import QueryError, SchemaError


class QueryExecutor:
    """A facade for executing SQL queries and retrieving results."""
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        try:
            start_time = time.time()

            with self.connection_manager.get_cursor() as cursor:
                # Execute the query with parameters if provided
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)

                # If this is a SELECT query (has description)
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = []

                    for row in cursor.fetchall():
                        # Convert row to dictionary
                        row_dict = {}
                        for i, column in enumerate(columns):
                            value = row[i]
                            # Convert complex types to JSON
                            if isinstance(value, (dict, list, tuple)):
                                value = json.dumps(value)
                            row_dict[column] = value
                        rows.append(row_dict)

                    result = QueryResult(
                        rows=rows,
                        column_names=columns,
                        affected_rows=cursor.rowcount,
                        execution_time=time.time() - start_time,
                    )
                else:
                    # For non-query operations
                    result = QueryResult(
                        rows=[],
                        column_names=[],
                        affected_rows=cursor.rowcount,
                        execution_time=time.time() - start_time,
                    )

                # Commit changes if not in a transaction
                if not cursor.connection.autocommit:
                    cursor.connection.commit()

                return result

        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}", original_error=e)

    def get_detailed_schema_information(self) -> Dict[str, Any]:
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

        try:
            schema = DatabaseSchema()

            with self.connection_manager.get_cursor() as cursor:
                cursor.execute(query)

                for (
                    schema_name,
                    table_name,
                    column_name,
                    data_type,
                    char_max_len,
                    is_nullable,
                    column_default,
                ) in cursor.fetchall():

                    if not schema.table_exists(table_name):
                        schema.add_table(
                            Table(name=table_name, schema=schema_name, columns={})
                        )

                    schema.get_table(table_name).columns[column_name] = Column(
                        name=column_name,
                        data_type=data_type,
                        character_maximum_length=char_max_len,
                        is_nullable=is_nullable,
                        column_default=column_default,
                    )

            return schema.to_dict()

        except Exception as e:
            raise SchemaError(
                f"Failed to retrieve detailed schema information: {str(e)}",
                original_error=e,
            )
