"""
Configuration management for CineAI backend
Loads environment variables and provides centralized config access
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Create directories if they don't exist
ASSETS_DIR.mkdir(exist_ok=True)
MUSIC_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# API Configuration
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
HUGGINGFACE_IMAGE_MODEL = os.getenv("HUGGINGFACE_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")

# Application Settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"  # Skip API calls for testing
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# CORS Settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Database
DATABASE_PATH = BASE_DIR / "cineai.db"

# Mood to Music Directory Mapping
MOOD_DIRS = {
    "calm": MUSIC_DIR / "calm",
    "tense": MUSIC_DIR / "tense",
    "upbeat": MUSIC_DIR / "upbeat",
    "mysterious": MUSIC_DIR / "mysterious",
    "dramatic": MUSIC_DIR / "dramatic",
    "sad": MUSIC_DIR / "sad",
    "ambient": MUSIC_DIR / "ambient",
}

# Create mood directories
for mood_dir in MOOD_DIRS.values():
    mood_dir.mkdir(exist_ok=True, parents=True)

# Video Generation Settings
DEFAULT_ASPECT_RATIO = "16:9"
ASPECT_RATIOS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
}
DEFAULT_FPS = 24

# Validation
def validate_config():
    """Validate required configuration"""
    errors = []

    if not GROQ_API_KEY:
        errors.append("GROQ_API_KEY is not set")
    if not ELEVENLABS_API_KEY:
        errors.append("ELEVENLABS_API_KEY is not set")
    if not HUGGINGFACE_API_KEY:
        errors.append("HUGGINGFACE_API_KEY is not set")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

def get_aspect_ratio_dimensions(aspect: str) -> tuple[int, int]:
    """Get width and height for given aspect ratio"""
    return ASPECT_RATIOS.get(aspect, ASPECT_RATIOS[DEFAULT_ASPECT_RATIO])

# Export all config
__all__ = [
    "BASE_DIR",
    "PROJECT_ROOT",
    "ASSETS_DIR",
    "MUSIC_DIR",
    "OUTPUTS_DIR",
    "GROQ_API_KEY",
    "ELEVENLABS_API_KEY",
    "DEEPGRAM_API_KEY",
    "HUGGINGFACE_API_KEY",
    "GROQ_MODEL",
    "HUGGINGFACE_IMAGE_MODEL",
    "DEBUG",
    "HOST",
    "PORT",
    "CORS_ORIGINS",
    "DATABASE_PATH",
    "MOOD_DIRS",
    "DEFAULT_ASPECT_RATIO",
    "ASPECT_RATIOS",
    "DEFAULT_FPS",
    "validate_config",
    "get_aspect_ratio_dimensions",
]
