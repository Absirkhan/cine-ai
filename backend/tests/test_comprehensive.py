"""
Comprehensive basic unit and integration tests for CineAI
Tests the core functionality without requiring external API keys
"""
import pytest
import sys
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.schema import (
    PipelineState, Scene, Character, Dialogue, Story,
    VoiceParams, MoodType, EditIntent, AudioManifest
)
from shared.state_manager import StateManager
from phase2_audio.music_selector import get_available_moods


class TestSchemaValidation:
    """Test Pydantic schema validation"""

    def test_voice_params_creation(self):
        """Test VoiceParams model"""
        voice = VoiceParams(
            gender="male",
            tone="calm",
            accent="american",
            speed=1.0,
            pitch=1.0
        )
        assert voice.gender == "male"
        assert voice.tone == "calm"
        assert voice.speed == 1.0

    def test_character_creation(self):
        """Test Character model with all required fields"""
        character = Character(
            name="John",
            role="protagonist",
            voice_params=VoiceParams(gender="male", tone="serious"),
            visual_description="A tall man with dark hair"
        )
        assert character.name == "John"
        assert character.role == "protagonist"
        assert character.voice_params.gender == "male"

    def test_dialogue_creation(self):
        """Test Dialogue model"""
        dialogue = Dialogue(
            character="John",
            text="Hello, world!",
            duration_ms=2000
        )
        assert dialogue.character == "John"
        assert dialogue.text == "Hello, world!"
        assert dialogue.duration_ms == 2000

    def test_scene_creation(self):
        """Test Scene model with required fields"""
        scene = Scene(
            id="scene_001",
            description="Opening scene",
            visual_prompt="A castle at dawn",
            dialogue=[
                Dialogue(character="John", text="Good morning", duration_ms=1500)
            ],
            mood=MoodType.CALM,
            duration_ms=5000
        )
        assert scene.id == "scene_001"
        assert len(scene.dialogue) == 1
        assert scene.mood == MoodType.CALM
        assert scene.duration_ms == 5000

    def test_story_creation(self):
        """Test Story model"""
        story = Story(
            title="The Adventure",
            summary="An epic tale",
            genre="Fantasy",
            tone="Cinematic",
            total_duration_ms=60000
        )
        assert story.title == "The Adventure"
        assert story.genre == "Fantasy"

    def test_mood_enum_values(self):
        """Test MoodType enum values"""
        valid_moods = [
            MoodType.CALM, MoodType.TENSE, MoodType.UPBEAT,
            MoodType.MYSTERIOUS, MoodType.DRAMATIC, MoodType.SAD, MoodType.AMBIENT
        ]
        assert len(valid_moods) == 7
        assert MoodType.CALM.value == "calm"

    def test_edit_intent_creation(self):
        """Test EditIntent for voice change"""
        intent = EditIntent(
            intent_type="change_voice",
            target="audio",
            scope="character:Alice",
            parameters={"new_voice": "voice_123"},
            original_query="Change Alice's voice"
        )
        assert intent.intent_type == "change_voice"
        assert intent.target == "audio"
        assert intent.scope == "character:Alice"


