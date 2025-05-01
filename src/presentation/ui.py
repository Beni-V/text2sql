import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

from src.services.llm_text_to_sql_service import LLMTextToSQLService


class SchemaDisplay:
    """Component for displaying database schema in the sidebar."""

    def __init__(self, schema_service):
        self.schema_service = schema_service

    def render(self):
        """Render the schema display in the sidebar."""
        with st.sidebar:
            st.header("Database Schema")
            try:
                schema_info = self.schema_service.get_schema_information()
                st.json(schema_info, expanded=False)
            except Exception as e:
                st.error(f"Error loading schema: {str(e)}")


class QueryInput:
    """Component for handling user query input."""

    def render(self):
        """Render the query input section and return the query if submitted."""
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
    """Component for processing SQL queries and displaying results."""

    def __init__(self, text_to_sql_service):
        self.text_to_sql_service = text_to_sql_service

    def process_query(self, question: str):
        """Process a natural language query and display results."""
        with st.spinner("Processing..."):
            try:
                # Generate SQL
                sql_query = self.text_to_sql_service.generate_sql(question)
                st.success("Generated SQL Query")
                st.code(sql_query, language="sql")

                # Execute SQL
                self.execute_query(sql_query)
            except Exception as e:
                st.error(f"Generation error: {str(e)}")

    def execute_query(self, sql_query: str):
        """Execute a SQL query and display results."""
        try:
            # Execute query
            result = self.text_to_sql_service.database_facade.execute_query(sql_query)

            # Display results
            st.success("Query Results")

            if result.get("rows"):
                df = pd.DataFrame(result.get("rows", []))
                st.dataframe(df)

                # Add download button
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Results as CSV",
                    csv,
                    "query_results.csv",
                    "text/csv",
                    key="download-csv",
                )
            else:
                affected = result.get("affected_rows", 0)
                if affected >= 0:
                    st.info(f"Query executed successfully. {affected} rows affected.")
                else:
                    st.info("Query executed successfully but returned no results")
        except Exception as e:
            st.error(f"Execution error: {str(e)}")


class UI:
    """Main UI class that orchestrates all UI components."""

    def __init__(self):
        self.text_to_sql_service = LLMTextToSQLService()
        self.schema_display = SchemaDisplay(self.text_to_sql_service.schema_service)
        self.query_input = QueryInput()
        self.query_processor = SQLQueryProcessor(self.text_to_sql_service)

    def configure_page(self):
        """Configure the Streamlit page settings."""
        st.set_page_config(
            page_title="SQL Query Generator",
            page_icon="🔍",
            layout="wide",
        )

        # Add custom CSS to make the sidebar flush with the left edge
        st.markdown(
            """
            <style>
            div[data-testid="stSidebarNav"] {
                padding-top: 0rem;
            }
            section[data-testid="stSidebar"] {
                width: 100%;
                background-color: transparent;
                padding-left: 0;
                padding-right: 0;
                margin-left: 0;
            }
            section[data-testid="stSidebar"] > div {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def render(self):
        """Render the complete UI."""
        # Configure the page
        self.configure_page()

        # App header
        st.title("🔍 SQL Query Generator")

        # Render schema display in sidebar
        self.schema_display.render()

        # Render query input and process if submitted
        question = self.query_input.render()
        if question:
            self.query_processor.process_query(question)
