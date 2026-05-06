"""
BGM (Background Music) Tool
Selects and applies background music to scenes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict, Optional
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class BGMTool(BaseTool):
    """
    Background music selection and application
    """

    def __init__(self):
        super().__init__()
        self.music_selector = None  # Lazy load

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="bgm_selector",
            description="Select and apply background music based on mood",
            category="audio",
            input_schema={
                "type": "object",
                "properties": {
                    "mood": {"type": "string", "description": "Scene mood (suspenseful, action, romantic, etc.)"},
                    "duration_ms": {"type": "number", "description": "Required duration in milliseconds"},
                    "scene_id": {"type": "string", "description": "Scene identifier"},
                },
                "required": ["mood", "duration_ms"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "bgm_path": {"type": "string", "description": "Path to BGM file"},
                    "mood": {"type": "string"}
                }
            }
        )

    def execute(
        self,
        mood: str,
        duration_ms: int,
        scene_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Select background music

        Args:
            mood: Scene mood
            duration_ms: Required duration
            scene_id: Optional scene ID

        Returns:
            BGM file path and metadata
        """
        # Lazy load
        if not self.music_selector:
            from agents.audio_agent.music_selector import MusicSelector
            self.music_selector = MusicSelector()

        bgm_path = self.music_selector.select_music(mood, duration_ms)

        return {
            "bgm_path": bgm_path,
            "mood": mood,
            "duration_ms": duration_ms
        }
