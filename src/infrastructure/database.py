import json
import os
import time
import pyodbc
from src.infrastructure.config import EnvConfig
from src.infrastructure.exceptions import QueryError
from src.utils import Singleton


class Database(metaclass=Singleton):
    """Singleton class for accessing the database."""

    def __init__(self):
        self._config = EnvConfig()

    @property
    def _connection_string(self) -> str:
        """Get the connection string for the database."""
        if os.uname().sysname == "Darwin":
            driver = "ODBC Driver 18 for SQL Server"
        elif self._config.is_streamlit_prod:
            driver = "ODBC Driver 17 for SQL Server"
        else:
            driver = "FreeTDS"

        return (
            f"DRIVER={driver};"
            f"SERVER={self._config.db_server},1433;"
            f"DATABASE={self._config.db_name};"
            f"UID={self._config.db_user};"
            f"PWD={self._config.db_password};"
            f"TDS_Version=7.3;"
            f"TrustServerCertificate=yes;"
        )

    def execute_query(self, query: str) -> dict:
        """Execute a SQL query and return the results."""
        try:
            start_time = time.time()

            with pyodbc.connect(self._connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)

                    columns = [desc[0] for desc in cursor.description]
                    rows = []

                    query_result = cursor.fetchall()
                    result = Database._query_result_to_dict(
                        columns, cursor, query_result, rows, start_time
                    )

                    if not conn.autocommit:
                        conn.commit()

                    return result

        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}")

    @staticmethod
    def _query_result_to_dict(columns, cursor, query_result, rows, start_time):
        for row in query_result:
            row_dict = {}
            for i, column in enumerate(columns):
                value = row[i]
                # Convert complex types to JSON
                if isinstance(value, (dict, list, tuple)):
                    value = json.dumps(value)
                row_dict[column] = value
            rows.append(row_dict)

        return {
            "rows": rows,
            "column_names": columns,
            "affected_rows": cursor.rowcount,
            "execution_time": time.time() - start_time,
        }
