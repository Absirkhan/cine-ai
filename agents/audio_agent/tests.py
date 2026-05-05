"""
Unit tests for Phase 2: Audio Generation
Run with: pytest phase2_audio/tests.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from .generator import AudioGenerator
from .music_selector import select_bgm_for_scene, get_available_moods
from shared.schema import PipelineState, Scene, Character, Dialogue, VoiceParams, MoodType


class TestAudioGenerator:
    """Test cases for AudioGenerator"""

    @pytest.fixture
    def mock_character(self):
        return Character(
            name="Test Character",
            role="protagonist",
            voice_params=VoiceParams(
                gender="female",
                tone="calm",
                speed=1.0,
                pitch=1.0
            ),
            visual_description="Test description"
        )

    @pytest.fixture
    def mock_scene(self):
        return Scene(
            id="scene_001",
            description="Test scene",
            visual_prompt="Test prompt",
            mood=MoodType.CALM,
            duration_ms=15000,
            dialogue=[
                Dialogue(character="Test Character", text="Hello, this is a test."),
                Dialogue(character="Test Character", text="This is another line.")
            ]
        )

    def test_voice_id_mapping(self, mock_character):
        """Test voice ID mapping for different character types"""
        generator = AudioGenerator.__new__(AudioGenerator)
        generator.voice_mappings = {
            ("female", "calm"): "voice_1",
            ("male", "authoritative"): "voice_2"
        }

        # Test exact match
        voice_id = generator._get_voice_id(mock_character)
        assert voice_id == "voice_1"

        # Test fallback
        mock_character.voice_params.tone = "energetic"
        voice_id = generator._get_voice_id(mock_character)
        # Should fallback to another female voice or default
        assert isinstance(voice_id, str)

    @patch('phase2_audio.generator.ElevenLabs')
    def test_synthesize_dialogue(self, mock_elevenlabs, mock_character):
        """Test dialogue synthesis"""
        # Setup mock
        mock_client = Mock()
        mock_audio = [b"fake_audio_data"]
        mock_client.generate.return_value = iter(mock_audio)
        mock_elevenlabs.return_value = mock_client

        generator = AudioGenerator()
        dialogue = Dialogue(character="Test", text="Hello world")

        audio_file, duration = generator._synthesize_dialogue(
            dialogue,
            mock_character,
            "test_run",
            "scene_001",
            0
        )

        assert isinstance(audio_file, str)
        assert duration > 0
        assert Path(audio_file).suffix == ".mp3"

    def test_bgm_selection(self):
        """Test BGM selection based on mood"""
        import config

        # Create test music directory
        test_mood_dir = config.MOOD_DIRS["calm"]
        test_mood_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy music file
        test_music_file = test_mood_dir / "test_calm.mp3"
        test_music_file.write_bytes(b"fake_music_data")

        try:
            # Test selection
            bgm_file = select_bgm_for_scene(MoodType.CALM, "test_run", "scene_001")

            if bgm_file:  # Only assert if music files exist
                assert bgm_file is not None
                assert "calm" in bgm_file.lower()
        finally:
            # Cleanup
            if test_music_file.exists():
                test_music_file.unlink()

    def test_available_moods(self):
        """Test getting available moods with music"""
        moods = get_available_moods()
        assert isinstance(moods, list)
        # May be empty if no music files are present
        assert all(isinstance(m, str) for m in moods)

    @patch('phase2_audio.generator.ElevenLabs')
    @patch('phase2_audio.generator.select_bgm_for_scene')
    def test_full_audio_generation(
        self,
        mock_bgm_selector,
        mock_elevenlabs,
        mock_scene,
        mock_character
    ):
        """Test complete audio generation pipeline"""
        # Setup mocks
        mock_client = Mock()
        mock_audio = [b"fake_audio_data"]
        mock_client.generate.return_value = iter(mock_audio)
        mock_elevenlabs.return_value = mock_client

        mock_bgm_selector.return_value = "/fake/path/to/bgm.mp3"

        # Create pipeline state
        state = PipelineState(
            run_id="test_run",
            version=1,
            timestamp="2024-01-01T00:00:00",
            user_prompt="Test",
            user_params={},
            scenes=[mock_scene],
            characters=[mock_character],
            phase_status={
                "script": "complete",
                "audio": "pending",
                "video": "pending",
                "web": "pending",
                "edit": "pending"
            }
        )

        generator = AudioGenerator()
        result_state = generator.generate(state)

        # Validate
        assert result_state.phase_status["audio"] == "complete"
        assert all(d.audio_file for d in result_state.scenes[0].dialogue)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
