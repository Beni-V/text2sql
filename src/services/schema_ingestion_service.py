import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.infrastructure.config import EnvConfig
from src.services.database_schema_service import DatabaseSchemaService
from src.utils import Singleton


class SchemaIngestionService(metaclass=Singleton):
    """Service for ingesting database schema into a vector store."""

    def __init__(self):
        self._database_schema_service = DatabaseSchemaService()
        self._config = EnvConfig()
        self._embeddings = OpenAIEmbeddings(
            openai_api_key=self._config.openai_api_key, model="text-embedding-3-small"
        )
        self._vector_store = None
        self._vector_store_path = "data/vector_store"

    def ingest_schema(self, force_refresh: bool = False) -> None:
        """
        Ingest database schema into a vector store.

        Args:
            force_refresh: If True, force a refresh of the vector store even if it already exists.
        """
        # Check if the vector store already exists
        if not force_refresh and self._vector_store_exists():
            self._vector_store = self._load_vector_store()
            return

        # Get the schema
        schema = self._database_schema_service.retrieve(use_cache=True)

        # Create documents from the schema
        documents = self._create_schema_documents(schema)

        # Create the vector store
        self._create_vector_store(documents)

    def _vector_store_exists(self) -> bool:
        """Check if the vector store already exists."""
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self._vector_store_path), exist_ok=True)

        # Check if the index file exists
        return os.path.exists(f"{self._vector_store_path}/index.faiss")

    def _load_vector_store(self) -> FAISS:
        """Load the vector store from disk."""
        return FAISS.load_local(
            self._vector_store_path,
            self._embeddings,
            allow_dangerous_deserialization=True,
        )

    def _create_schema_documents(self, schema: dict) -> list[Document]:
        """
        Create documents from the schema.

        This creates separate documents for:
        1. Each table with its columns
        2. Each relationship between tables
        """
        documents = []

        # Create a document for each table with its columns
        for table_name, table_info in schema.items():
            table_schema_name = table_info.get("table_schema_name", "")
            columns = table_info.get("columns", {})

            column_info = []
            for col_name, col_info in columns.items():
                data_type = col_info.get("data_type", "unknown")
                is_nullable = (
                    "nullable"
                    if col_info.get("is_nullable") == "YES"
                    else "not nullable"
                )
                char_max_len = col_info.get("character_maximum_length", "")

                if char_max_len:
                    data_type = f"{data_type}({char_max_len})"

                column_info.append(f"{col_name}: {data_type}, {is_nullable}")

            content = (
                f"Table: {table_schema_name}.{table_name}\nColumns:\n"
                + "\n".join(column_info)
            )
            metadata = {
                "table_name": table_name,
                "table_schema_name": table_schema_name,
                "type": "table_columns",
            }

            documents.append(Document(page_content=content, metadata=metadata))

        # Create a document for each relationship
        for table_name, table_info in schema.items():
            relationships = table_info.get("relationships", {})

            # Foreign keys from this table to other tables
            for fk in relationships.get("foreign_keys", []):
                content = (
                    f"Foreign Key Relationship: {table_name}.{fk.get('column')} "
                    f"references {fk.get('references_table')}.{fk.get('references_column')}"
                )
                metadata = {
                    "source_table": table_name,
                    "source_column": fk.get("column"),
                    "target_table": fk.get("references_table"),
                    "target_column": fk.get("references_column"),
                    "constraint_name": fk.get("constraint_name"),
                    "type": "foreign_key",
                }

                documents.append(Document(page_content=content, metadata=metadata))

            # Tables referencing this table
            for ref in relationships.get("referenced_by", []):
                content = (
                    f"Reference Relationship: {ref.get('table')}.{ref.get('column')} "
                    f"references {table_name}.{ref.get('referenced_column')}"
                )
                metadata = {
                    "source_table": ref.get("table"),
                    "source_column": ref.get("column"),
                    "target_table": table_name,
                    "target_column": ref.get("referenced_column"),
                    "constraint_name": ref.get("constraint_name"),
                    "type": "referenced_by",
                }

                documents.append(Document(page_content=content, metadata=metadata))

        return documents

    def _create_vector_store(self, documents: list[Document]) -> None:
        """Create a vector store from the documents."""
        self._vector_store = FAISS.from_documents(documents, self._embeddings)

        # Save the vector store to disk
        self._vector_store.save_local(self._vector_store_path)

    @property
    def vector_store(self) -> FAISS:
        """Get the vector store."""
        if self._vector_store is None:
            self.ingest_schema()

        return self._vector_store
