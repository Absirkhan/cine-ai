"""
FFmpeg Tool
Handles video encoding, format conversion, and basic editing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import subprocess
from typing import Any, Dict, Optional
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class FFmpegTool(BaseTool):
    """
    FFmpeg operations for video processing
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="ffmpeg_processor",
            description="Process videos using FFmpeg (encoding, conversion, trimming)",
            category="video",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["encode", "convert", "trim", "concat", "add_audio"]},
                    "input_path": {"type": "string", "description": "Input video path"},
                    "output_path": {"type": "string", "description": "Output video path"},
                    "audio_path": {"type": "string", "description": "Audio path (for add_audio)"},
                    "start_time": {"type": "number", "description": "Start time in seconds (for trim)"},
                    "end_time": {"type": "number", "description": "End time in seconds (for trim)"},
                    "codec": {"type": "string", "description": "Video codec", "default": "libx264"},
                    "preset": {"type": "string", "description": "Encoding preset", "default": "medium"},
                },
                "required": ["operation", "input_path", "output_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "output_path": {"type": "string", "description": "Path to processed video"},
                    "success": {"type": "boolean"}
                }
            }
        )

    def execute(
        self,
        operation: str,
        input_path: str,
        output_path: str,
        audio_path: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        codec: str = "libx264",
        preset: str = "medium",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute FFmpeg operation

        Args:
            operation: Operation type
            input_path: Input video
            output_path: Output video
            audio_path: Audio for add_audio operation
            start_time: Start time for trim
            end_time: End time for trim
            codec: Video codec
            preset: Encoding preset

        Returns:
            Output path and success status
        """
        cmd = ["ffmpeg", "-y"]  # -y to overwrite

        if operation == "add_audio":
            if not audio_path:
                raise ValueError("audio_path required for add_audio operation")

            cmd.extend([
                "-i", input_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                output_path
            ])

        elif operation == "trim":
            if start_time is None or end_time is None:
                raise ValueError("start_time and end_time required for trim")

            duration = end_time - start_time
            cmd.extend([
                "-i", input_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c", "copy",
                output_path
            ])

        elif operation == "encode":
            cmd.extend([
                "-i", input_path,
                "-c:v", codec,
                "-preset", preset,
                "-crf", "23",
                output_path
            ])

        elif operation == "convert":
            cmd.extend([
                "-i", input_path,
                "-c:v", codec,
                output_path
            ])

        else:
            raise ValueError(f"Unknown operation: {operation}")

        # Execute FFmpeg
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            success = True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            success = False

        return {
            "output_path": output_path,
            "success": success,
            "operation": operation
        }
