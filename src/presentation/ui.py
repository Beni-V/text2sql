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
    def render(self) -> tuple[None | str, bool | None]:
        # Use a form to handle Enter key press
        with st.form(key="query_form"):
            natural_language_query = st.text_input(
                "Enter your natural language query:",
                placeholder="e.g. Show me all employees in the Sales department",
            )

            generation_mode = self._display_and_get_generation_mode()
            use_rag = True if generation_mode == self._rag_mode_option else False

            # This button will be triggered when Enter is pressed or when clicked
            submit_button = st.form_submit_button("Generate and Execute SQL")

            if submit_button:
                if natural_language_query:
                    return natural_language_query, use_rag
                else:
                    st.warning("Please enter a query first")

        return None, None

    def _display_and_get_generation_mode(self) -> str:
        return st.radio(
            "Generation Mode:",
            options=[self._rag_mode_option, self._regular_mode_option],
            index=0,
            help="RAG uses only relevant parts of the schema. Regular uses the entire schema.",
        )

    @property
    def _rag_mode_option(self) -> str:
        return "RAG (Retrieval-Augmented Generation)"

    @property
    def _regular_mode_option(self) -> str:
        return "Regular (Full Schema)"


class SQLQueryProcessor:
    """Processes and executes SQL queries based on user input."""

    def __init__(self):
        self._llm_service = LLMTextToSQLService()

    def process_query(self, natural_language_query: str, use_rag: bool) -> None:
        with st.spinner("Processing..."):
            try:
                # Set the generation mode
                self._llm_service.set_generation_mode(use_rag)

                # Display the selected mode
                mode_display = "RAG" if use_rag else "Regular"
                st.info(f"Using {mode_display} generation mode")

                # Use the generate_and_execute_sql method that handles refinement
                result = self._llm_service.generate_and_execute_sql(natural_language_query)

                # Display the SQL query
                st.success("Generated SQL Query")
                st.code(result["query"], language="sql")

                # Display refinement information if the query was refined
                if result["refined"]:
                    self._display_original_query(result)

                self._display_results(result["result"])
                self._display_executed_prompt()

            except Exception as e:
                st.error(f"Error: {str(e)}")

    def _display_executed_prompt(self) -> None:
        with st.expander("View last executed prompt", expanded=False):
            last_prompt = self._llm_service.get_last_executed_prompt()
            if last_prompt:
                st.markdown("##### Prompt sent to LLM")
                st.text(last_prompt)
            else:
                st.info("No prompt has been executed yet")

    @staticmethod
    def _display_original_query(result: dict) -> None:
        with st.expander("Query was refined due to errors", expanded=False):
            st.warning(
                f"Original query had errors and was refined {result['refinement_attempts']} time(s)"
            )
            st.markdown("##### Original Query")
            st.code(result["original_query"], language="sql")
            st.markdown("##### Error Message")
            st.code(result["error_message"])

    @staticmethod
    def _display_results(result: dict) -> None:
        st.success("Query Results")

        if result.get("rows"):
            df = pd.DataFrame(result.get("rows", []))
            st.dataframe(df)
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
        natural_language_query, use_rag = self._query_input.render()

        if natural_language_query:
            self._query_processor.process_query(natural_language_query, use_rag)
