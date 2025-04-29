import os
import pyodbc
from contextlib import contextmanager

# Get database connection details from environment variables
SQL_SERVER = os.environ.get('SQL_SERVER', 'localhost')
SQL_DATABASE = os.environ.get('SQL_DATABASE', 'AdventureWorks')
SQL_USER = os.environ.get('SQL_USER', 'SA')
SQL_PASSWORD = os.environ.get('SQL_PASSWORD', 'YourStrong!Passw0rd')

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
                    return cursor.fetchall()
                return []
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {str(e)}")
