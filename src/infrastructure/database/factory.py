"""
Database factory for creating database-related objects.
Implements Factory Method pattern.
"""

from src.config.app_config import AppConfig
from src.infrastructure.database.connection import PyODBCConnection, ConnectionManager
from src.infrastructure.database.mssql_service import MSSQLService
from src.services.database_service import DatabaseService
from src.services.schema_service import SchemaService


class DatabaseFactory:
    """
    Factory for creating database-related objects.
    Implements Factory Method pattern.
    """

    @staticmethod
    def create_connection(config: AppConfig):
        """
        Create a database connection.

        Args:
            config: Application configuration

        Returns:
            DatabaseConnection implementation
        """
        return PyODBCConnection(config)

    @staticmethod
    def create_connection_manager(connection) -> ConnectionManager:
        """
        Create a connection manager.

        Args:
            connection: Database connection

        Returns:
            ConnectionManager
        """
        return ConnectionManager(connection)

    @staticmethod
    def create_mssql_service(connection_manager: ConnectionManager) -> MSSQLService:
        """
        Create a Microsoft SQL Server service.

        Args:
            connection_manager: Connection manager

        Returns:
            MSSQLService implementing QueryExecutor and SchemaProvider
        """
        return MSSQLService(connection_manager)

    @staticmethod
    def create_database_service(query_executor) -> DatabaseService:
        """
        Create a database service.

        Args:
            query_executor: Query executor implementation

        Returns:
            DatabaseService
        """
        return DatabaseService(query_executor)

    @staticmethod
    def create_schema_service(schema_provider) -> SchemaService:
        """
        Create a schema service.

        Args:
            schema_provider: Schema provider implementation

        Returns:
            SchemaService
        """
        return SchemaService(schema_provider)
