"""
State Management Tool
Handles pipeline state operations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict, Optional
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class StateManagementTool(BaseTool):
    """
    Manage pipeline state with versioning and snapshots
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="state_manager",
            description="Manage pipeline state with version control",
            category="system",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["snapshot", "revert", "get_latest", "get_history"]},
                    "run_id": {"type": "string"},
                    "version": {"type": "number"},
                    "description": {"type": "string"},
                },
                "required": ["operation", "run_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "object", "description": "Operation result"}
                }
            }
        )

    def execute(
        self,
        operation: str,
        run_id: str,
        version: Optional[int] = None,
        description: str = "",
        state: Any = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute state management operation

        Args:
            operation: Operation type (snapshot, revert, get_latest, get_history)
            run_id: Run identifier
            version: Version number (for revert)
            description: Change description (for snapshot)
            state: State object (for snapshot)

        Returns:
            Operation result
        """
        from state_manager.state_manager import StateManager

        manager = StateManager.load_or_create(run_id)

        if operation == "snapshot":
            version = manager.snapshot(state, description, [])
            return {"version": version, "run_id": run_id}

        elif operation == "revert":
            if version is None:
                raise ValueError("Version required for revert")
            state = manager.revert(version)
            return {"state": state, "version": version}

        elif operation == "get_latest":
            state = manager.get_latest_state()
            return {"state": state}

        elif operation == "get_history":
            history = manager.get_history()
            return {"history": history}

        else:
            raise ValueError(f"Unknown operation: {operation}")