class TestStateManager:
    """Test StateManager version control functionality"""

    @pytest.fixture
    def temp_run_dir(self):
        """Create temporary run directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_state(self):
        """Create a minimal valid PipelineState"""
        return PipelineState(
            run_id="test_run",
            timestamp=datetime.utcnow().isoformat(),
            user_prompt="Test prompt",
            story=Story(
                title="Test Story",
                summary="A test story",
                genre="Test",
                tone="Test",
                total_duration_ms=30000
            )
        )

    def test_snapshot_creation(self, temp_run_dir, sample_state):
        """Test creating state snapshots"""
        manager = StateManager(temp_run_dir)
        version = manager.snapshot(sample_state, "Initial state")
        assert version == 1  # First version is 1

    def test_multiple_snapshots(self, temp_run_dir, sample_state):
        """Test creating multiple snapshots"""
        manager = StateManager(temp_run_dir)

        v1 = manager.snapshot(sample_state, "Version 1")
        assert v1 == 1

        v2 = manager.snapshot(sample_state, "Version 2")
        assert v2 == 2

        v3 = manager.snapshot(sample_state, "Version 3")
        assert v3 == 3

    def test_snapshot_retrieval(self, temp_run_dir, sample_state):
        """Test retrieving state snapshots"""
        manager = StateManager(temp_run_dir)
        version = manager.snapshot(sample_state, "Test snapshot")

        retrieved_snapshot = manager.get_snapshot(version)
        assert retrieved_snapshot is not None
        assert retrieved_snapshot.state.run_id == sample_state.run_id

    def test_history_tracking(self, temp_run_dir, sample_state):
        """Test version history tracking"""
        manager = StateManager(temp_run_dir)

        manager.snapshot(sample_state, "Version 1")
        manager.snapshot(sample_state, "Version 2")
        manager.snapshot(sample_state, "Version 3")

        history = manager.get_history()
        assert len(history) == 3
        assert history[0]["description"] == "Version 1"

    def test_current_version_tracking(self, temp_run_dir, sample_state):
        """Test current version tracking"""
        manager = StateManager(temp_run_dir)

        assert manager.current_version == 0  # Starts at 0

        manager.snapshot(sample_state, "V1")
        assert manager.current_version == 1  # First snapshot is version 1


class TestPipelineIntegration:
    """Test integration between pipeline components"""

    @pytest.fixture
    def complete_state(self):
        """Create a complete pipeline state"""
        return PipelineState(
            run_id="integration_test",
            timestamp=datetime.utcnow().isoformat(),
            user_prompt="A story about adventure",
            story=Story(
                title="The Great Adventure",
                summary="An epic tale of courage",
                genre="Fantasy",
                tone="Cinematic",
                total_duration_ms=90000
            ),
            characters=[
                Character(
                    name="Hero",
                    role="protagonist",
                    voice_params=VoiceParams(gender="male", tone="confident"),
                    visual_description="A brave warrior in armor"
                ),
                Character(
                    name="Guide",
                    role="mentor",
                    voice_params=VoiceParams(gender="female", tone="calm"),
                    visual_description="A wise elder in robes"
                )
            ],
            scenes=[
                Scene(
                    id="scene_001",
                    description="The journey begins",
                    visual_prompt="A hero standing at the edge of a vast forest at dawn",
                    dialogue=[
                        Dialogue(
                            character="Hero",
                            text="The journey begins today.",
                            duration_ms=2000
                        ),
                        Dialogue(
                            character="Guide",
                            text="Follow the path and trust your instincts.",
                            duration_ms=3000
                        )
                    ],
                    mood=MoodType.UPBEAT,
                    duration_ms=8000
                ),
                Scene(
                    id="scene_002",
                    description="Facing challenges",
                    visual_prompt="Dark storm clouds gathering over mountains",
                    dialogue=[
                        Dialogue(
                            character="Hero",
                            text="The storm approaches. I must be strong.",
                            duration_ms=3000
                        )
                    ],
                    mood=MoodType.TENSE,
                    duration_ms=6000
                )
            ]
        )

    def test_character_to_scene_mapping(self, complete_state):
        """Test that characters are properly linked to dialogues"""
        char_names = {char.name for char in complete_state.characters}
        assert "Hero" in char_names
        assert "Guide" in char_names

        for scene in complete_state.scenes:
            for dialogue in scene.dialogue:
                assert dialogue.character in char_names

    def test_scene_mood_consistency(self, complete_state):
        """Test that scenes have valid mood values"""
        for scene in complete_state.scenes:
            assert isinstance(scene.mood, MoodType)

    def test_scene_numbering(self, complete_state):
        """Test that scenes have unique IDs"""
        scene_ids = [scene.id for scene in complete_state.scenes]
        assert len(scene_ids) == len(set(scene_ids))  # All unique

    def test_state_serialization(self, complete_state):
        """Test that state can be serialized to JSON"""
        json_data = complete_state.model_dump()
        assert json_data["run_id"] == "integration_test"
        assert len(json_data["scenes"]) == 2
        assert len(json_data["characters"]) == 2


class TestBGMSelection:
    """Test background music selection logic"""

    def test_get_available_moods(self):
        """Test retrieving available mood categories"""
        moods = get_available_moods()
        assert isinstance(moods, list)


class TestAudioManifest:
    """Test audio manifest structure"""

    def test_audio_manifest_creation(self):
        """Test creating audio manifest"""
        manifest = AudioManifest(
            scene_id="scene_001",
            dialogue_segments=[
                {
                    "character": "Hero",
                    "audio_file": "hero_001.mp3",
                    "start_ms": 0,
                    "end_ms": 2000
                }
            ],
            bgm_file="background.mp3",
            bgm_start_ms=0,
            total_duration_ms=8000
        )
        assert manifest.scene_id == "scene_001"
        assert len(manifest.dialogue_segments) == 1
        assert manifest.total_duration_ms == 8000


class TestVersioningWorkflow:
    """Test full versioning workflow"""

    @pytest.fixture
    def temp_run_dir(self):
        """Create temporary run directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_edit_workflow_with_versions(self, temp_run_dir):
        """Test full edit workflow with versioning"""
        manager = StateManager(temp_run_dir)

        # Initial state
        state = PipelineState(
            run_id="edit_test",
            timestamp=datetime.utcnow().isoformat(),
            user_prompt="Test edit workflow",
            story=Story(
                title="Edit Test",
                summary="Testing edits",
                genre="Test",
                tone="Test",
                total_duration_ms=30000
            ),
            characters=[
                Character(
                    name="Alice",
                    role="protagonist",
                    voice_params=VoiceParams(gender="female", tone="cheerful"),
                    visual_description="A young woman"
                )
            ],
            scenes=[
                Scene(
                    id="scene_001",
                    description="Opening",
                    visual_prompt="A forest",
                    mood=MoodType.CALM,
                    duration_ms=5000
                )
            ]
        )

        # Version 1: Initial
        v1 = manager.snapshot(state, "Initial generation")
        assert v1 == 1

        # Edit: Change character voice tone
        state.characters[0].voice_params.tone = "serious"
        v2 = manager.snapshot(state, "Changed Alice's voice tone")
        assert v2 == 2

        # Edit: Add a new scene
        new_scene = Scene(
            id="scene_002",
            description="Resolution",
            visual_prompt="Sunset over valley",
            mood=MoodType.CALM,
            duration_ms=5000
        )
        state.scenes.append(new_scene)
        v3 = manager.snapshot(state, "Added resolution scene")
        assert v3 == 3

        # Verify history
        history = manager.get_history()
        assert len(history) == 3

        # Verify versions can be retrieved
        snapshot_v1 = manager.get_snapshot(1)
        assert len(snapshot_v1.state.scenes) == 1
        assert snapshot_v1.state.characters[0].voice_params.tone == "cheerful"

        snapshot_v2 = manager.get_snapshot(2)
        assert snapshot_v2.state.characters[0].voice_params.tone == "serious"

        snapshot_v3 = manager.get_snapshot(3)
        assert len(snapshot_v3.state.scenes) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
