from typing import List, Dict, Any
from langchain_core.documents import Document

from src.services.schema_ingestion_service import SchemaIngestionService
from src.utils import Singleton


class SchemaRetrievalService(metaclass=Singleton):
    """Service for retrieving relevant schema information based on a query."""

    def __init__(self):
        self._schema_ingestion_service = SchemaIngestionService()
        self._schema_ingestion_service.ingest_schema()  # Ensure schema is ingested
        
    def retrieve_relevant_schema(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        Retrieve relevant schema information based on a query.
        
        Args:
            query: The natural language query to find relevant schema for.
            top_k: The number of most relevant documents to retrieve.
            
        Returns:
            A dictionary containing the relevant schema information.
        """
        # Get the vector store
        vector_store = self._schema_ingestion_service.vector_store
        
        # Retrieve similar documents
        docs = vector_store.similarity_search(query, k=top_k)
        
        # Process the documents into a schema dictionary
        return self._process_retrieved_documents(docs)
    
    def _process_retrieved_documents(self, docs: List[Document]) -> Dict[str, Any]:
        """
        Process retrieved documents into a schema dictionary format.
        
        Args:
            docs: The retrieved documents from the vector store.
            
        Returns:
            A dictionary containing relevant schema information in the same format
            as the original DatabaseSchemaService.
        """
        # Initialize schema structure
        schema = {}
        
        # Process table_columns documents
        for doc in docs:
            doc_type = doc.metadata.get("type")
            
            if doc_type == "table_columns":
                table_name = doc.metadata.get("table_name")
                table_schema_name = doc.metadata.get("table_schema_name")
                
                # Initialize table if it doesn't exist
                if table_name not in schema:
                    schema[table_name] = {
                        "table_schema_name": table_schema_name,
                        "columns": {},
                        "relationships": {
                            "foreign_keys": [],
                            "referenced_by": []
                        }
                    }
                
                # Extract column information from content
                lines = doc.page_content.split("\n")
                for line in lines:
                    if ":" in line and not line.startswith("Table:"):
                        # Split by first colon to separate column name from details
                        col_parts = line.split(":", 1)
                        if len(col_parts) < 2:
                            continue
                            
                        col_name = col_parts[0].strip()
                        col_details = col_parts[1].strip()
                        
                        # Parse column details
                        data_type = "unknown"
                        is_nullable = "NO"
                        
                        if "," in col_details:
                            type_part, nullable_part = col_details.split(",", 1)
                            data_type = type_part.strip()
                            is_nullable = "YES" if "nullable" in nullable_part.lower() else "NO"
                        else:
                            data_type = col_details
                        
                        # Extract character length if present
                        char_max_len = None
                        if "(" in data_type and ")" in data_type:
                            data_type_parts = data_type.split("(")
                            base_type = data_type_parts[0]
                            char_max_len = data_type_parts[1].split(")")[0]
                            data_type = base_type
                        
                        # Add column to schema
                        schema[table_name]["columns"][col_name] = {
                            "data_type": data_type,
                            "character_maximum_length": char_max_len,
                            "is_nullable": is_nullable,
                            "column_default": None
                        }
        
        # Process relationship documents
        for doc in docs:
            doc_type = doc.metadata.get("type")
            
            if doc_type == "foreign_key":
                source_table = doc.metadata.get("source_table")
                source_column = doc.metadata.get("source_column")
                target_table = doc.metadata.get("target_table")
                target_column = doc.metadata.get("target_column")
                constraint_name = doc.metadata.get("constraint_name")
                
                # Skip if the source table is not in our schema
                if source_table not in schema:
                    continue
                    
                # Add foreign key information
                foreign_key_info = {
                    "constraint_name": constraint_name,
                    "column": source_column,
                    "references_table": target_table,
                    "references_column": target_column
                }
                
                schema[source_table]["relationships"]["foreign_keys"].append(foreign_key_info)
                
                # Add the target table if it's not already in the schema
                if target_table not in schema:
                    schema[target_table] = {
                        "table_schema_name": "",  # This will be filled in if we encounter a table_columns doc for this table
                        "columns": {},
                        "relationships": {
                            "foreign_keys": [],
                            "referenced_by": []
                        }
                    }
                
                # Add referenced_by information to the target table
                referenced_by_info = {
                    "constraint_name": constraint_name,
                    "table": source_table,
                    "column": source_column,
                    "referenced_column": target_column
                }
                
                schema[target_table]["relationships"]["referenced_by"].append(referenced_by_info)
                
            elif doc_type == "referenced_by":
                source_table = doc.metadata.get("source_table")
                source_column = doc.metadata.get("source_column")
                target_table = doc.metadata.get("target_table")
                target_column = doc.metadata.get("target_column")
                constraint_name = doc.metadata.get("constraint_name")
                
                # Skip if the target table is not in our schema
                if target_table not in schema:
                    continue
                    
                # Add referenced_by information
                referenced_by_info = {
                    "constraint_name": constraint_name,
                    "table": source_table,
                    "column": source_column,
                    "referenced_column": target_column
                }
                
                schema[target_table]["relationships"]["referenced_by"].append(referenced_by_info)
                
                # Add the source table if it's not already in the schema
                if source_table not in schema:
                    schema[source_table] = {
                        "table_schema_name": "",  # This will be filled in if we encounter a table_columns doc for this table
                        "columns": {},
                        "relationships": {
                            "foreign_keys": [],
                            "referenced_by": []
                        }
                    }
                
                # Add foreign key information to the source table
                foreign_key_info = {
                    "constraint_name": constraint_name,
                    "column": source_column,
                    "references_table": target_table,
                    "references_column": target_column
                }
                
                schema[source_table]["relationships"]["foreign_keys"].append(foreign_key_info)
                
        return schema
