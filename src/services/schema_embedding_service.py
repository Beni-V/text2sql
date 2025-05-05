import os
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
        self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self._vector_store = None
        self._embedded = False

    @property
    def _vector_store_path(self) -> str:
        return "data/vector_store"

    def embed_schema(self) -> None:
        """Embed database schema into a vector store."""
        # Check if the vector store already exists
        if not self._embedded:
            self._vector_store = self._load_vector_store()
            self._embedded = True
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

    @staticmethod
    def _create_schema_documents(schema: dict) -> list[Document]:
        """Create documents from the schema for each table with its columns and relationships."""
        return [
            Document(
                json.dumps({"table_name": table_name, "table_data": schema[table_name]})
            )
            for table_name in schema
        ]

    def _create_vector_store(self, documents: list[Document]) -> None:
        """Create a vector store from the documents."""
        self._vector_store = FAISS.from_documents(documents, self._embeddings)

        # Save the vector store to disk
        self._vector_store.save_local(self._vector_store_path)

    @property
    def vector_store(self) -> FAISS:
        """Get the vector store."""
        if self._vector_store is None:
            self.embed_schema()

        return self._vector_store
