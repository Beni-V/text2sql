import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional

from src.services.database_service import DatabaseService
from src.services.schema_service import SchemaService
from src.services.sql_generation_service import LLMSQLGenerator
from src.utils.exceptions import QueryError, QueryGenerationError


class SchemaDisplay:

    def __init__(self, schema_service: SchemaService):
        self.schema_service = schema_service

    def render(self):
        with st.sidebar:
            st.header("Database Schema")
            if st.button("Refresh Schema"):
                st.cache_data.clear()
                self.schema_service.clear_cache()

            schema_info = self.schema_service.get_detailed_schema_information()
            st.json(schema_info, expanded=False)


class QueryInput:

    def render(self) -> Optional[str]:
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

    def __init__(
        self,
        sql_generator: LLMSQLGenerator,
        db_service: DatabaseService,
        schema_service: SchemaService,
    ):
        self.sql_generator = sql_generator
        self.db_service = db_service
        self.schema_service = schema_service

    def process_query(self, question: str):
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
