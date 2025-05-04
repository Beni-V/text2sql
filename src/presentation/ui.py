import pandas as pd
import streamlit as st

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
    def render() -> tuple[None | str, bool | None]:
        question = st.text_input(
            "Enter your question:",
            placeholder="e.g. Show me all employees in the Sales department",
        )

        generation_mode = st.radio(
            "Generation Mode:",
            options=["RAG (Retrieval-Augmented Generation)", "Regular (Full Schema)"],
            index=0,
            help="RAG uses only relevant parts of the schema. Regular uses the entire schema.",
        )

        use_rag = (
            True if generation_mode == "RAG (Retrieval-Augmented Generation)" else False
        )

        if st.button("Generate and Execute SQL"):
            if question:
                return question, use_rag
            else:
                st.warning("Please enter a question first")

        return None, None


class SQLQueryProcessor:
    """Processes and executes SQL queries based on user input."""

    def __init__(self):
        self._llm_service = LLMTextToSQLService()

    def process_query(self, question: str, use_rag: bool) -> None:
        with st.spinner("Processing..."):
            try:
                # Set the generation mode
                self._llm_service.set_generation_mode(use_rag)

                # Display the selected mode
                mode_display = "RAG" if use_rag else "Regular"
                st.info(f"Using {mode_display} generation mode")

                # Use the generate_and_execute_sql method that handles refinement
                result = self._llm_service.generate_and_execute_sql(question)

                # Display the SQL query
                st.success("Generated SQL Query")
                st.code(result["query"], language="sql")

                # Display refinement information if the query was refined
                if result["refined"]:
                    with st.expander("Query was refined due to errors", expanded=True):
                        st.warning(
                            f"Original query had errors and was refined {result['refinement_attempts']} time(s)"
                        )
                        st.markdown("##### Original Query")
                        st.code(result["original_query"], language="sql")
                        st.markdown("##### Error Message")
                        st.code(result["error_message"])

                # Display the query results
                self._display_results(result["result"])
                
                # Display the last executed prompt
                with st.expander("View last executed prompt", expanded=False):
                    last_prompt = self._llm_service.get_last_executed_prompt()
                    if last_prompt:
                        st.markdown("##### Prompt sent to LLM")
                        st.text(last_prompt)
                    else:
                        st.info("No prompt has been executed yet")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    def _display_results(self, result):
        st.success("Query Results")

        if result.get("rows"):
            df = pd.DataFrame(result.get("rows", []))
            st.dataframe(df)

            # Display query statistics
            st.info(f"Execution time: {result.get('execution_time', 0):.3f} seconds")
        else:
            st.info("Query executed successfully, but returned no results")


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
        question, use_rag = self._query_input.render()

        if question:
            self._query_processor.process_query(question, use_rag)
