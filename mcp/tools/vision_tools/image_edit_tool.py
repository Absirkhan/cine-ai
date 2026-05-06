"""
Image Edit Tool
Basic image editing operations (crop, resize, filter)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict, Optional, Tuple
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class ImageEditTool(BaseTool):
    """
    Basic image editing operations
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="image_editor",
            description="Edit images (crop, resize, rotate, apply filters)",
            category="vision",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["crop", "resize", "rotate", "filter"]},
                    "input_path": {"type": "string", "description": "Input image path"},
                    "output_path": {"type": "string", "description": "Output image path"},
                    "width": {"type": "number", "description": "Width (for resize)"},
                    "height": {"type": "number", "description": "Height (for resize)"},
                    "angle": {"type": "number", "description": "Rotation angle (for rotate)"},
                    "filter_type": {"type": "string", "description": "Filter type (blur, sharpen, etc.)"},
                },
                "required": ["operation", "input_path", "output_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "output_path": {"type": "string"},
                    "dimensions": {"type": "object"}
                }
            }
        )

    def execute(
        self,
        operation: str,
        input_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        angle: Optional[float] = None,
        filter_type: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Edit image

        Args:
            operation: Operation type
            input_path: Input image
            output_path: Output image
            width: Target width
            height: Target height
            angle: Rotation angle
            filter_type: Filter to apply

        Returns:
            Output path and dimensions
        """
        from PIL import Image, ImageFilter

        img = Image.open(input_path)

        if operation == "resize":
            if not width or not height:
                raise ValueError("width and height required for resize")
            img = img.resize((width, height), Image.Resampling.LANCZOS)

        elif operation == "crop":
            if not width or not height:
                raise ValueError("width and height required for crop")
            # Center crop
            left = (img.width - width) // 2
            top = (img.height - height) // 2
            right = left + width
            bottom = top + height
            img = img.crop((left, top, right, bottom))

        elif operation == "rotate":
            if angle is None:
                raise ValueError("angle required for rotate")
            img = img.rotate(angle, expand=True)

        elif operation == "filter":
            if filter_type == "blur":
                img = img.filter(ImageFilter.BLUR)
            elif filter_type == "sharpen":
                img = img.filter(ImageFilter.SHARPEN)
            elif filter_type == "edge":
                img = img.filter(ImageFilter.FIND_EDGES)

        # Save
        img.save(output_path)

        return {
            "output_path": output_path,
            "dimensions": {
                "width": img.width,
                "height": img.height
            },
            "operation": operation
        }
