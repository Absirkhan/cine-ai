"""
ElevenLabs Voice Configuration - Free Tier Allowlist
CRITICAL: Only use these voice IDs to avoid 402 Payment Required errors
"""

from typing import Dict, Literal


# ALLOWLISTED VOICES FOR FREE TIER
# DO NOT use any voice IDs not in this list - they will cause 402 errors
ALLOWED_VOICES = {
    # Storytelling / Narrative
    "george": {
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "name": "George",
        "description": "Warm, Captivating Storyteller",
        "accent": "british",
        "age": "middle_aged",
        "gender": "male",
        "use_cases": ["narrative", "storytelling", "drama", "fantasy", "cinematic"]
    },
    "daniel": {
        "voice_id": "onwK4e9ZLuTAKqWW03F9",
        "name": "Daniel",
        "description": "Steady Broadcaster",
        "accent": "british",
        "age": "middle_aged",
        "gender": "male",
        "use_cases": ["documentary", "formal", "sci-fi", "thriller", "cinematic"]
    },

    # Character / Animation
    "callum": {
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",
        "name": "Callum",
        "description": "Husky Trickster",
        "accent": "american",
        "age": "middle_aged",
        "gender": "male",
        "use_cases": ["comedy", "playful", "fantasy", "suspense"]
    },
    "harry": {
        "voice_id": "SOYHLrjzK2X1ezoPC6cr",
        "name": "Harry",
        "description": "Fierce Warrior",
        "accent": "american",
        "age": "young",
        "gender": "male",
        "use_cases": ["action", "fantasy", "sci-fi", "thriller", "suspense"]
    },

    # Professional / Educational
    "alice": {
        "voice_id": "Xb7hH8MSUJpSbSDYk0k2",
        "name": "Alice",
        "description": "Clear, Engaging Educator",
        "accent": "british",
        "age": "middle_aged",
        "gender": "female",
        "use_cases": ["documentary", "educational", "professional"]
    },
    "matilda": {
        "voice_id": "XrExE9yKIg1WjnnlVkGX",
        "name": "Matilda",
        "description": "Knowledgeable, Professional",
        "accent": "american",
        "age": "middle_aged",
        "gender": "female",
        "use_cases": ["professional", "drama", "documentary"]
    },

    # Conversational
    "jessica": {
        "voice_id": "cgSgspJ2msm6clMCkdW9",
        "name": "Jessica",
        "description": "Playful, Bright, Warm",
        "accent": "american",
        "age": "young",
        "gender": "female",
        "use_cases": ["comedy", "playful", "warm", "conversational"]
    },
    "will": {
        "voice_id": "bIHbv24MWmeRgasZH58o",
        "name": "Will",
        "description": "Relaxed Optimist",
        "accent": "american",
        "age": "young",
        "gender": "male",
        "use_cases": ["comedy", "relaxed", "conversational"]
    }
}


# Extract just the voice IDs for quick validation
ALLOWED_VOICE_IDS = {v["voice_id"] for v in ALLOWED_VOICES.values()}


# Genre-based voice selection mappings
GENRE_VOICE_MAP = {
    "sci-fi": ["daniel", "harry"],
    "thriller": ["daniel", "harry"],
    "documentary": ["daniel", "alice", "matilda"],
    "drama": ["george", "matilda"],
    "comedy": ["jessica", "will", "callum"],
    "fantasy": ["george", "harry", "callum"],
    "action": ["harry", "daniel"],
    "cinematic": ["george", "daniel"]
}


# Tone-based voice selection mappings
TONE_VOICE_MAP = {
    "dark": ["daniel", "harry", "callum"],
    "suspense": ["daniel", "harry", "callum"],
    "playful": ["jessica", "callum", "will"],
    "warm": ["george", "jessica"],
    "professional": ["alice", "matilda", "daniel"],
    "calm": ["will", "george"],
    "energetic": ["harry", "jessica"]
}


