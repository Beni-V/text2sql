from src.config.app_config import AppConfig
from src.infrastructure.database.connection import Connection, ConnectionManager
from src.infrastructure.database.mssql_service import QueryExecutor
from src.services.database_service import DatabaseService
from src.services.schema_service import SchemaService


class DatabaseFactory:
    """A helper class for creating database related objects."""
    @staticmethod
    def create_connection(config: AppConfig):
        return Connection(config)

    @staticmethod
    def create_connection_manager(connection) -> ConnectionManager:
        return ConnectionManager(connection)

    @staticmethod
    def create_query_executor(connection_manager: ConnectionManager) -> QueryExecutor:
        return QueryExecutor(connection_manager)

    @staticmethod
    def create_database_service(query_executor) -> DatabaseService:
        return DatabaseService(query_executor)

    @staticmethod
    def create_schema_service(schema_provider) -> SchemaService:
        return SchemaService(schema_provider)
