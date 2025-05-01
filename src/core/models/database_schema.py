from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Column:
    name: str
    data_type: str
    character_maximum_length: Optional[int] = None
    is_nullable: str = "YES"
    column_default: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_type": self.data_type,
            "character_maximum_length": self.character_maximum_length,
            "is_nullable": self.is_nullable,
            "column_default": self.column_default,
        }


@dataclass
class Table:

    name: str
    schema: str
    columns: Dict[str, Column]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "columns": {
                col_name: col.to_dict() for col_name, col in self.columns.items()
            },
        }


class DatabaseSchema:

    def __init__(self):
        self.tables: Dict[str, Table] = {}

    def add_table(self, table: Table) -> None:
        self.tables[table.name] = table

    def get_table(self, table_name: str) -> Optional[Table]:
        return self.tables.get(table_name)

    def table_exists(self, table_name: str) -> bool:
        return table_name in self.tables

    def to_dict(self) -> Dict[str, Any]:
        return {
            table_name: table.to_dict() for table_name, table in self.tables.items()
        }
