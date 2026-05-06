"""
Logger Tool
Centralized logging for pipeline operations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class LoggerTool(BaseTool):
    """
    Logging operations
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("CineAI")

        if not self.logger.handlers:
            # Setup logging
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="logger",
            description="Log messages at different levels",
            category="system",
            input_schema={
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["debug", "info", "warning", "error", "critical"]},
                    "message": {"type": "string", "description": "Log message"},
                    "extra": {"type": "object", "description": "Extra context"},
                },
                "required": ["level", "message"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "logged": {"type": "boolean"}
                }
            }
        )

    def execute(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Log a message

        Args:
            level: Log level
            message: Message to log
            extra: Extra context

        Returns:
            Success status
        """
        log_method = getattr(self.logger, level.lower())

        if extra:
            message = f"{message} | {extra}"

        log_method(message)

        return {
            "logged": True,
            "level": level,
            "timestamp": datetime.utcnow().isoformat()
        }
