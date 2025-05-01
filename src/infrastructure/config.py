import os
from typing import Any, Optional
from dotenv import load_dotenv


class EnvConfig:
    """
    Configuration class for environment variables.
    Provides methods to access environment variables with proper type conversion.
    """

    def __init__(self):
        # Load environment variables
        load_dotenv()

    def get(self, key: str, default: Any = None) -> Optional[str]:
        """
        Get an environment variable by key.

        Args:
            key: The name of the environment variable
            default: Default value if not found

        Returns:
            The value of the environment variable, or the default if not found
        """
        return os.getenv(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean environment variable by key.

        Args:
            key: The name of the environment variable
            default: Default value if not found

        Returns:
            Boolean value of the environment variable
        """
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "t", "yes", "y", "1")

    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an integer environment variable by key.

        Args:
            key: The name of the environment variable
            default: Default value if not found

        Returns:
            Integer value of the environment variable
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get a float environment variable by key.

        Args:
            key: The name of the environment variable
            default: Default value if not found

        Returns:
            Float value of the environment variable
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default

    @property
    def db_server(self) -> str:
        """Get the database server."""
        return self.get("DB_SERVER", "localhost")

    @property
    def db_name(self) -> str:
        """Get the database name."""
        return self.get("SQL_DATABASE", "")

    @property
    def db_user(self) -> str:
        """Get the database username."""
        return self.get("SQL_USER", "")

    @property
    def db_password(self) -> str:
        """Get the database password."""
        return self.get("SQL_PASSWORD", "")

    # OpenAI configuration
    @property
    def openai_api_key(self) -> str:
        """Get the OpenAI API key."""
        return self.get("OPENAI_API_KEY", "")

    @property
    def openai_model(self) -> str:
        """Get the OpenAI model."""
        return self.get("OPENAI_MODEL", "gpt-4.1-mini")

    @property
    def openai_temperature(self) -> float:
        """Get the OpenAI temperature."""
        return self.get_float("OPENAI_TEMPERATURE", 0)

    # Application configuration
    @property
    def enable_ui(self) -> bool:
        """Get whether UI is enabled."""
        return self.get_bool("ENABLE_UI", True)

    @property
    def port(self) -> int:
        """Get the server port."""
        return self.get_int("PORT", 5000)
