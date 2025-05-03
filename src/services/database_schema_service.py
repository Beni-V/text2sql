from src.infrastructure.config import EnvConfig
from src.infrastructure.database import Database
from src.infrastructure.exceptions import SchemaError
from src.utils import Singleton


class DatabaseSchemaService(metaclass=Singleton):
    """Service for retrieving and managing database schema information."""

    def __init__(self):
        self._database = Database()
        self._cached_schema = None
        self._config = EnvConfig()
        self._schema_retrieval_query_result = None

    def retrieve(self, use_cache: bool = True) -> dict:
        """Query the database for schema information. Cache it and return as a dictionary."""
        try:
            if use_cache and self._cached_schema is not None:
                return self._cached_schema

            # Get table and column information
            columns_query_result = self._database.execute_query(self._schema_retrieval_query)
            schema = self._construct_schema_as_dict(columns_query_result)
            
            # Get relationship information
            relationships_query_result = self._database.execute_query(self._relationships_retrieval_query)
            schema = self._add_relationships_to_schema(schema, relationships_query_result)
            
            self._cached_schema = schema
            return schema

        except Exception as e:
            raise SchemaError(f"Failed to retrieve schema information: {str(e)}")

    @staticmethod
    def _construct_schema_as_dict(query_result: dict) -> dict:
        """Construct the schema as a dictionary from the query result."""
        schema = {}

        for row in query_result["rows"]:
            table_name = row["TABLE_NAME"]
            table_schema_name = row["TABLE_SCHEMA"]
            column_name = row["COLUMN_NAME"]
            data_type = row["DATA_TYPE"]
            char_max_len = row["CHARACTER_MAXIMUM_LENGTH"]
            is_nullable = row["IS_NULLABLE"]
            column_default = row["COLUMN_DEFAULT"]

            if table_name not in schema:
                schema[table_name] = {
                    "table_schema_name": table_schema_name,
                    "columns": {},
                    "relationships": {
                        "foreign_keys": [],
                        "referenced_by": []
                    }
                }

            schema[table_name]["columns"][column_name] = {
                "data_type": data_type,
                "character_maximum_length": char_max_len,
                "is_nullable": is_nullable,
                "column_default": column_default,
            }

        return schema
    
    @staticmethod
    def _add_relationships_to_schema(schema: dict, relationships_result: dict) -> dict:
        """Add relationship information to the schema."""
        for row in relationships_result["rows"]:
            fk_table_name = row["FK_TABLE_NAME"]
            pk_table_name = row["PK_TABLE_NAME"]
            fk_column_name = row["FK_COLUMN_NAME"]
            pk_column_name = row["PK_COLUMN_NAME"]
            constraint_name = row["CONSTRAINT_NAME"]
            
            # Skip if tables are not in our schema (could happen with system tables)
            if fk_table_name not in schema or pk_table_name not in schema:
                continue
                
            # Add foreign key information to the table that contains the foreign key
            foreign_key_info = {
                "constraint_name": constraint_name,
                "column": fk_column_name,
                "references_table": pk_table_name,
                "references_column": pk_column_name
            }
            schema[fk_table_name]["relationships"]["foreign_keys"].append(foreign_key_info)
            
            # Add reverse relationship information to the referenced table
            referenced_by_info = {
                "constraint_name": constraint_name,
                "table": fk_table_name,
                "column": fk_column_name,
                "referenced_column": pk_column_name
            }
            schema[pk_table_name]["relationships"]["referenced_by"].append(referenced_by_info)
            
        return schema

    @property
    def _schema_retrieval_query(self) -> str:
        """SQL query to retrieve schema information."""
        return """
               SELECT TABLE_SCHEMA,
                      TABLE_NAME,
                      COLUMN_NAME,
                      DATA_TYPE,
                      CHARACTER_MAXIMUM_LENGTH,
                      IS_NULLABLE,
                      COLUMN_DEFAULT
               FROM INFORMATION_SCHEMA.COLUMNS
               ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION; \
               """
               
    @property
    def _relationships_retrieval_query(self) -> str:
        """SQL query to retrieve relationship information between tables."""
        return """
               SELECT 
                   fk.name AS CONSTRAINT_NAME,
                   OBJECT_SCHEMA_NAME(fk.parent_object_id) + '.' + OBJECT_NAME(fk.parent_object_id) AS FK_TABLE_NAME,
                   COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS FK_COLUMN_NAME,
                   OBJECT_SCHEMA_NAME(fk.referenced_object_id) + '.' + OBJECT_NAME(fk.referenced_object_id) AS PK_TABLE_NAME,
                   COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS PK_COLUMN_NAME
               FROM 
                   sys.foreign_keys AS fk
               INNER JOIN 
                   sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
               ORDER BY 
                   fk.name;
               """