# Character parameter mappings (gender, tone) -> voice key
CHARACTER_VOICE_MAP = {
    ("female", "calm"): "matilda",
    ("female", "energetic"): "jessica",
    ("female", "professional"): "alice",
    ("female", "playful"): "jessica",
    ("male", "calm"): "will",
    ("male", "authoritative"): "daniel",
    ("male", "energetic"): "harry",
    ("male", "playful"): "callum",
    ("male", "warm"): "george",
    ("neutral", "calm"): "george",
}


def validate_voice_id(voice_id: str) -> bool:
    """
    Validate that a voice ID is in the allowlist

    Args:
        voice_id: ElevenLabs voice ID to validate

    Returns:
        True if voice ID is allowed, False otherwise
    """
    return voice_id in ALLOWED_VOICE_IDS


def get_voice_id_by_key(voice_key: str) -> str:
    """
    Get voice ID by voice key (e.g., 'george', 'jessica')

    Args:
        voice_key: Lowercase voice key

    Returns:
        Voice ID string

    Raises:
        ValueError: If voice key is not in allowlist
    """
    if voice_key not in ALLOWED_VOICES:
        raise ValueError(
            f"Voice key '{voice_key}' not in allowlist. "
            f"Available: {', '.join(ALLOWED_VOICES.keys())}"
        )
    return ALLOWED_VOICES[voice_key]["voice_id"]


def select_voice_by_genre(genre: str, fallback: str = "george") -> str:
    """
    Select best voice ID based on genre

    Args:
        genre: Genre string (e.g., 'sci-fi', 'comedy')
        fallback: Fallback voice key if genre not found

    Returns:
        Voice ID string
    """
    genre_lower = genre.lower()

    # Try exact match
    if genre_lower in GENRE_VOICE_MAP:
        voice_key = GENRE_VOICE_MAP[genre_lower][0]  # Use first recommended
        return get_voice_id_by_key(voice_key)

    # Fallback
    return get_voice_id_by_key(fallback)


def select_voice_by_tone(tone: str, fallback: str = "george") -> str:
    """
    Select best voice ID based on tone

    Args:
        tone: Tone string (e.g., 'dark', 'playful')
        fallback: Fallback voice key if tone not found

    Returns:
        Voice ID string
    """
    tone_lower = tone.lower()

    # Try exact match
    if tone_lower in TONE_VOICE_MAP:
        voice_key = TONE_VOICE_MAP[tone_lower][0]  # Use first recommended
        return get_voice_id_by_key(voice_key)

    # Fallback
    return get_voice_id_by_key(fallback)


def select_voice_by_character(gender: str, tone: str, fallback: str = "george") -> str:
    """
    Select best voice ID based on character parameters

    Args:
        gender: Character gender ('male', 'female', 'neutral')
        tone: Character tone ('calm', 'energetic', etc.)
        fallback: Fallback voice key if no match found

    Returns:
        Voice ID string
    """
    key = (gender.lower(), tone.lower())

    # Try exact match
    if key in CHARACTER_VOICE_MAP:
        voice_key = CHARACTER_VOICE_MAP[key]
        return get_voice_id_by_key(voice_key)

    # Try gender-only match
    for (g, t), voice_key in CHARACTER_VOICE_MAP.items():
        if g == gender.lower():
            return get_voice_id_by_key(voice_key)

    # Fallback
    return get_voice_id_by_key(fallback)


def get_all_voice_ids() -> list[str]:
    """Get list of all allowed voice IDs"""
    return list(ALLOWED_VOICE_IDS)


def get_voice_info(voice_id: str) -> Dict | None:
    """
    Get full info for a voice ID

    Args:
        voice_id: ElevenLabs voice ID

    Returns:
        Voice info dict or None if not found
    """
    for voice_data in ALLOWED_VOICES.values():
        if voice_data["voice_id"] == voice_id:
            return voice_data
    return None
