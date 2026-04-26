"""
Shared JSON Schema for CineAI Pipeline
This is the central data contract used across all phases.
All phases must consume and produce data conforming to these models.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class MoodType(str, Enum):
    """Available mood types for scene BGM selection"""
    CALM = "calm"
    TENSE = "tense"
    UPBEAT = "upbeat"
    MYSTERIOUS = "mysterious"
    DRAMATIC = "dramatic"
    SAD = "sad"
    AMBIENT = "ambient"  # Default fallback


class VoiceParams(BaseModel):
    """Character voice parameters for TTS"""
    gender: Literal["male", "female", "neutral"] = "neutral"
    tone: str = Field(..., description="Voice tone (e.g., calm, energetic, whispered)")
    accent: Optional[str] = Field(None, description="Accent if specified (e.g., british, american)")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    pitch: float = Field(1.0, ge=0.5, le=2.0, description="Pitch adjustment")


class Character(BaseModel):
    """Character definition with voice and visual attributes"""
    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character role in story (e.g., protagonist, narrator)")
    voice_params: VoiceParams
    visual_description: str = Field(..., description="Physical appearance for image generation")


class Dialogue(BaseModel):
    """Single dialogue line within a scene"""
    character: str = Field(..., description="Character name speaking this line")
    text: str = Field(..., description="Dialogue text")
    duration_ms: Optional[int] = Field(None, description="Estimated TTS duration in milliseconds")
    audio_file: Optional[str] = Field(None, description="Path to generated audio file")


class Scene(BaseModel):
    """Individual scene with all metadata"""
    id: str = Field(..., description="Unique scene identifier (e.g., scene_001)")
    description: str = Field(..., description="Scene description for visual generation")
    dialogue: List[Dialogue] = Field(default_factory=list)
    visual_prompt: str = Field(..., description="Engineered prompt for image generation")
    mood: MoodType = Field(MoodType.AMBIENT, description="Scene mood for BGM selection")
    duration_ms: int = Field(..., description="Target scene duration in milliseconds")

    # Generated assets (populated by downstream phases)
    image_file: Optional[str] = Field(None, description="Path to generated scene image")
    video_file: Optional[str] = Field(None, description="Path to animated scene video")
    bgm_file: Optional[str] = Field(None, description="Path to background music file")


class Story(BaseModel):
    """High-level story metadata"""
    title: str = Field(..., description="Story title")
    summary: str = Field(..., description="Brief story summary")
    genre: str = Field(..., description="Story genre (e.g., Sci-Fi, Documentary)")
    tone: str = Field(..., description="Overall narrative tone (e.g., Cinematic, Playful)")
    total_duration_ms: int = Field(..., description="Target total video duration in milliseconds")


class AudioManifest(BaseModel):
    """Audio timing manifest for A/V synchronization"""
    scene_id: str
    dialogue_segments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of {character, audio_file, start_ms, end_ms}"
    )
    bgm_file: Optional[str] = None
    bgm_start_ms: int = 0
    bgm_end_ms: Optional[int] = None
    total_duration_ms: int


class PipelineState(BaseModel):
    """Complete pipeline state - passed between all phases"""
    run_id: str = Field(..., description="Unique run identifier")
    version: int = Field(1, description="State version for undo/redo")
    timestamp: str = Field(..., description="ISO timestamp of last update")

    # User input
    user_prompt: str = Field(..., description="Original user prompt")
    user_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="User parameters (genre, tone, duration, aspect ratio)"
    )

    # Phase outputs
    story: Optional[Story] = None
    scenes: List[Scene] = Field(default_factory=list)
    characters: List[Character] = Field(default_factory=list)
    audio_manifest: Optional[AudioManifest] = None

    # Final outputs
    final_video_path: Optional[str] = None

    # Phase status tracking
    phase_status: Dict[str, str] = Field(
        default_factory=lambda: {
            "script": "pending",
            "audio": "pending",
            "video": "pending",
            "web": "pending",
            "edit": "pending"
        }
    )

    # Error tracking
    errors: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class EditIntent(BaseModel):
    """Parsed user edit intention"""
    intent_type: Literal["change_voice", "change_mood", "change_bgm", "regenerate_scene",
                         "adjust_duration", "apply_filter", "change_script", "full_regenerate"]
    target: Literal["audio", "video_frame", "video", "script", "bgm"]
    scope: Optional[str] = Field(None, description="Target scope (e.g., character:Narrator, scene:scene_001)")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    original_query: str = Field(..., description="Original user edit command")


class VersionSnapshot(BaseModel):
    """State snapshot for undo/redo functionality"""
    version: int
    timestamp: str
    state: PipelineState
    change_description: str = Field(..., description="Human-readable description of what changed")
    asset_paths: List[str] = Field(default_factory=list, description="List of asset file paths at this version")
