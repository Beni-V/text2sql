import pandas as pd
import streamlit as st

from src.infrastructure.database import Database
from src.services.database_schema_service import DatabaseSchemaService
from src.services.llm_text_to_sql_service import LLMTextToSQLService


class SidebarSchemaDisplay:
    """Displays the database schema in the sidebar."""

    @staticmethod
    def render() -> None:
        with st.sidebar:
            SidebarSchemaDisplay._set_sidebar_header()
            try:
                st.json(DatabaseSchemaService().retrieve(), expanded=False)
            except Exception as e:
                st.error(f"Error loading schema: {str(e)}")

    @staticmethod
    def _set_sidebar_header() -> None:
        st.header("Database Schema")


class QueryInput:
    @staticmethod
    def render() -> None | str:
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
    """Processes and executes SQL queries based on user input."""

    def __init__(self):
        self._current_sql_query = None

    def process_query(self, question: str):
        with st.spinner("Processing..."):
            try:
                self._current_sql_query = LLMTextToSQLService().generate_sql(question)
                st.success("Generated SQL Query")
                st.code(self._current_sql_query, language="sql")
                self._execute_query_and_display_results()
            except Exception as e:
                st.error(f"Generation error: {str(e)}")

    def _execute_query_and_display_results(self):
        try:
            result = Database().execute_query(self._current_sql_query)
            st.success("Query Results")

            if result.get("rows"):
                df = pd.DataFrame(result.get("rows", []))
                st.dataframe(df)
        except Exception as e:
            st.error(f"Execution error: {str(e)}")


class UI:
    """Main UI class that orchestrates all UI components."""

    def __init__(self):
        self._sidebar_schema_display = SidebarSchemaDisplay()
        self._query_input = QueryInput()
        self._query_processor = SQLQueryProcessor()

    @staticmethod
    def _configure_page() -> None:
        UI._configure_tab_appearance()
        UI._configure_css()
        UI._set_page_title()

    @staticmethod
    def _set_page_title() -> None:
        st.title("🔍 SQL Query Generator")

    @staticmethod
    def _configure_css() -> None:
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

    @staticmethod
    def _configure_tab_appearance() -> None:
        st.set_page_config(
            page_title="SQL Query Generator",
            page_icon="🔍",
            layout="wide",
        )

    def render(self) -> None:
        UI._configure_page()

        self._sidebar_schema_display.render()
        question = self._query_input.render()

        if question:
            self._query_processor.process_query(question)
