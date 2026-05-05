"""
Tool Executor - Dynamically executes tools from the registry
"""

from typing import Any, Dict, Optional
from .tool_registry import get_registry
from .base_tool import BaseTool


class ToolExecutor:
    """
    Executes tools dynamically by name

    This allows agents to call tools without direct imports,
    promoting loose coupling and modularity
    """

    def __init__(self):
        self.registry = get_registry()

    def execute(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool by name

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found or validation fails
            Exception: Any tool-specific errors
        """
        tool = self.registry.get_tool(tool_name)

        if not tool:
            available_tools = [t.name for t in self.registry.list_tools()]
            raise ValueError(
                f"Tool '{tool_name}' not found. "
                f"Available tools: {', '.join(available_tools)}"
            )

        # Validate inputs
        tool.validate_input(**kwargs)

        # Execute
        try:
            result = tool.execute(**kwargs)
            return result
        except Exception as e:
            print(f"Error executing tool '{tool_name}': {e}")
            raise

    def execute_batch(self, tool_calls: list[Dict[str, Any]]) -> list[Any]:
        """
        Execute multiple tools in sequence

        Args:
            tool_calls: List of {tool_name: str, params: dict}

        Returns:
            List of results in order
        """
        results = []
        for call in tool_calls:
            tool_name = call.get("tool_name")
            params = call.get("params", {})
            result = self.execute(tool_name, **params)
            results.append(result)
        return results

    def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific tool"""
        tool = self.registry.get_tool(tool_name)
        if tool:
            return tool.metadata.dict()
        return None

    def list_available_tools(self, category: Optional[str] = None) -> list[str]:
        """
        List all available tools

        Args:
            category: Optional category filter

        Returns:
            List of tool names
        """
        if category:
            tools = self.registry.get_tools_by_category(category)
            return [tool.metadata.name for tool in tools]
        else:
            return [tool.name for tool in self.registry.list_tools()]
