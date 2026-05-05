"""
Base Tool Interface for MCP (Model Context Protocol)
All tools inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ToolMetadata(BaseModel):
    """Metadata describing a tool's capabilities"""
    name: str
    description: str
    category: str  # llm, audio, vision, video, system
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    version: str = "1.0.0"


class BaseTool(ABC):
    """
    Base class for all MCP tools

    Tools are self-contained modules that perform specific operations.
    Each tool should:
    - Define its metadata (name, description, schemas)
    - Implement the execute() method
    - Handle its own errors gracefully
    """

    def __init__(self):
        self._metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool-specific output
        """
        pass

    @property
    def metadata(self) -> ToolMetadata:
        """Get tool metadata"""
        return self._metadata

    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters against schema
        Override for custom validation
        """
        # Basic validation - can be enhanced
        required_params = self._metadata.input_schema.get("required", [])
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self._metadata.name})"
