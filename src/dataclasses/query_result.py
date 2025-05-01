from dataclasses import dataclass
from typing import Any


@dataclass
class QueryResult:
    rows: list[dict[str, Any]]
    column_names: list[str]
    affected_rows: int = 0
    execution_time: float | None = None
