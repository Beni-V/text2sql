import json
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from src.infrastructure.config import EnvConfig
from src.services.database_schema_service import DatabaseSchemaService
from src.utils import Singleton


class SchemaEmbeddingService(metaclass=Singleton):
    """Service for ingesting database schema into a vector store."""

    def __init__(self):
        self._database_schema_service = DatabaseSchemaService()
        self._config = EnvConfig()
        self._embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", api_key=self._config.openai_api_key
        )
        self._vector_store = None
        self._embedded = False

    def embed_schema(self) -> None:
        """Embed database schema into a vector store."""
        # Check if the vector store already exists
        if not self._embedded:
            # Get the schema
            schema = self._database_schema_service.retrieve(use_cache=True)

            # Create documents from the schema
            documents = self._create_schema_documents(schema)

            # Create the vector store
            self._vector_store = FAISS.from_documents(documents, self._embeddings)

            self._embedded = True

    @staticmethod
    def _create_schema_documents(schema: dict) -> list[Document]:
        """Create documents from the schema for each table with its columns and relationships."""
        return [
            Document(
                json.dumps({"table_name": table_name, "table_data": schema[table_name]})
            )
            for table_name in schema
        ]

    @property
    def vector_store(self) -> FAISS:
        """Get the vector store."""
        if self._vector_store is None:
            self.embed_schema()

        return self._vector_store
