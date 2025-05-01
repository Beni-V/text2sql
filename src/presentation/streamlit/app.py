import streamlit as st

from src.config.app_config import AppConfig
from src.config.env_loader import EnvironmentLoader
from src.infrastructure.database.factory import DatabaseFactory
from src.infrastructure.llm.factory import LLMFactory
from src.presentation.streamlit.components import (
    SchemaDisplay,
    QueryInput,
    SQLQueryProcessor,
)


def configure_page(config: AppConfig):
    streamlit_config = config.streamlit_config

    # Set page configuration
    st.set_page_config(
        page_title=streamlit_config["page_title"],
        page_icon=streamlit_config["page_icon"],
        layout=streamlit_config["layout"],
    )

    # Add custom CSS
    st.markdown(
        f"<style>{streamlit_config['custom_css']}</style>", unsafe_allow_html=True
    )


def create_app():
    # Load configuration
    config = AppConfig(EnvironmentLoader())

    # Configure database components
    database_connection_manager = DatabaseFactory.create_connection_manager(
        DatabaseFactory.create_connection(config)
    )
    database_query_executor = DatabaseFactory.create_query_executor(
        database_connection_manager
    )

    # Create services
    db_service = DatabaseFactory.create_database_service(database_query_executor)
    schema_service = DatabaseFactory.create_schema_service(database_query_executor)

    # Configure LLM components
    llm_service = LLMFactory.create_llm_service(config)
    prompt_template = LLMFactory.create_sql_prompt_template()
    sql_generator = LLMFactory.create_sql_generator(llm_service, prompt_template)

    # Create UI components
    schema_display = SchemaDisplay(schema_service)
    query_input = QueryInput()
    query_processor = SQLQueryProcessor(sql_generator, db_service, schema_service)

    return {
        "config": config,
        "schema_display": schema_display,
        "query_input": query_input,
        "query_processor": query_processor,
    }


def main():
    # Create and configure the application
    app = create_app()

    # Configure the page
    configure_page(app["config"])

    # App header
    st.title("🔍 SQL Query Generator")

    # Render schema display
    app["schema_display"].render()

    # Render query input and process if submitted
    question = app["query_input"].render()
    if question:
        app["query_processor"].process_query(question)


if __name__ == "__main__":
    main()
