"""
Data models for query results.
Following Single Responsibility Principle by focusing solely on result representation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class QueryResult:
    """
    Represents the result of a database query.
    """

    rows: List[Dict[str, Any]]
    column_names: List[str]
    affected_rows: int = 0
    execution_time: Optional[float] = None
