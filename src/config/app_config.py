import os
from typing import Any

from .env_loader import EnvironmentLoader


class AppConfig:
    """Application configuration class. Used to store and access configuration values."""

    def __init__(self) -> None:
        self.env_loader = EnvironmentLoader()
        self._database_config: dict[str, Any] | None = None
        self._llm_config: dict[str, Any] | None = None

    @property
    def database_config(self) -> dict[str, Any]:
        if self._database_config is None:
            self._database_config = self.env_loader.get_required_variables(
                "SQL_SERVER", "SQL_DATABASE", "SQL_USER", "SQL_PASSWORD"
            )
            self._database_config["trust_server_certificate"] = True
            if os.uname().sysname == "Darwin":
                self._database_config["driver"] = "ODBC Driver 18 for SQL Server"
            else:
                self._database_config["driver"] = "FreeTDS"
        return self._database_config

    @property
    def llm_config(self) -> dict[str, Any]:
        if self._llm_config is None:
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
    def streamlit_config(self) -> dict[str, Any]:
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
        server = self.database_config["SQL_SERVER"]
        port = os.environ.get("SQL_PORT", "1433")
        database = self.database_config["SQL_DATABASE"]
        user = self.database_config["SQL_USER"]
        password = self.database_config["SQL_PASSWORD"]

        return (
            f"DRIVER={{{self.database_config['driver']}}};"
            f"SERVER={server};"
            f"PORT={port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TDS_VERSION=7.3;"
            f"TrustServerCertificate={'yes' if self.database_config['trust_server_certificate'] else 'no'}"
        )
