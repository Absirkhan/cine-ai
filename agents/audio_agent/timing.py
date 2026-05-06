"""
Audio Timing Manifest Builder
Combines dialogue and BGM timing for A/V synchronization
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List
from pydub import AudioSegment

from shared.schema import PipelineState, Scene, AudioManifest


def build_timing_manifest(state: PipelineState) -> AudioManifest:
    """
    Build comprehensive timing manifest for entire video

    Args:
        state: PipelineState with generated audio files

    Returns:
        AudioManifest with all timing information
    """
    all_segments = []
    current_time_ms = 0

    for scene in state.scenes:
        # Add dialogue segments with offset
        for dialogue_item in scene.dialogue:
            if dialogue_item.audio_file:
                all_segments.append({
                    "scene_id": scene.id,
                    "character": dialogue_item.character,
                    "text": dialogue_item.text,
                    "audio_file": dialogue_item.audio_file,
                    "start_ms": current_time_ms,
                    "end_ms": current_time_ms + (dialogue_item.duration_ms or 0)
                })
                current_time_ms += (dialogue_item.duration_ms or 0)

        # Advance to next scene
        # If dialogue was shorter than scene duration, pad with silence
        if current_time_ms % scene.duration_ms != 0:
            current_time_ms = ((current_time_ms // scene.duration_ms) + 1) * scene.duration_ms

    manifest = AudioManifest(
        scene_id="full_video",
        dialogue_segments=all_segments,
        bgm_file=None,  # BGM is per-scene, mixed during video composition
        total_duration_ms=current_time_ms
    )

    state.audio_manifest = manifest
    return manifest


def get_audio_duration(audio_file_path: str) -> int:
    """
    Get actual duration of audio file

    Args:
        audio_file_path: Path to audio file

    Returns:
        Duration in milliseconds
    """
    try:
        audio = AudioSegment.from_file(audio_file_path)
        return len(audio)
    except Exception as e:
        print(f"Warning: Could not read audio file {audio_file_path}: {e}")
        return 0


def update_dialogue_durations(state: PipelineState) -> PipelineState:
    """
    Update dialogue duration estimates with actual audio file durations

    Args:
        state: PipelineState with audio files

    Returns:
        Updated state with accurate durations
    """
    for scene in state.scenes:
        for dialogue in scene.dialogue:
            if dialogue.audio_file:
                actual_duration = get_audio_duration(dialogue.audio_file)
                if actual_duration > 0:
                    dialogue.duration_ms = actual_duration

    return state
