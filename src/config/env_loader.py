"""
Environment variable loader with validation.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class EnvironmentLoader:
    """
    Handles loading and validating environment variables.
    Follows the Single Responsibility Principle by only managing environment configuration.
    """

    def __init__(self, env_file_path: Optional[str] = None):
        """
        Initialize the environment loader.

        Args:
            env_file_path: Optional path to .env file (defaults to .env in current directory)
        """
        self.env_file_path = env_file_path
        self._loaded = False

    def load(self) -> bool:
        """
        Load environment variables from .env file.

        Returns:
            bool: True if environment was loaded successfully
        """
        if self._loaded:
            return True

        result = load_dotenv(dotenv_path=self.env_file_path)
        self._loaded = result
        return result

    def get_variable(
        self, name: str, default: Any = None, required: bool = False
    ) -> Any:
        """
        Get an environment variable with validation.

        Args:
            name: Name of the environment variable
            default: Default value if variable is not found
            required: Whether the variable is required

        Returns:
            The environment variable value or default

        Raises:
            ValueError: If the variable is required but not found
        """
        if not self._loaded:
            self.load()

        value = os.environ.get(name, default)

        if required and value is None:
            raise ValueError(f"Required environment variable '{name}' is missing")

        return value

    def get_required_variables(self, *var_names) -> Dict[str, str]:
        """
        Get multiple required environment variables.

        Args:
            *var_names: Names of required environment variables

        Returns:
            Dict of variable names and values

        Raises:
            ValueError: If any required variable is missing
        """
        result = {}
        missing = []

        for name in var_names:
            try:
                result[name] = self.get_variable(name, required=True)
            except ValueError:
                missing.append(name)

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Please create a .env file with all required credentials.\n"
                "See .env.example for reference."
            )

        return result
