"""
Audio Merger Tool
Combines voice, BGM, and other audio tracks
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict, List, Optional
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class AudioMergerTool(BaseTool):
    """
    Merge multiple audio tracks with volume control
    """

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="audio_merger",
            description="Merge voice, BGM, and effects into final audio track",
            category="audio",
            input_schema={
                "type": "object",
                "properties": {
                    "voice_path": {"type": "string", "description": "Path to voice/narration track"},
                    "bgm_path": {"type": "string", "description": "Path to background music"},
                    "output_path": {"type": "string", "description": "Output file path"},
                    "bgm_volume": {"type": "number", "description": "BGM volume (0.0-1.0)", "default": 0.3},
                    "voice_volume": {"type": "number", "description": "Voice volume (0.0-1.0)", "default": 1.0},
                },
                "required": ["voice_path", "output_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "merged_audio_path": {"type": "string", "description": "Path to merged audio"}
                }
            }
        )

    def execute(
        self,
        voice_path: str,
        output_path: str,
        bgm_path: Optional[str] = None,
        bgm_volume: float = 0.3,
        voice_volume: float = 1.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Merge audio tracks

        Args:
            voice_path: Voice track path
            output_path: Output path
            bgm_path: Optional BGM path
            bgm_volume: BGM volume level
            voice_volume: Voice volume level

        Returns:
            Path to merged audio
        """
        from pydub import AudioSegment
        import os

        # Load voice
        voice = AudioSegment.from_file(voice_path)

        # Adjust voice volume
        if voice_volume != 1.0:
            voice = voice + (20 * (voice_volume - 1))  # Convert to dB

        final_audio = voice

        # Mix with BGM if provided
        if bgm_path and os.path.exists(bgm_path):
            bgm = AudioSegment.from_file(bgm_path)

            # Adjust BGM volume
            bgm = bgm + (20 * (bgm_volume - 1))  # Convert to dB

            # Loop or trim BGM to match voice duration
            if len(bgm) < len(voice):
                # Loop BGM
                loops_needed = (len(voice) // len(bgm)) + 1
                bgm = bgm * loops_needed

            # Trim to voice length
            bgm = bgm[:len(voice)]

            # Overlay
            final_audio = voice.overlay(bgm)

        # Export
        final_audio.export(output_path, format="mp3")

        return {
            "merged_audio_path": output_path,
            "duration_ms": len(final_audio),
            "has_bgm": bgm_path is not None
        }
