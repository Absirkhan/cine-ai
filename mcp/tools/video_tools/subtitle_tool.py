"""
Subtitle Tool
Generates and burns subtitles into videos
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import subprocess
from typing import Any, Dict, List
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class SubtitleTool(BaseTool):
    """
    Generate and add subtitles to videos
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="subtitle_generator",
            description="Generate and burn subtitles into video",
            category="video",
            input_schema={
                "type": "object",
                "properties": {
                    "video_path": {"type": "string", "description": "Input video path"},
                    "output_path": {"type": "string", "description": "Output video path"},
                    "subtitles": {
                        "type": "array",
                        "description": "List of subtitle entries",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "start_ms": {"type": "number"},
                                "end_ms": {"type": "number"}
                            }
                        }
                    },
                    "font_size": {"type": "number", "default": 24},
                    "font_color": {"type": "string", "default": "white"},
                },
                "required": ["video_path", "output_path", "subtitles"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "output_path": {"type": "string"},
                    "subtitle_count": {"type": "number"}
                }
            }
        )

    def execute(
        self,
        video_path: str,
        output_path: str,
        subtitles: List[Dict[str, Any]],
        font_size: int = 24,
        font_color: str = "white",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add subtitles to video

        Args:
            video_path: Input video
            output_path: Output video with subtitles
            subtitles: List of {text, start_ms, end_ms}
            font_size: Subtitle font size
            font_color: Subtitle color

        Returns:
            Output path and subtitle count
        """
        # Generate SRT file
        srt_path = output_path.replace('.mp4', '.srt')

        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                start_time = self._ms_to_srt_time(sub['start_ms'])
                end_time = self._ms_to_srt_time(sub['end_ms'])

                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{sub['text']}\n\n")

        # Burn subtitles using FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", f"subtitles={srt_path}:force_style='FontSize={font_size},PrimaryColour={self._color_to_ass(font_color)}'",
            "-c:a", "copy",
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            success = True
        except subprocess.CalledProcessError:
            success = False

        return {
            "output_path": output_path,
            "subtitle_count": len(subtitles),
            "success": success,
            "srt_path": srt_path
        }

    def _ms_to_srt_time(self, ms: int) -> str:
        """Convert milliseconds to SRT time format (HH:MM:SS,mmm)"""
        seconds = ms / 1000
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(ms % 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _color_to_ass(self, color: str) -> str:
        """Convert color name to ASS color code"""
        colors = {
            "white": "&HFFFFFF",
            "black": "&H000000",
            "yellow": "&H00FFFF",
            "red": "&H0000FF",
        }
        return colors.get(color.lower(), "&HFFFFFF")
