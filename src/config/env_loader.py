import os
from typing import Any
from dotenv import load_dotenv


class EnvironmentLoader:
    """Loads environment variables from a .env file. Includes helper methods to retrieve."""

    def __init__(self) -> None:
        self._loaded: bool = False

    def load(self) -> None:
        if self._loaded:
            return
        load_dotenv()
        self._loaded = True

    def get_variable(
        self, name: str, default: Any = None, required: bool = False
    ) -> Any:
        if not self._loaded:
            self.load()

        value = os.environ.get(name, default)

        if required and value is None:
            raise ValueError(f"Required environment variable '{name}' is missing")

        return value

    def get_required_variables(self, *var_names: str) -> dict[str, str]:
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
