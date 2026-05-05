"""
Basic integration tests for the CineAI pipeline
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.schema import PipelineState, Character, Scene, Dialogue
from shared.state_manager import StateManager
from phase2_audio.music_selector import select_bgm_for_scene
import tempfile
import shutil


class TestPipelineIntegration:
    """Test integration between pipeline components"""

    @pytest.fixture
    def temp_run_dir(self):
        """Create temporary run directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def complete_state(self):
        """Create a complete pipeline state for testing"""
        return PipelineState(
            run_id="integration_test",
            user_prompt="A story about adventure",
            story_title="The Great Adventure",
            story_summary="An epic tale of courage and discovery",
            characters=[
                Character(
                    name="Hero",
                    description="The brave protagonist",
                    personality="Courageous and determined",
                    voice_id="ElevenLabs_voice_hero"
                ),
                Character(
                    name="Guide",
                    description="The wise mentor",
                    personality="Calm and knowledgeable",
                    voice_id="ElevenLabs_voice_guide"
                )
            ],
            scenes=[
                Scene(
                    scene_number=1,
                    description="The journey begins",
                    visual_prompt="A hero standing at the edge of a vast forest at dawn",
                    dialogues=[
                        Dialogue(
                            character_name="Hero",
                            text="The journey begins today.",
                            voice_id="ElevenLabs_voice_hero"
                        ),
                        Dialogue(
                            character_name="Guide",
                            text="Follow the path and trust your instincts.",
                            voice_id="ElevenLabs_voice_guide"
                        )
                    ],
                    mood="inspirational"
                ),
                Scene(
                    scene_number=2,
                    description="Facing challenges",
                    visual_prompt="Dark storm clouds gathering over mountains",
                    dialogues=[
                        Dialogue(
                            character_name="Hero",
                            text="The storm approaches. I must be strong.",
                            voice_id="ElevenLabs_voice_hero"
                        )
                    ],
                    mood="tense"
                )
            ]
        )

    def test_state_persistence_and_retrieval(self, temp_run_dir, complete_state):
        """Test that pipeline state can be saved and retrieved"""
        # Create state manager
        manager = StateManager(temp_run_dir)

        # Save initial state
        version = manager.snapshot(complete_state, "Initial generation")
        assert version == 0

        # Retrieve state
        retrieved = manager.get_snapshot(version)
        assert retrieved.run_id == complete_state.run_id
        assert retrieved.story_title == complete_state.story_title
        assert len(retrieved.characters) == len(complete_state.characters)
        assert len(retrieved.scenes) == len(complete_state.scenes)

    def test_character_to_scene_mapping(self, complete_state):
        """Test that characters are properly linked to dialogues in scenes"""
        # Get all character names
        char_names = {char.name for char in complete_state.characters}
        assert "Hero" in char_names
        assert "Guide" in char_names

        # Verify dialogues reference existing characters
        for scene in complete_state.scenes:
            for dialogue in scene.dialogues:
                assert dialogue.character_name in char_names

    def test_scene_mood_consistency(self, complete_state):
        """Test that scenes have valid mood values"""
        valid_moods = [
            "action", "adventurous", "calm", "dark", "dramatic",
            "epic", "happy", "inspirational", "mysterious",
            "peaceful", "romantic", "sad", "suspenseful", "tense"
        ]

        for scene in complete_state.scenes:
            assert scene.mood in valid_moods

    def test_bgm_selection_integration(self, complete_state):
        """Test BGM selection for multiple scenes"""
        for scene in complete_state.scenes:
            bgm_path = select_bgm_for_scene(scene)
            # BGM may be None if library not available
            assert bgm_path is None or isinstance(bgm_path, str)

    def test_state_versioning_workflow(self, temp_run_dir, complete_state):
        """Test full versioning workflow with multiple edits"""
        manager = StateManager(temp_run_dir)

        # Version 0: Initial state
        v0 = manager.snapshot(complete_state, "Initial generation")
        assert v0 == 0

        # Simulate an edit: change a character's voice
        complete_state.characters[0].voice_id = "ElevenLabs_new_voice"
        v1 = manager.snapshot(complete_state, "Changed Hero's voice")
        assert v1 == 1

        # Simulate another edit: add a new scene
        new_scene = Scene(
            scene_number=3,
            description="The resolution",
            visual_prompt="Sunset over a peaceful valley",
            dialogues=[],
            mood="peaceful"
        )
        complete_state.scenes.append(new_scene)
        v2 = manager.snapshot(complete_state, "Added resolution scene")
        assert v2 == 2

        # Verify history
        history = manager.get_history()
        assert len(history) == 3
        assert history[0]["description"] == "Initial generation"
        assert history[1]["description"] == "Changed Hero's voice"
        assert history[2]["description"] == "Added resolution scene"

        # Retrieve and verify each version
        state_v0 = manager.get_snapshot(0)
        assert len(state_v0.scenes) == 2
        assert state_v0.characters[0].voice_id == "ElevenLabs_voice_hero"

        state_v1 = manager.get_snapshot(1)
        assert state_v1.characters[0].voice_id == "ElevenLabs_new_voice"

        state_v2 = manager.get_snapshot(2)
        assert len(state_v2.scenes) == 3

    def test_dialogue_voice_consistency(self, complete_state):
        """Test that dialogue voice IDs match character voice IDs"""
        # Build character voice mapping
        char_voices = {char.name: char.voice_id for char in complete_state.characters}

        # Check each dialogue
        for scene in complete_state.scenes:
            for dialogue in scene.dialogues:
                expected_voice = char_voices.get(dialogue.character_name)
                # Voice ID should match the character's voice
                assert dialogue.voice_id == expected_voice

    def test_scene_numbering_sequence(self, complete_state):
        """Test that scenes are numbered sequentially"""
        scene_numbers = [scene.scene_number for scene in complete_state.scenes]
        scene_numbers.sort()

        # Should start at 1 and be sequential
        assert scene_numbers[0] == 1
        for i in range(1, len(scene_numbers)):
            assert scene_numbers[i] == scene_numbers[i-1] + 1


class TestPipelineStateValidation:
    """Test comprehensive state validation"""

    def test_minimal_valid_state(self):
        """Test that minimal valid state can be created"""
        state = PipelineState(
            run_id="minimal_test",
            user_prompt="Test",
            story_title="Test Story",
            characters=[],
            scenes=[]
        )

        assert state.run_id == "minimal_test"
        assert len(state.characters) == 0
        assert len(state.scenes) == 0

    def test_state_with_complete_data(self):
        """Test state with all fields populated"""
        state = PipelineState(
            run_id="complete_test",
            user_prompt="A complete test",
            story_title="Complete Test Story",
            story_summary="A full test of the state",
            characters=[
                Character(
                    name="TestChar",
                    description="Test character",
                    personality="Test personality",
                    voice_id="test_voice"
                )
            ],
            scenes=[
                Scene(
                    scene_number=1,
                    description="Test scene",
                    visual_prompt="A test visual",
                    dialogues=[
                        Dialogue(
                            character_name="TestChar",
                            text="Test dialogue",
                            voice_id="test_voice"
                        )
                    ],
                    mood="calm"
                )
            ]
        )

        # Verify all fields
        assert state.run_id == "complete_test"
        assert state.story_title == "Complete Test Story"
        assert len(state.characters) == 1
        assert len(state.scenes) == 1
        assert state.scenes[0].dialogues[0].text == "Test dialogue"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
