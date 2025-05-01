from typing import Dict, Any, Optional
from .env_loader import EnvironmentLoader


class AppConfig:
    def __init__(self, env_loader: Optional[EnvironmentLoader] = None):
        self.env_loader = env_loader or EnvironmentLoader()
        self._database_config = None
        self._llm_config = None

    @property
    def database_config(self) -> Dict[str, Any]:
        if self._database_config is None:
            self._database_config = self.env_loader.get_required_variables(
                "SQL_SERVER", "SQL_DATABASE", "SQL_USER", "SQL_PASSWORD"
            )
            self._database_config["trust_server_certificate"] = True
            self._database_config["driver"] = "ODBC Driver 18 for SQL Server"

        return self._database_config

    @property
    def llm_config(self) -> Dict[str, Any]:
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
    def streamlit_config(self) -> Dict[str, Any]:
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
        return (
            f"DRIVER={{{self.database_config['driver']}}};"
            f"SERVER={self.database_config['SQL_SERVER']};"
            f"DATABASE={self.database_config['SQL_DATABASE']};"
            f"UID={self.database_config['SQL_USER']};"
            f"PWD={self.database_config['SQL_PASSWORD']};"
            f"TrustServerCertificate={'yes' if self.database_config['trust_server_certificate'] else 'no'}"
        )
