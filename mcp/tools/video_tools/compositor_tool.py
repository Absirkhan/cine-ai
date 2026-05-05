"""
Video Compositor Tool
Combines scene videos, audio, and BGM into final output
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class VideoCompositorTool(BaseTool):
    """
    Compose final video from scenes, audio, and BGM
    """

    def __init__(self):
        super().__init__()
        self.compositor = None  # Lazy load

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="video_compositor",
            description="Compose final video with audio synchronization",
            category="video",
            input_schema={
                "type": "object",
                "properties": {
                    "state": {"type": "object", "description": "Pipeline state with all assets"},
                },
                "required": ["state"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "video_path": {"type": "string", "description": "Path to final video"}
                }
            }
        )

    def execute(self, state: Any, **kwargs) -> Dict[str, Any]:
        """
        Compose final video

        Args:
            state: PipelineState with all scenes and assets

        Returns:
            Path to final composed video
        """
        # Lazy load
        if not self.compositor:
            from agents.video_agent.compositor import VideoCompositor
            self.compositor = VideoCompositor()

        video_path = self.compositor.compose_final_video(state)

        return {
            "video_path": video_path,
            "scenes_count": len(state.scenes)
        }
