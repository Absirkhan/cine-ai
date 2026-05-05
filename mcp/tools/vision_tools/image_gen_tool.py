"""
Image Generation Tool
Wraps FAL AI PixArt-Sigma for image generation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class ImageGeneratorTool(BaseTool):
    """
    Image generation using PixArt-Sigma via FAL AI
    """

    def __init__(self):
        super().__init__()
        self.image_gen = None  # Lazy load

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="image_generator",
            description="Generate images from text prompts using PixArt-Sigma",
            category="vision",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Image generation prompt"},
                    "run_id": {"type": "string"},
                    "scene_id": {"type": "string"},
                    "negative_prompt": {"type": "string"},
                },
                "required": ["prompt", "run_id", "scene_id"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to generated image"}
                }
            }
        )

    def execute(
        self,
        prompt: str,
        run_id: str,
        scene_id: str,
        negative_prompt: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image

        Args:
            prompt: Image prompt
            run_id: Pipeline run ID
            scene_id: Scene identifier
            negative_prompt: Optional negative prompt

        Returns:
            Path to generated image
        """
        # Lazy load
        if not self.image_gen:
            from agents.video_agent.image_generator import ImageGenerator
            self.image_gen = ImageGenerator()

        image_path = self.image_gen.generate_image(
            prompt=prompt,
            run_id=run_id,
            scene_id=scene_id,
            negative_prompt=negative_prompt
        )

        return {
            "image_path": image_path,
            "prompt": prompt
        }
