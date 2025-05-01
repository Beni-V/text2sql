from contextlib import contextmanager

import pyodbc

from src.config.app_config import AppConfig
from src.utils.exceptions import ConnectionError


class Connection:
    """Database connection class. Used to establish and manage database connection."""
    def __init__(self, config: AppConfig):
        self.config = config
        self.connection = None

    def connect(self) -> pyodbc.Connection:
        try:
            if self.connection is not None and not self.connection.closed:
                return self.connection

            connection_string = self.config.get_database_connection_string()
            self.connection = pyodbc.connect(connection_string)
            return self.connection
        except Exception as e:
            raise ConnectionError(
                f"Database connection failed: {str(e)}", original_error=e
            )

    def close(self) -> None:
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
                self.connection = None
        except Exception as e:
            raise ConnectionError(
                f"Error closing database connection: {str(e)}", original_error=e
            )


class ConnectionManager:
    """Provides a context manager for database connections. Manages the `Connection` class."""
    def __init__(self, connection):
        self.connection = connection

    @contextmanager
    def get_connection(self):
        try:
            conn = self.connection.connect()
            yield conn
        finally:
            self.connection.close()

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
