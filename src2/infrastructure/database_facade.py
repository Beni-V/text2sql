import json
import os
import time
from typing import Dict, Any, Optional

import pyodbc

from src2.infrastructure.exceptions import QueryError
from src2.infrastructure.config import EnvConfig


class DatabaseFacade:
    """A facade for database operations, focused on executing queries."""

    def __init__(self):
        # Get configuration from environment
        self.config = EnvConfig()

        self.connection_string = (
            f"DRIVER={"ODBC Driver 18 for SQL Server" if os.uname().sysname == "Darwin" else "FreeTDS"};"
            f"SERVER={self.config.db_server};"
            f"DATABASE={self.config.db_name};"
            f"UID={self.config.db_user};"
            f"PWD={self.config.db_password};"
            f"TrustServerCertificate=yes;"
        )

    def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a SQL query and return the results.

        Args:
            query: SQL query to execute
            parameters: Optional parameters for the query

        Returns:
            A dictionary containing the query results with rows, columns, etc.
        """
        try:
            start_time = time.time()

            with pyodbc.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
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

                        result = {
                            "rows": rows,
                            "column_names": columns,
                            "affected_rows": cursor.rowcount,
                            "execution_time": time.time() - start_time,
                        }
                    else:
                        # For non-query operations
                        result = {
                            "rows": [],
                            "column_names": [],
                            "affected_rows": cursor.rowcount,
                            "execution_time": time.time() - start_time,
                        }

                    # Commit changes if not in a transaction
                    if not conn.autocommit:
                        conn.commit()

                    return result

        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}", original_error=e)
