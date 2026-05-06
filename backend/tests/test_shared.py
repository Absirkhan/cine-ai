"""
Unit tests for shared utilities and schema validation
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.schema import (
    PipelineState, Scene, Character, Dialogue,
    EditIntent, FilterParams, VoiceChangeParams
)
from shared.state_manager import StateManager
import os
import tempfile
import shutil


class TestSchemaValidation:
    """Test Pydantic schema validation"""

    def test_character_creation(self):
        """Test Character model validation"""
        character = Character(
            name="John",
            description="A brave knight",
            personality="Courageous and noble",
            voice_id="ElevenLabs_voice_1"
        )
        assert character.name == "John"
        assert character.voice_id == "ElevenLabs_voice_1"

    def test_dialogue_creation(self):
        """Test Dialogue model validation"""
        dialogue = Dialogue(
            character_name="John",
            text="Hello, world!",
            voice_id="voice_1"
        )
        assert dialogue.character_name == "John"
        assert dialogue.text == "Hello, world!"

    def test_scene_creation(self):
        """Test Scene model validation"""
        scene = Scene(
            scene_number=1,
            description="Opening scene",
            visual_prompt="A castle at dawn",
            dialogues=[
                Dialogue(character_name="John", text="Good morning", voice_id="v1")
            ],
            mood="peaceful"
        )
        assert scene.scene_number == 1
        assert len(scene.dialogues) == 1
        assert scene.mood == "peaceful"

    def test_edit_intent_filter(self):
        """Test EditIntent for filter operations"""
        intent = EditIntent(
            operation="apply_filter",
            scope="scene_1",
            filter_params=FilterParams(filter_type="sepia")
        )
        assert intent.operation == "apply_filter"
        assert intent.filter_params.filter_type == "sepia"

    def test_edit_intent_voice_change(self):
        """Test EditIntent for voice change operations"""
        intent = EditIntent(
            operation="change_voice",
            scope="character_John",
            voice_change_params=VoiceChangeParams(
                new_voice_id="new_voice",
                character_name="John"
            )
        )
        assert intent.operation == "change_voice"
        assert intent.voice_change_params.character_name == "John"


class TestStateManager:
    """Test StateManager version control functionality"""

    @pytest.fixture
    def temp_run_dir(self):
        """Create temporary run directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_state(self):
        """Create a sample PipelineState for testing"""
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
                )
            ],
            scenes=[
                Scene(
                    scene_number=1,
                    description="Opening",
                    visual_prompt="A forest",
                    dialogues=[],
                    mood="mysterious"
                )
            ]
        )

    def test_snapshot_creation(self, temp_run_dir, sample_state):
        """Test creating state snapshots"""
        manager = StateManager(temp_run_dir)

        # Create first snapshot
        version = manager.snapshot(sample_state, "Initial state")
        assert version == 0

        # Create second snapshot
        version = manager.snapshot(sample_state, "Second state")
        assert version == 1

    def test_snapshot_retrieval(self, temp_run_dir, sample_state):
        """Test retrieving state snapshots"""
        manager = StateManager(temp_run_dir)

        # Create snapshot
        version = manager.snapshot(sample_state, "Test snapshot")

        # Retrieve snapshot
        retrieved_state = manager.get_snapshot(version)
        assert retrieved_state is not None
        assert retrieved_state.run_id == sample_state.run_id
        assert retrieved_state.story_title == sample_state.story_title

    def test_history_tracking(self, temp_run_dir, sample_state):
        """Test version history tracking"""
        manager = StateManager(temp_run_dir)

        # Create multiple snapshots
        manager.snapshot(sample_state, "Version 0")
        manager.snapshot(sample_state, "Version 1")
        manager.snapshot(sample_state, "Version 2")

        # Get history
        history = manager.get_history()
        assert len(history) == 3
        assert history[0]["description"] == "Version 0"
        assert history[2]["description"] == "Version 2"

    def test_current_version_tracking(self, temp_run_dir, sample_state):
        """Test current version tracking"""
        manager = StateManager(temp_run_dir)

        assert manager.current_version == -1  # No snapshots yet

        manager.snapshot(sample_state, "V0")
        assert manager.current_version == 0

        manager.snapshot(sample_state, "V1")
        assert manager.current_version == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
