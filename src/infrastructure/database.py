import json
import os
import time
import pyodbc

from typing import Dict, Any, Optional
from src.infrastructure.exceptions import QueryError
from src.infrastructure.config import EnvConfig
from src.utils import Singleton


class Database(metaclass=Singleton):
    """Singleton class for accessing the database."""
    def __init__(self):
        self._config = EnvConfig()

    @property
    def _connection_string(self) -> str:
        """Get the connection string for the database."""
        return (
            f"DRIVER={"ODBC Driver 18 for SQL Server" if os.uname().sysname == "Darwin" else "FreeTDS"};"
            f"SERVER={self._config.db_server};"
            f"DATABASE={self._config.db_name};"
            f"UID={self._config.db_user};"
            f"PWD={self._config.db_password};"
            f"TrustServerCertificate=yes;"
        )

    def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a SQL query and return the results."""
        try:
            start_time = time.time()

            with pyodbc.connect(self._connection_string) as conn:
                with conn.cursor() as cursor:
                    if parameters:
                        cursor.execute(query, parameters)
                    else:
                        cursor.execute(query)

                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        rows = []

                        for row in cursor.fetchall():
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
                        result = {
                            "rows": [],
                            "column_names": [],
                            "affected_rows": cursor.rowcount,
                            "execution_time": time.time() - start_time,
                        }

                    if not conn.autocommit:
                        conn.commit()

                    return result

        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}")
