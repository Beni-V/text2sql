"""
Database interfaces for the application.
Following Interface Segregation Principle by creating focused interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class SchemaProvider(ABC):
    """
    Abstract interface for database schema operations.
    Separate interface according to ISP.
    """

    @abstractmethod
    def get_schema_information(self) -> Dict[str, Any]:
        """
        Get database schema information.

        Returns:
            Dictionary with schema information

        Raises:
            SchemaError: If schema retrieval fails
        """
        pass

    @abstractmethod
    def get_detailed_schema_information(self) -> Dict[str, Any]:
        """
        Get detailed database schema information.

        Returns:
            Dictionary with detailed schema information

        Raises:
            SchemaError: If detailed schema retrieval fails
        """
        pass
