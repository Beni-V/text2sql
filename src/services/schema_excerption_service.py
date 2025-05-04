import json

from langchain_core.documents import Document

from src.services.schema_embedding_service import SchemaEmbeddingService
from src.utils import Singleton


class SchemaExcerptionService(metaclass=Singleton):
    """Service for retrieving relevant schema information based on a query."""

    def __init__(self):
        self._schema_ingestion_service = SchemaEmbeddingService()
        self._schema_ingestion_service.embed_schema()  # Ensure schema is ingested

    def retrieve_relevant_schema(self, query: str, top_k: int) -> dict:
        """Retrieve relevant schema information based on a query."""
        # Get the vector store
        vector_store = self._schema_ingestion_service.vector_store

        # Retrieve similar documents
        docs = vector_store.similarity_search(query, k=top_k)

        # Process the documents into a schema dictionary
        return self._process_retrieved_documents(docs)

    @staticmethod
    def _process_retrieved_documents(docs: list[Document]) -> dict:
        result = {}

        for doc in docs:
            page_content_as_dict = json.loads(doc.page_content)
            table_name = page_content_as_dict.get("table_name")
            metadata = page_content_as_dict.get("table_data")
            result[table_name] = metadata

        return result
