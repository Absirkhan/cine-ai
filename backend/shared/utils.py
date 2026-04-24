"""
Shared utility functions for CineAI pipeline
"""

import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
import config


def generate_run_id() -> str:
    """Generate a unique run ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"run_{timestamp}_{unique_id}"


def generate_scene_id(index: int) -> str:
    """Generate scene ID from index"""
    return f"scene_{index:03d}"


def generate_asset_filename(run_id: str, asset_type: str, identifier: str, extension: str) -> Path:
    """
    Generate consistent asset filename

    Args:
        run_id: Pipeline run ID
        asset_type: Type of asset (audio, image, video, etc.)
        identifier: Unique identifier (scene_id, character_name, etc.)
        extension: File extension without dot

    Returns:
        Full path to asset file
    """
    filename = f"{asset_type}_{identifier}.{extension}"
    asset_path = config.OUTPUTS_DIR / run_id / "assets" / filename
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    return asset_path


def hash_prompt(prompt: str) -> str:
    """Generate hash from prompt for caching"""
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]


def parse_duration(duration_str: str) -> int:
    """
    Parse duration string to milliseconds

    Args:
        duration_str: Duration in format "30s", "1m", "90s", "2 min", etc.

    Returns:
        Duration in milliseconds
    """
    duration_str = duration_str.lower().strip()

    # Remove spaces
    duration_str = duration_str.replace(" ", "")

    # Parse
    if "min" in duration_str:
        minutes = float(duration_str.replace("min", ""))
        return int(minutes * 60 * 1000)
    elif "s" in duration_str:
        seconds = float(duration_str.replace("s", ""))
        return int(seconds * 1000)
    else:
        # Assume seconds
        return int(float(duration_str) * 1000)


def format_duration_ms(milliseconds: int) -> str:
    """Format milliseconds to human-readable duration"""
    seconds = milliseconds / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = seconds / 60
        return f"{minutes:.1f}min"


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if not"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_mood_music_file(mood: str) -> Optional[Path]:
    """
    Get a random music file for the given mood

    Args:
        mood: Mood type (calm, tense, etc.)

    Returns:
        Path to music file, or None if no files found
    """
    import random

    mood_dir = config.MOOD_DIRS.get(mood.lower())

    if not mood_dir or not mood_dir.exists():
        # Fallback to ambient
        mood_dir = config.MOOD_DIRS.get("ambient")

    if not mood_dir:
        return None

    # Get all music files
    music_files = list(mood_dir.glob("*.mp3")) + list(mood_dir.glob("*.wav"))

    if not music_files:
        return None

    # Return random file
    return random.choice(music_files)


def validate_api_keys():
    """Validate that required API keys are set"""
    try:
        config.validate_config()
        return True
    except ValueError as e:
        return False


class ProgressTracker:
    """Simple progress tracking for phases"""

    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0

    def update(self, step: int, message: str = ""):
        """Update progress"""
        self.current_step = step
        progress = (step / self.total_steps) * 100
        return {
            "step": step,
            "total": self.total_steps,
            "progress": progress,
            "message": message
        }

    def increment(self, message: str = ""):
        """Increment progress by one step"""
        return self.update(self.current_step + 1, message)

    def complete(self, message: str = "Complete"):
        """Mark as complete"""
        return self.update(self.total_steps, message)
