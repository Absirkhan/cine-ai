"""
Phase 2: TTS Audio Generation with ElevenLabs
Handles voice synthesis and timing manifest creation
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Any
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
import wave
import time
import httpx
import requests

from shared.schema import PipelineState, Scene, Character, Dialogue, AudioManifest
from shared.utils import generate_asset_filename
import config
from .deepgram_voice_config import get_deepgram_voice


class AudioGenerator:
    """Handles TTS generation using ElevenLabs API with Deepgram fallback"""

    def __init__(self):
        # Create custom httpx client with longer timeout and retry settings
        httpx_client = httpx.Client(
            timeout=httpx.Timeout(120.0, connect=60.0),  # 120s total, 60s connect
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            transport=httpx.HTTPTransport(retries=3)
        )

        self.client = ElevenLabs(
            api_key=config.ELEVENLABS_API_KEY,
            httpx_client=httpx_client
        )

        # Voice ID mappings (ElevenLabs pre-made voices)
        # You can replace these with custom voice IDs
        self.voice_mappings = {
            ("female", "calm"): "EXAVITQu4vr4xnSDxMaL",  # Bella
            ("female", "energetic"): "21m00Tcm4TlvDq8ikWAM",  # Rachel
            ("male", "calm"): "pNInz6obpgDQGcFmaJgB",  # Adam
            ("male", "authoritative"): "VR6AewLTigWG4xSOukaG",  # Arnold
            ("male", "energetic"): "5Q0t7uMcjvnagumLfvZi",  # Clyde
            ("neutral", "whispered"): "TX3LPaxmHKxFdv7VOQHJ",  # Elli
        }

        # Flag to force Deepgram fallback (for IP blocking or free tier exhaustion)
        self.use_deepgram_fallback = True  # Always use Deepgram due to ElevenLabs IP blocking

        print(f"✓ AudioGenerator initialized (Using Deepgram TTS due to ElevenLabs limitations)")

    def _get_voice_id(self, character: Character) -> str:
        """
        Map character voice parameters to ElevenLabs voice ID
        CRITICAL: Only returns voice IDs from the free tier allowlist

        Args:
            character: Character with voice parameters

        Returns:
            ElevenLabs voice ID (guaranteed to be in allowlist)

        Raises:
            ValueError: If validation fails (should never happen with proper config)
        """
        gender = character.voice_params.gender
        tone = character.voice_params.tone

        # Use allowlist-based selection
        voice_id = select_voice_by_character(gender, tone, fallback="george")

        # Double-check validation (safety check)
        if not validate_voice_id(voice_id):
            raise ValueError(
                f"CRITICAL: Voice ID '{voice_id}' not in allowlist! "
                f"This should never happen. Check voice_config.py"
            )

        # Log voice selection
        voice_info = get_voice_info(voice_id)
        if voice_info:
            print(f"   Selected voice: {voice_info['name']} ({voice_info['description']})")

        return voice_id

        # Ultimate fallback
        return "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)

    def _synthesize_with_deepgram(
        self,
        text: str,
        character: Character,
        run_id: str,
        scene_id: str,
        dialogue_idx: int
    ) -> tuple[str, int]:
        """
        Synthesize dialogue using Deepgram Aura TTS

        Args:
            text: Text to synthesize
            character: Character speaking
            run_id: Pipeline run ID
            scene_id: Scene ID
            dialogue_idx: Index of dialogue within scene

        Returns:
            Tuple of (audio_file_path, duration_ms)
        """
        # Get Deepgram voice model based on character
        deepgram_model = get_deepgram_voice(
            character.voice_params.gender,
            character.voice_params.tone
        )

        print(f"🎤 Using Deepgram voice: {deepgram_model}")

        # Deepgram API endpoint
        url = f"https://api.deepgram.com/v1/speak?model={deepgram_model}"

        headers = {
            "Authorization": f"Token {config.DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": text
        }

        # Make request to Deepgram
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            audio_bytes = response.content
            print(f"✓ Deepgram synthesis successful!")

        except requests.exceptions.RequestException as e:
            print(f"✗ Deepgram API error: {str(e)}")
            raise Exception(f"Deepgram TTS failed: {str(e)}")

        # Save to file
        audio_file = generate_asset_filename(
            run_id,
            "audio",
            f"{scene_id}_dialogue_{dialogue_idx:02d}",
            "mp3"
        )

        with open(audio_file, "wb") as f:
            f.write(audio_bytes)

        # Estimate duration (approximate)
        # Rough estimate: ~150 words per minute average speech
        word_count = len(text.split())
        duration_ms = int((word_count / 150) * 60 * 1000 / character.voice_params.speed)

        return str(audio_file), duration_ms

    def _synthesize_dialogue(
        self,
        dialogue: Dialogue,
        character: Character,
        run_id: str,
        scene_id: str,
        dialogue_idx: int
    ) -> tuple[str, int]:
        """
        Synthesize a single dialogue line
        Uses Deepgram as fallback if ElevenLabs fails or is unavailable

        Args:
            dialogue: Dialogue object
            character: Character speaking
            run_id: Pipeline run ID
            scene_id: Scene ID
            dialogue_idx: Index of dialogue within scene

        Returns:
            Tuple of (audio_file_path, duration_ms)
        """
        # Check if we should use Deepgram fallback immediately
        if self.use_deepgram_fallback:
            print(f"⚡ Using Deepgram TTS (ElevenLabs bypassed)")
            return self._synthesize_with_deepgram(
                dialogue.text,
                character,
                run_id,
                scene_id,
                dialogue_idx
            )

        # Otherwise, try ElevenLabs first with fallback to Deepgram
        voice_id = self._get_voice_id(character)

        # CRITICAL VALIDATION: Ensure voice_id is in allowlist before API call
        if not validate_voice_id(voice_id):
            raise ValueError(
                f"BLOCKED: Voice ID '{voice_id}' is not in the free tier allowlist. "
                f"Using this voice will cause a 402 Payment Required error. "
                f"Character: {character.name}, Gender: {character.voice_params.gender}, "
                f"Tone: {character.voice_params.tone}"
            )

        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                print(f"🎤 Synthesizing dialogue with ElevenLabs (attempt {attempt + 1}/{max_retries})...")

                # Generate audio using the correct ElevenLabs API method
                audio_generator = self.client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=dialogue.text,
                    model_id="eleven_multilingual_v2",
                    voice_settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.75,
                        style=0.0,
                        use_speaker_boost=True
                    )
                )

                # Convert generator to bytes
                audio_bytes = b"".join(audio_generator)
                print(f"✓ ElevenLabs synthesis successful!")
                break  # Success, exit retry loop

            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.TimeoutException) as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠ Timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"✗ ElevenLabs failed after {max_retries} attempts, falling back to Deepgram...")
                    return self._synthesize_with_deepgram(
                        dialogue.text,
                        character,
                        run_id,
                        scene_id,
                        dialogue_idx
                    )

            except Exception as e:
                print(f"✗ ElevenLabs error: {str(e)}, falling back to Deepgram...")
                return self._synthesize_with_deepgram(
                    dialogue.text,
                    character,
                    run_id,
                    scene_id,
                    dialogue_idx
                )

        # Save to file (if ElevenLabs succeeded)
        audio_file = generate_asset_filename(
            run_id,
            "audio",
            f"{scene_id}_dialogue_{dialogue_idx:02d}",
            "mp3"
        )

        with open(audio_file, "wb") as f:
            f.write(audio_bytes)

        # Estimate duration (approximate - ElevenLabs doesn't provide exact duration)
        # Rough estimate: ~150 words per minute average speech
        word_count = len(dialogue.text.split())
        duration_ms = int((word_count / 150) * 60 * 1000 / character.voice_params.speed)

        return str(audio_file), duration_ms

    def generate_scene_audio(
        self,
        scene: Scene,
        characters: List[Character],
        run_id: str
    ) -> Dict[str, Any]:
        """
        Generate audio for all dialogue in a scene

        Args:
            scene: Scene object with dialogue
            characters: List of all characters
            run_id: Pipeline run ID

        Returns:
            Dictionary with dialogue segments and timing
        """
        # Create character lookup
        char_lookup = {char.name: char for char in characters}

        dialogue_segments = []
        current_time_ms = 0

        for idx, dialogue in enumerate(scene.dialogue):
            # Find character
            character = char_lookup.get(
                dialogue.character,
                characters[0]  # Fallback to first character
            )

            # Synthesize
            audio_file, duration_ms = self._synthesize_dialogue(
                dialogue,
                character,
                run_id,
                scene.id,
                idx
            )

            # Update dialogue object
            dialogue.audio_file = audio_file
            dialogue.duration_ms = duration_ms

            # Add to manifest
            dialogue_segments.append({
                "character": dialogue.character,
                "text": dialogue.text,
                "audio_file": audio_file,
                "start_ms": current_time_ms,
                "end_ms": current_time_ms + duration_ms
            })

            current_time_ms += duration_ms

        return {
            "dialogue_segments": dialogue_segments,
            "total_duration_ms": current_time_ms
        }

    def generate(self, state: PipelineState) -> PipelineState:
        """
        Generate audio for all scenes

        Args:
            state: PipelineState with story, scenes, and characters

        Returns:
            Updated PipelineState with audio files and manifest
        """
        from .music_selector import select_bgm_for_scene
        from datetime import datetime

        if not state.scenes or not state.characters:
            raise ValueError("Cannot generate audio without scenes and characters")

        # Generate audio for each scene
        for scene in state.scenes:
            scene_audio = self.generate_scene_audio(
                scene,
                state.characters,
                state.run_id
            )

            # Select BGM based on mood
            bgm_file = select_bgm_for_scene(scene.mood, state.run_id, scene.id)
            if bgm_file:
                scene.bgm_file = bgm_file

            # Create audio manifest for this scene
            # Note: Full manifest is created in timing.py, this is scene-level
            scene_manifest = AudioManifest(
                scene_id=scene.id,
                dialogue_segments=scene_audio["dialogue_segments"],
                bgm_file=bgm_file,
                bgm_start_ms=0,
                bgm_end_ms=scene.duration_ms,
                total_duration_ms=scene_audio["total_duration_ms"]
            )

        # Update phase status
        state.phase_status["audio"] = "complete"
        state.timestamp = datetime.utcnow().isoformat()

        return state
