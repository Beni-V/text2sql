import json
import os
import pyodbc
from contextlib import contextmanager
# db_service.py
from dotenv import load_dotenv
try:
    load_dotenv()  # Loads from .env in same directory

    # Will fail FAST if any env var is missing
    SQL_SERVER = os.environ['SQL_SERVER']
    SQL_DATABASE = os.environ['SQL_DATABASE']
    SQL_USER = os.environ['SQL_USER']
    SQL_PASSWORD = os.environ['SQL_PASSWORD']
except KeyError as e:
    raise RuntimeError(
        f"Missing environment variable: {e}\n"
        "Please create a .env file with all required credentials.\n"
        "See .env.example for reference."
    )
@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={SQL_SERVER};'
            f'DATABASE={SQL_DATABASE};'
            f'UID={SQL_USER};'
            f'PWD={SQL_PASSWORD};'
            'TrustServerCertificate=yes'
        )
        yield conn
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {str(e)}")
    finally:
        if conn:
            conn.close()

def execute_sql(sql_query: str, parameters=None):
    """Execute SQL query with parameters"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if parameters:
                    cursor.execute(sql_query, parameters)
                else:
                    cursor.execute(sql_query)

                if cursor.description:  # If this is a SELECT query
                    columns = [desc[0] for desc in cursor.description]
                    return [
                        {column: json.dumps(value) if isinstance(value, (dict, list, tuple)) else value for column, value in zip(columns, row)}
                        for row in cursor.fetchall()
                    ]
                return []
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {str(e)}")
