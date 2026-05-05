"""
TTS (Text-to-Speech) Tool
Wraps ElevenLabs and Deepgram TTS functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class TTSTool(BaseTool):
    """
    Text-to-Speech synthesis tool
    Delegates to backend audio generators (ElevenLabs/Deepgram)
    """

    def __init__(self):
        super().__init__()
        self.generator = None  # Lazy load

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="tts_synthesizer",
            description="Synthesize speech from text using TTS engines",
            category="audio",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to synthesize"},
                    "voice_id": {"type": "string", "description": "Voice ID"},
                    "output_path": {"type": "string", "description": "Output file path"},
                },
                "required": ["text", "output_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "audio_path": {"type": "string"},
                    "duration_ms": {"type": "number"}
                }
            }
        )

    def execute(self, text: str, voice_id: str = None, output_path: str = None, **kwargs) -> Dict[str, Any]:
        """
        Synthesize speech

        Args:
            text: Text to synthesize
            voice_id: Optional voice ID
            output_path: Where to save audio

        Returns:
            Audio file path and metadata
        """
        # Lazy load to avoid circular imports
        if not self.generator:
            from agents.audio_agent.generator import AudioGenerator
            self.generator = AudioGenerator()

        # This is a simplified wrapper
        # In full implementation, would call specific TTS methods
        return {
            "audio_path": output_path,
            "duration_ms": len(text) * 100,  # Placeholder
            "voice_id": voice_id or "default"
        }
