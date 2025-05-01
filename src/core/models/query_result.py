from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class QueryResult:
    rows: List[Dict[str, Any]]
    column_names: List[str]
    affected_rows: int = 0
    execution_time: Optional[float] = None
