"""
Basic unit tests for Phase 5 (Edit Agent)
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase5_edit.intent_parser import IntentParser
from shared.schema import PipelineState, Scene, Character, EditIntent


class TestIntentParserUtilities:
    """Test utility functions in IntentParser"""

    @pytest.fixture
    def parser(self):
        """Create IntentParser instance"""
        return IntentParser()

    @pytest.fixture
    def sample_state(self):
        """Create sample state for testing"""
        return PipelineState(
            run_id="test_run",
            user_prompt="Test prompt",
            story_title="Test Story",
            characters=[
                Character(
                    name="Alice",
                    description="Protagonist",
                    personality="Brave",
                    voice_id="voice_1"
                ),
                Character(
                    name="Bob",
                    description="Sidekick",
                    personality="Funny",
                    voice_id="voice_2"
                )
            ],
            scenes=[
                Scene(
                    scene_number=1,
                    description="Opening",
                    visual_prompt="A forest",
                    dialogues=[],
                    mood="mysterious"
                ),
                Scene(
                    scene_number=2,
                    description="Confrontation",
                    visual_prompt="A castle",
                    dialogues=[],
                    mood="tense"
                )
            ]
        )

    def test_get_scene_id_from_scope_numeric(self, parser, sample_state):
        """Test extracting scene ID from numeric scope"""
        scene_id = parser.get_scene_id_from_scope("scene_1", sample_state)
        assert scene_id == 1

    def test_get_scene_id_from_scope_word(self, parser, sample_state):
        """Test extracting scene ID from word-based scope"""
        scene_id = parser.get_scene_id_from_scope("first_scene", sample_state)
        assert scene_id == 1

        scene_id = parser.get_scene_id_from_scope("second_scene", sample_state)
        assert scene_id == 2

    def test_get_scene_id_from_scope_all(self, parser, sample_state):
        """Test 'all' scope returns None"""
        scene_id = parser.get_scene_id_from_scope("all", sample_state)
        assert scene_id is None

    def test_get_scene_id_invalid_scope(self, parser, sample_state):
        """Test invalid scope returns None"""
        scene_id = parser.get_scene_id_from_scope("scene_999", sample_state)
        assert scene_id is None

    def test_get_character_name_from_scope(self, parser, sample_state):
        """Test extracting character name from scope"""
        char_name = parser.get_character_name_from_scope("character_Alice", sample_state)
        assert char_name == "Alice"

        char_name = parser.get_character_name_from_scope("character_Bob", sample_state)
        assert char_name == "Bob"

    def test_get_character_name_case_insensitive(self, parser, sample_state):
        """Test character name extraction is case-insensitive"""
        char_name = parser.get_character_name_from_scope("character_alice", sample_state)
        assert char_name == "Alice"

        char_name = parser.get_character_name_from_scope("character_bob", sample_state)
        assert char_name == "Bob"

    def test_get_character_name_not_found(self, parser, sample_state):
        """Test when character not found"""
        char_name = parser.get_character_name_from_scope("character_Charlie", sample_state)
        assert char_name is None


class TestEditIntentStructure:
    """Test EditIntent schema and structure"""

    def test_filter_intent_creation(self):
        """Test creating a filter intent"""
        from shared.schema import FilterParams

        intent = EditIntent(
            operation="apply_filter",
            scope="scene_1",
            filter_params=FilterParams(filter_type="sepia", intensity=0.7)
        )

        assert intent.operation == "apply_filter"
        assert intent.scope == "scene_1"
        assert intent.filter_params.filter_type == "sepia"
        assert intent.filter_params.intensity == 0.7

    def test_voice_change_intent_creation(self):
        """Test creating a voice change intent"""
        from shared.schema import VoiceChangeParams

        intent = EditIntent(
            operation="change_voice",
            scope="character_Alice",
            voice_change_params=VoiceChangeParams(
                new_voice_id="new_voice_123",
                character_name="Alice"
            )
        )

        assert intent.operation == "change_voice"
        assert intent.voice_change_params.character_name == "Alice"
        assert intent.voice_change_params.new_voice_id == "new_voice_123"

    def test_undo_intent_creation(self):
        """Test creating an undo intent"""
        intent = EditIntent(
            operation="undo",
            scope="all"
        )

        assert intent.operation == "undo"
        assert intent.scope == "all"


class TestFilterValidation:
    """Test filter parameter validation"""

    def test_valid_filter_types(self):
        """Test that valid filter types are accepted"""
        from shared.schema import FilterParams

        valid_filters = [
            "sepia", "grayscale", "blur", "sharpen",
            "brightness", "contrast", "saturation",
            "vintage", "vignette", "edge_detect"
        ]

        for filter_type in valid_filters:
            params = FilterParams(filter_type=filter_type)
            assert params.filter_type == filter_type

    def test_filter_intensity_range(self):
        """Test filter intensity is within valid range"""
        from shared.schema import FilterParams

        # Valid intensities
        params = FilterParams(filter_type="sepia", intensity=0.0)
        assert params.intensity == 0.0

        params = FilterParams(filter_type="sepia", intensity=0.5)
        assert params.intensity == 0.5

        params = FilterParams(filter_type="sepia", intensity=1.0)
        assert params.intensity == 1.0


class TestParserInitialization:
    """Test parser initialization and setup"""

    def test_parser_creation(self):
        """Test that parser can be created"""
        parser = IntentParser()
        assert parser is not None
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'get_scene_id_from_scope')
        assert hasattr(parser, 'get_character_name_from_scope')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
