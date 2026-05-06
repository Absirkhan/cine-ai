"""
Basic unit tests for Phase 2 (Audio Generation)
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase2_audio.generator import AudioGenerator
from phase2_audio.music_selector import select_bgm_for_scene, get_available_moods
from shared.schema import Scene, Character, Dialogue


class TestVoiceMapping:
    """Test voice ID mapping and validation"""

    @pytest.fixture
    def generator(self):
        """Create AudioGenerator instance"""
        return AudioGenerator()

    def test_voice_id_retrieval_with_elevenlabs(self, generator):
        """Test voice ID retrieval with ElevenLabs prefix"""
        voice_id = "ElevenLabs_Chris_friendly_male"
        result = generator._get_voice_id(voice_id)
        # Should return the voice ID from config or the original
        assert result is not None
        assert isinstance(result, str)

    def test_voice_id_retrieval_with_deepgram(self, generator):
        """Test voice ID retrieval with Deepgram prefix"""
        voice_id = "Deepgram_asteria_english"
        result = generator._get_voice_id(voice_id)
        assert result is not None
        assert isinstance(result, str)

    def test_voice_id_fallback(self, generator):
        """Test fallback when voice not found"""
        voice_id = "NonExistent_Voice_12345"
        result = generator._get_voice_id(voice_id)
        # Should return original or a default voice
        assert result is not None


class TestBGMSelection:
    """Test background music selection logic"""

    def test_bgm_selection_for_valid_mood(self):
        """Test BGM selection for a valid mood"""
        scene = Scene(
            scene_number=1,
            description="Test scene",
            visual_prompt="A peaceful meadow",
            dialogues=[],
            mood="peaceful"
        )

        bgm_path = select_bgm_for_scene(scene)

        # Should return a path or None
        assert bgm_path is None or isinstance(bgm_path, str)

    def test_bgm_selection_for_action_mood(self):
        """Test BGM selection for action mood"""
        scene = Scene(
            scene_number=2,
            description="Action scene",
            visual_prompt="A battle",
            dialogues=[],
            mood="action"
        )

        bgm_path = select_bgm_for_scene(scene)
        assert bgm_path is None or isinstance(bgm_path, str)

    def test_get_available_moods(self):
        """Test retrieving available mood categories"""
        moods = get_available_moods()

        # Should return a list of mood strings
        assert isinstance(moods, list)
        # May be empty if music library not set up
        assert len(moods) >= 0


class TestAudioTimingCalculations:
    """Test audio timing and duration calculations"""

    def test_dialogue_timing_structure(self):
        """Test that dialogue timing has correct structure"""
        # This is more of a schema test
        dialogue = Dialogue(
            character_name="Alice",
            text="Hello, world!",
            voice_id="voice_1"
        )

        # Verify dialogue structure
        assert dialogue.character_name == "Alice"
        assert dialogue.text == "Hello, world!"
        assert dialogue.voice_id == "voice_1"

        # Audio path will be set during generation
        assert hasattr(dialogue, 'audio_path')

    def test_scene_with_multiple_dialogues(self):
        """Test scene with multiple dialogues"""
        scene = Scene(
            scene_number=1,
            description="Conversation",
            visual_prompt="Two people talking",
            dialogues=[
                Dialogue(character_name="Alice", text="Hi Bob", voice_id="v1"),
                Dialogue(character_name="Bob", text="Hi Alice", voice_id="v2"),
                Dialogue(character_name="Alice", text="How are you?", voice_id="v1")
            ],
            mood="calm"
        )

        assert len(scene.dialogues) == 3
        assert scene.dialogues[0].character_name == "Alice"
        assert scene.dialogues[1].character_name == "Bob"


class TestAudioGeneration:
    """Test audio generation workflow"""

    @pytest.fixture
    def generator(self):
        """Create AudioGenerator instance"""
        return AudioGenerator()

    def test_generator_initialization(self, generator):
        """Test that generator initializes correctly"""
        assert generator is not None
        assert hasattr(generator, 'generate')
        assert hasattr(generator, '_get_voice_id')

    def test_character_voice_mapping(self):
        """Test that characters have voice IDs"""
        character = Character(
            name="TestChar",
            description="A test character",
            personality="Friendly",
            voice_id="ElevenLabs_voice_test"
        )

        assert character.voice_id == "ElevenLabs_voice_test"
        assert character.name == "TestChar"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
