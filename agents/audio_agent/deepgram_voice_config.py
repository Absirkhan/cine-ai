"""
Deepgram Aura-2 Voice Configuration
Maps character parameters to Deepgram voice models
"""

from typing import Dict

# Deepgram Aura-2 Voice Models
# Format: aura-2-{voice_name}-en
DEEPGRAM_VOICES = {
    # Storytelling / Narrative voices
    ("male", "warm"): "aura-2-orpheus-en",  # Professional, Clear, Confident, Trustworthy
    ("male", "calm"): "aura-2-arcas-en",    # Natural, Smooth, Clear, Comfortable
    ("male", "authoritative"): "aura-2-atlas-en",  # Enthusiastic, Confident, Approachable, Friendly

    # Character / Dramatic voices
    ("male", "energetic"): "aura-2-apollo-en",  # Confident, Comfortable, Casual
    ("male", "playful"): "aura-2-aries-en",     # Warm, Energetic, Caring

    # Female voices
    ("female", "calm"): "aura-2-helena-en",      # Caring, Natural, Positive, Friendly
    ("female", "energetic"): "aura-2-thalia-en", # Clear, Confident, Energetic, Enthusiastic
    ("female", "professional"): "aura-2-matilda-en",  # Would map to Alice in real Deepgram
    ("female", "playful"): "aura-2-jessica-en",       # Would map to Jessica-like voice
    ("female", "warm"): "aura-2-hera-en",        # Smooth, Warm, Professional

    # Neutral/fallback
    ("neutral", "calm"): "aura-2-orion-en",  # Approachable, Comfortable, Calm, Polite
}

# Genre-based voice selection for Deepgram
DEEPGRAM_GENRE_VOICES = {
    "sci-fi": "aura-2-atlas-en",       # Confident, authoritative
    "thriller": "aura-2-orpheus-en",   # Professional, trustworthy
    "documentary": "aura-2-orion-en",  # Calm, informative
    "drama": "aura-2-orpheus-en",      # Professional storytelling
    "comedy": "aura-2-aries-en",       # Warm, energetic
    "fantasy": "aura-2-atlas-en",      # Confident, engaging
    "action": "aura-2-apollo-en",      # Energetic, confident
    "cinematic": "aura-2-orpheus-en",  # Professional, clear
}

# Tone-based voice selection for Deepgram
DEEPGRAM_TONE_VOICES = {
    "dark": "aura-2-orpheus-en",     # Professional, trustworthy
    "suspense": "aura-2-atlas-en",   # Confident, engaging
    "playful": "aura-2-aries-en",    # Warm, energetic
    "warm": "aura-2-hera-en",        # Smooth, warm
    "professional": "aura-2-orpheus-en",  # Professional, clear
    "calm": "aura-2-arcas-en",       # Natural, smooth
    "energetic": "aura-2-apollo-en", # Confident, energetic
}

# Default fallback voice
DEEPGRAM_DEFAULT_VOICE = "aura-2-orpheus-en"  # Professional, versatile


def get_deepgram_voice(gender: str, tone: str) -> str:
    """
    Get Deepgram voice model based on character parameters

    Args:
        gender: Character gender ('male', 'female', 'neutral')
        tone: Character tone ('calm', 'energetic', etc.)

    Returns:
        Deepgram voice model string (e.g., 'aura-2-orpheus-en')
    """
    key = (gender.lower(), tone.lower())

    # Try exact match
    if key in DEEPGRAM_VOICES:
        return DEEPGRAM_VOICES[key]

    # Try gender-only match
    for (g, t), voice in DEEPGRAM_VOICES.items():
        if g == gender.lower():
            return voice

    # Fallback to default
    return DEEPGRAM_DEFAULT_VOICE


def get_deepgram_voice_by_genre(genre: str) -> str:
    """Get Deepgram voice based on genre"""
    return DEEPGRAM_GENRE_VOICES.get(genre.lower(), DEEPGRAM_DEFAULT_VOICE)


def get_deepgram_voice_by_tone(tone: str) -> str:
    """Get Deepgram voice based on tone"""
    return DEEPGRAM_TONE_VOICES.get(tone.lower(), DEEPGRAM_DEFAULT_VOICE)
