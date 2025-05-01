"""
Application configuration management.
Centralizes all configuration in one place following Single Responsibility Principle.
"""

from typing import Dict, Any, Optional
from .env_loader import EnvironmentLoader


class AppConfig:
    """
    Manages application configuration.
    Acts as a configuration facade for the entire application.
    """

    def __init__(self, env_loader: Optional[EnvironmentLoader] = None):
        """
        Initialize application configuration.

        Args:
            env_loader: Environment loader instance (dependency injection)
        """
        self.env_loader = env_loader or EnvironmentLoader()
        self._database_config = None
        self._llm_config = None

    @property
    def database_config(self) -> Dict[str, Any]:
        """
        Get database configuration.
        Lazy-loaded for better performance.

        Returns:
            Dictionary with database configuration
        """
        if self._database_config is None:
            # Load required database configuration variables
            self._database_config = self.env_loader.get_required_variables(
                "SQL_SERVER", "SQL_DATABASE", "SQL_USER", "SQL_PASSWORD"
            )
            # Add additional database configuration settings
            self._database_config["trust_server_certificate"] = True
            self._database_config["driver"] = "ODBC Driver 18 for SQL Server"

        return self._database_config

    @property
    def llm_config(self) -> Dict[str, Any]:
        """
        Get LLM service configuration.
        Lazy-loaded for better performance.

        Returns:
            Dictionary with LLM service configuration
        """
        if self._llm_config is None:
            # Load required LLM configuration variables
            self._llm_config = {
                "api_key": self.env_loader.get_variable(
                    "OPENAI_API_KEY", required=True
                ),
                "model": self.env_loader.get_variable(
                    "OPENAI_MODEL", default="gpt-4.1-mini"
                ),
                "temperature": float(
                    self.env_loader.get_variable("OPENAI_TEMPERATURE", default="0")
                ),
            }

        return self._llm_config

    @property
    def streamlit_config(self) -> Dict[str, Any]:
        """
        Get Streamlit configuration.

        Returns:
            Dictionary with Streamlit configuration
        """
        return {
            "page_title": "SQL Query Generator",
            "page_icon": "🔍",
            "layout": "wide",
            "custom_css": """
                .sql-box {
                    background-color: #f5f5f5;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                    font-family: monospace;
                }
            """,
        }

    def get_database_connection_string(self) -> str:
        """
        Get database connection string.

        Returns:
            Formatted connection string
        """
        db = self.database_config
        return (
            f"DRIVER={{{db['driver']}}};"
            f"SERVER={db['SQL_SERVER']};"
            f"DATABASE={db['SQL_DATABASE']};"
            f"UID={db['SQL_USER']};"
            f"PWD={db['SQL_PASSWORD']};"
            f"TrustServerCertificate={'yes' if db['trust_server_certificate'] else 'no'}"
        )
