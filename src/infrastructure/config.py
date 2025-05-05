import os
from typing import Any, Optional
from dotenv import load_dotenv

from src.utils import Singleton


class EnvConfig(metaclass=Singleton):
    """Singleton class for accessing environment variables."""

    def __init__(self):
        load_dotenv()

    def get(self, key: str, default: Any = None) -> Optional[str]:
        return os.getenv(key, default)

    def get_float(self, key: str, default: float = 0.0) -> float:
        return float(self.get(key, default))

    @property
    def db_server(self) -> str:
        return self.get("SQL_SERVER", self.get("DB_SERVER", "localhost"))

    @property
    def db_name(self) -> str:
        return self.get("SQL_DATABASE", "")

    @property
    def db_user(self) -> str:
        return self.get("SQL_USER", "")

    @property
    def db_password(self) -> str:
        return self.get("SQL_PASSWORD", "")

    @property
    def openai_api_key(self) -> str:
        return self.get("OPENAI_API_KEY", "")

    @property
    def openai_model(self) -> str:
        return self.get("OPENAI_MODEL", "gpt-4.1-mini")

    @property
    def openai_temperature(self) -> float:
        return self.get_float("OPENAI_TEMPERATURE", 0)

    @property
    def is_streamlit_prod(self) -> bool:
        """Check if running in Streamlit production environment."""
        return self.get("STREAMLIT_SERVER_ENVIRONMENT", "").lower() == "production"
