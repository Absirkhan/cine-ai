"""
Tool Registry for discovering and managing MCP tools
"""

from typing import Dict, List, Optional, Type
from .base_tool import BaseTool, ToolMetadata


class ToolRegistry:
    """
    Central registry for all MCP tools

    Tools register themselves here and can be discovered
    by name or category
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}

    def register(self, tool_class: Type[BaseTool], auto_instantiate: bool = True):
        """
        Register a tool class

        Args:
            tool_class: Tool class to register
            auto_instantiate: Whether to create an instance immediately
        """
        # Create instance to get metadata
        instance = tool_class()
        tool_name = instance.metadata.name

        self._tool_classes[tool_name] = tool_class

        if auto_instantiate:
            self._tools[tool_name] = instance

        print(f"✓ Registered tool: {tool_name} ({instance.metadata.category})")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool instance by name"""
        if tool_name in self._tools:
            return self._tools[tool_name]

        # Lazy instantiation
        if tool_name in self._tool_classes:
            instance = self._tool_classes[tool_name]()
            self._tools[tool_name] = instance
            return instance

        return None

    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a category"""
        return [
            tool for tool in self._tools.values()
            if tool.metadata.category == category
        ]

    def list_tools(self) -> List[ToolMetadata]:
        """List metadata for all registered tools"""
        return [tool.metadata for tool in self._tools.values()]

    def list_categories(self) -> List[str]:
        """List all tool categories"""
        categories = set(tool.metadata.category for tool in self._tools.values())
        return sorted(categories)

    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool is registered"""
        return tool_name in self._tool_classes or tool_name in self._tools

    def __repr__(self) -> str:
        return f"ToolRegistry(tools={len(self._tools)}, categories={len(self.list_categories())})"


# Global registry instance
_global_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return _global_registry


def register_tool(tool_class: Type[BaseTool]):
    """Decorator to register a tool"""
    _global_registry.register(tool_class)
    return tool_class
