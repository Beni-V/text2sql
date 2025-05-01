"""
Data models for database schema representation.
Following Single Responsibility Principle by focusing solely on schema structure.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class Column:
    """
    Represents a database column with its properties.
    """

    name: str
    data_type: str
    character_maximum_length: Optional[int] = None
    is_nullable: str = "YES"  # "YES" or "NO"
    column_default: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "data_type": self.data_type,
            "character_maximum_length": self.character_maximum_length,
            "is_nullable": self.is_nullable,
            "column_default": self.column_default,
        }


@dataclass
class Table:
    """
    Represents a database table with its schema and columns.
    """

    name: str
    schema: str
    columns: Dict[str, Column]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "schema": self.schema,
            "columns": {
                col_name: col.to_dict() for col_name, col in self.columns.items()
            },
        }


class DatabaseSchema:
    """
    Represents the complete database schema.
    """

    def __init__(self):
        self.tables: Dict[str, Table] = {}

    def add_table(self, table: Table) -> None:
        """Add a table to the schema"""
        self.tables[table.name] = table

    def get_table(self, table_name: str) -> Optional[Table]:
        """Get a table by name"""
        return self.tables.get(table_name)

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        return table_name in self.tables

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            table_name: table.to_dict() for table_name, table in self.tables.items()
        }
