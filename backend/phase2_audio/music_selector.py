"""
BGM Selection Module
Selects background music from pre-downloaded library based on scene mood
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import random
import shutil
from typing import Optional, List

from shared.schema import MoodType
from shared.utils import generate_asset_filename
import config


def select_bgm_for_scene(
    mood: MoodType,
    run_id: str,
    scene_id: str
) -> Optional[str]:
    """
    Select a BGM track from the library based on scene mood

    Args:
        mood: Scene mood (calm, tense, upbeat, etc.)
        run_id: Pipeline run ID
        scene_id: Scene ID

    Returns:
        Path to selected BGM file, or None if no tracks available
    """
    # Get mood directory
    mood_str = mood.value if isinstance(mood, MoodType) else str(mood)
    mood_dir = config.MOOD_DIRS.get(mood_str.lower())

    if not mood_dir or not mood_dir.exists():
        print(f"⚠ No BGM directory for mood: {mood_str}")
        # Fallback to ambient
        mood_dir = config.MOOD_DIRS.get("ambient")
        if not mood_dir or not mood_dir.exists():
            return None

    # Get all music files in mood directory
    music_files = list(mood_dir.glob("*.mp3")) + list(mood_dir.glob("*.wav"))

    if not music_files:
        print(f"⚠ No music files found in {mood_dir}")
        return None

    # Randomly select a track
    selected_track = random.choice(music_files)

    # Copy to run assets directory
    bgm_file = generate_asset_filename(
        run_id,
        "bgm",
        f"{scene_id}_{mood_str}",
        selected_track.suffix[1:]  # Remove the dot from extension
    )

    # Copy file
    shutil.copy2(selected_track, bgm_file)

    print(f"✓ Selected BGM: {selected_track.name} for {scene_id} ({mood_str})")

    return str(bgm_file)


def get_available_moods() -> List[str]:
    """
    Get list of available mood categories

    Returns:
        List of mood names
    """
    return list(config.MOOD_DIRS.keys())


def check_bgm_library() -> dict:
    """
    Check BGM library status

    Returns:
        Dictionary with mood counts
    """
    library_status = {}

    for mood, mood_dir in config.MOOD_DIRS.items():
        if mood_dir.exists():
            music_files = list(mood_dir.glob("*.mp3")) + list(mood_dir.glob("*.wav"))
            library_status[mood] = len(music_files)
        else:
            library_status[mood] = 0

    return library_status


if __name__ == "__main__":
    """Run library check"""
    print("🎵 BGM Library Status:")
    print("=" * 50)

    status = check_bgm_library()
    total = 0

    for mood, count in status.items():
        icon = "✓" if count > 0 else "✗"
        print(f"{icon} {mood.capitalize():12} : {count} tracks")
        total += count

    print("=" * 50)
    print(f"Total tracks: {total}")

    if total == 0:
        print("\n⚠ No music files found!")
        print("\nTo add music files:")
        print("1. Create directories in backend/assets/music/")
        print("   - calm/")
        print("   - tense/")
        print("   - upbeat/")
        print("   - mysterious/")
        print("   - dramatic/")
        print("   - sad/")
        print("   - ambient/")
        print("\n2. Add royalty-free MP3/WAV files to each directory")
        print("\nRecommended sources:")
        print("- Free Music Archive (freemusicarchive.org)")
        print("- YouTube Audio Library")
        print("- Incompetech (incompetech.com)")
