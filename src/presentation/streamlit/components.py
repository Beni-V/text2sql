"""
Streamlit UI components.
Follows Single Responsibility Principle by separating UI components.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional

from src.services.database_service import DatabaseService
from src.services.schema_service import SchemaService
from src.services.sql_generation_service import LLMSQLGenerator
from src.utils.exceptions import QueryError, QueryGenerationError


class SchemaDisplay:
    """
    Component for displaying database schema.
    """

    def __init__(self, schema_service: SchemaService):
        """
        Initialize with schema service.

        Args:
            schema_service: Schema service for retrieving schema
        """
        self.schema_service = schema_service

    def render(self):
        """
        Render the schema display component.
        """
        with st.sidebar:
            st.header("Database Schema")
            if st.button("Refresh Schema"):
                st.cache_data.clear()
                self.schema_service.clear_cache()

            schema_info = self.schema_service.get_detailed_schema_information()
            st.json(schema_info, expanded=False)


class QueryInput:
    """
    Component for inputting natural language queries.
    """

    def render(self) -> Optional[str]:
        """
        Render the query input component.

        Returns:
            Query text if submitted, None otherwise
        """
        question = st.text_input(
            "Enter your question:",
            placeholder="e.g. Show me all employees in the Sales department",
        )

        if st.button("Generate and Execute SQL"):
            if question:
                return question
            else:
                st.warning("Please enter a question first")

        return None


class SQLQueryProcessor:
    """
    Component for processing SQL queries.
    """

    def __init__(
        self,
        sql_generator: LLMSQLGenerator,
        db_service: DatabaseService,
        schema_service: SchemaService,
    ):
        """
        Initialize with required services.

        Args:
            sql_generator: SQL generator service
            db_service: Database service
            schema_service: Schema service
        """
        self.sql_generator = sql_generator
        self.db_service = db_service
        self.schema_service = schema_service

    def process_query(self, question: str):
        """
        Process a natural language query.

        Args:
            question: Natural language question
        """
        with st.spinner("Processing..."):
            try:
                # Get schema information
                schema_info = self.schema_service.get_detailed_schema_information()

                # Generate SQL
                sql_query = self.sql_generator.generate_sql_query(question, schema_info)
                st.success("Generated SQL Query")
                st.code(sql_query, language="sql")

                # Execute SQL
                try:
                    results = self.db_service.execute_sql(sql_query)
                    st.success("Query Results")

                    if isinstance(results, list) and len(results) > 0:
                        df = pd.DataFrame(results)
                        st.dataframe(df)
                    else:
                        st.info("Query executed successfully but returned no results")
                except Exception as e:
                    st.error(f"Execution error: {str(e)}")
            except QueryGenerationError as e:
                st.error(f"Generation error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
