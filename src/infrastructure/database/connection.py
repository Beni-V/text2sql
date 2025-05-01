"""
Database connection management.
Implements connection pool and management following best practices.
"""

from contextlib import contextmanager

import pyodbc

from src.config.app_config import AppConfig
from src.core.interfaces.database import DatabaseConnection
from src.utils.exceptions import ConnectionError


class PyODBCConnection(DatabaseConnection):
    """
    PyODBC implementation of DatabaseConnection interface.
    Handles connection to Microsoft SQL Server via ODBC.
    """

    def __init__(self, config: AppConfig):
        """
        Initialize with configuration.

        Args:
            config: Application configuration with database settings
        """
        self.config = config
        self.connection = None

    def connect(self) -> pyodbc.Connection:
        """
        Establish connection to database.

        Returns:
            pyodbc.Connection: Active database connection

        Raises:
            ConnectionError: If connection fails
        """
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
        """
        Close the database connection.

        Raises:
            ConnectionError: If closing fails
        """
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
                self.connection = None
        except Exception as e:
            raise ConnectionError(
                f"Error closing database connection: {str(e)}", original_error=e
            )


class ConnectionManager:
    """
    Manages database connections using context manager pattern.
    """

    def __init__(self, connection: DatabaseConnection):
        """
        Initialize with a database connection.

        Args:
            connection: DatabaseConnection implementation
        """
        self.connection = connection

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            Active database connection

        Raises:
            ConnectionError: If connection fails
        """
        try:
            conn = self.connection.connect()
            yield conn
        finally:
            self.connection.close()

    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursors.

        Yields:
            Database cursor

        Raises:
            ConnectionError: If connection or cursor creation fails
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
