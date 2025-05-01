import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class EnvironmentLoader:

    def __init__(self):
        self.env_file_path = None
        self._loaded = False

    def load(self) -> bool:
        if self._loaded:
            return True

        result = load_dotenv(dotenv_path=self.env_file_path)
        self._loaded = result
        return result

    def get_variable(
        self, name: str, default: Any = None, required: bool = False
    ) -> Any:
        if not self._loaded:
            self.load()

        value = os.environ.get(name, default)

        if required and value is None:
            raise ValueError(f"Required environment variable '{name}' is missing")

        return value

    def get_required_variables(self, *var_names) -> Dict[str, str]:
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
