"""
File Tool
File I/O operations for the pipeline
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import shutil
import json
from typing import Any, Dict, Optional
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class FileTool(BaseTool):
    """
    File I/O operations
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="file_manager",
            description="File operations (read, write, copy, delete)",
            category="system",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["read", "write", "copy", "delete", "exists"]},
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "Content to write"},
                    "destination": {"type": "string", "description": "Destination path (for copy)"},
                },
                "required": ["operation", "path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "any", "description": "Operation result"}
                }
            }
        )

    def execute(
        self,
        operation: str,
        path: str,
        content: Optional[str] = None,
        destination: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute file operation

        Args:
            operation: Operation type
            path: File path
            content: Content for write
            destination: Destination for copy

        Returns:
            Operation result
        """
        file_path = Path(path)

        if operation == "read":
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            content = file_path.read_text(encoding='utf-8')
            return {"content": content, "path": path}

        elif operation == "write":
            if content is None:
                raise ValueError("content required for write operation")

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            return {"path": path, "size": len(content)}

        elif operation == "copy":
            if not destination:
                raise ValueError("destination required for copy")

            shutil.copy(path, destination)
            return {"source": path, "destination": destination}

        elif operation == "delete":
            if file_path.exists():
                file_path.unlink()
                return {"deleted": True, "path": path}
            return {"deleted": False, "path": path}

        elif operation == "exists":
            return {"exists": file_path.exists(), "path": path}

        else:
            raise ValueError(f"Unknown operation: {operation}")
