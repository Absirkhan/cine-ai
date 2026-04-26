"""
Edit Executor
Executes edit intents by modifying assets and re-running phases
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Optional
import shutil

from shared.schema import EditIntent, PipelineState
from shared.state_manager import StateManager
from .filters import ImageFilters
from phase2_audio.music_selector import select_bgm_for_scene
from shared.schema import MoodType


class EditExecutor:
    """Executes edit operations on pipeline state"""

    def __init__(self):
        self.filters = ImageFilters()

    def execute(
        self,
        intent: EditIntent,
        state: PipelineState,
        state_manager: StateManager
    ) -> PipelineState:
        """
        Execute edit intent on pipeline state

        Args:
            intent: Parsed edit intent
            state: Current pipeline state
            state_manager: State manager for versioning

        Returns:
            Updated pipeline state
        """
        print(f"\n🔧 Executing edit: {intent.intent_type}")
        print(f"   Target: {intent.target}")
        print(f"   Scope: {intent.scope}")
        print(f"   Parameters: {intent.parameters}")

        # Create snapshot before edit
        state_manager.snapshot(
            state,
            f"Before edit: {intent.original_query}",
            self._get_current_assets(state)
        )

        # Execute based on intent type
        if intent.intent_type == "change_voice":
            state = self._change_voice(intent, state)

        elif intent.intent_type == "change_mood" or intent.intent_type == "change_bgm":
            state = self._change_bgm(intent, state)

        elif intent.intent_type == "apply_filter":
            state = self._apply_filter(intent, state)

        elif intent.intent_type == "adjust_duration":
            state = self._adjust_duration(intent, state)

        elif intent.intent_type == "regenerate_scene":
            print("   Note: Scene regeneration requires re-running phases")

        elif intent.intent_type == "change_script":
            print("   Note: Script changes require re-running story generation")

        elif intent.intent_type == "full_regenerate":
            print("   Note: Full regeneration requires re-running entire pipeline")

        # Create snapshot after edit
        state_manager.snapshot(
            state,
            f"After edit: {intent.original_query}",
            self._get_current_assets(state)
        )

        return state

    def _change_voice(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Change voice parameters (requires TTS re-generation)"""
        character_name = None
        if intent.scope and intent.scope.startswith("character:"):
            character_name = intent.scope.split(":")[1]

        # Find character and update voice params
        for character in state.characters:
            if not character_name or character.name == character_name:
                if "tone" in intent.parameters:
                    character.voice_params.tone = intent.parameters["tone"]
                if "speed" in intent.parameters:
                    character.voice_params.speed = float(intent.parameters["speed"])
                if "pitch" in intent.parameters:
                    character.voice_params.pitch = float(intent.parameters["pitch"])

                print(f"   ✓ Updated voice params for {character.name}")

        state.phase_status["audio"] = "needs_regeneration"
        return state

    def _change_bgm(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Change background music by changing scene mood"""
        new_mood = intent.parameters.get("mood", "calm")

        # Get scene if specified
        scene_id = None
        if intent.scope and intent.scope.startswith("scene:"):
            scene_id = intent.scope.split(":")[1]

        # Update mood and re-select BGM
        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                # Update mood
                scene.mood = MoodType(new_mood)

                # Re-select BGM
                new_bgm = select_bgm_for_scene(scene.mood, state.run_id, scene.id)
                if new_bgm:
                    scene.bgm_file = new_bgm
                    print(f"   ✓ Changed BGM for {scene.id} to {new_mood}")

        state.phase_status["video"] = "needs_recomposition"
        return state

    def _apply_filter(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Apply visual filter to scene image"""
        filter_type = intent.parameters.get("filter", "darken")
        amount = intent.parameters.get("amount", 0.3)

        # Get scene if specified
        scene_id = None
        if intent.scope and intent.scope.startswith("scene:"):
            scene_id = intent.scope.split(":")[1]

        # Apply filter to scenes
        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                if not scene.image_file:
                    print(f"   ⚠ No image for {scene.id}")
                    continue

                # Create filtered image path
                original_path = scene.image_file
                filtered_path = original_path.replace(".png", f"_{filter_type}.png")

                # Apply filter
                try:
                    if filter_type == "darken":
                        self.filters.darken(original_path, filtered_path, float(amount))
                    elif filter_type == "brighten":
                        self.filters.brighten(original_path, filtered_path, float(amount))
                    elif filter_type == "contrast":
                        self.filters.adjust_contrast(original_path, filtered_path, float(amount))
                    elif filter_type == "saturation":
                        self.filters.adjust_saturation(original_path, filtered_path, float(amount))
                    elif filter_type == "blur":
                        self.filters.apply_blur(original_path, filtered_path, int(float(amount) * 20))
                    elif filter_type == "grayscale":
                        self.filters.to_grayscale(original_path, filtered_path)
                    elif filter_type == "sepia":
                        self.filters.apply_sepia(original_path, filtered_path)
                    elif filter_type == "warm":
                        self.filters.adjust_temperature(original_path, filtered_path, 1.2)
                    elif filter_type == "cool":
                        self.filters.adjust_temperature(original_path, filtered_path, 0.8)
                    elif filter_type == "vignette":
                        self.filters.apply_vignette(original_path, filtered_path, float(amount))
                    else:
                        print(f"   ⚠ Unknown filter: {filter_type}")
                        continue

                    # Update scene image
                    scene.image_file = filtered_path
                    print(f"   ✓ Applied {filter_type} filter to {scene.id}")

                except Exception as e:
                    print(f"   ✗ Error applying filter: {e}")

        state.phase_status["video"] = "needs_regeneration"
        return state

    def _adjust_duration(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Adjust scene duration"""
        new_duration = intent.parameters.get("duration_ms")
        if not new_duration:
            return state

        scene_id = None
        if intent.scope and intent.scope.startswith("scene:"):
            scene_id = intent.scope.split(":")[1]

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                scene.duration_ms = int(new_duration)
                print(f"   ✓ Adjusted duration for {scene.id} to {new_duration}ms")

        state.phase_status["video"] = "needs_regeneration"
        return state

    def _get_current_assets(self, state: PipelineState) -> list:
        """Get list of all current asset paths"""
        assets = []

        for scene in state.scenes:
            if scene.image_file:
                assets.append(scene.image_file)
            if scene.video_file:
                assets.append(scene.video_file)
            if scene.bgm_file:
                assets.append(scene.bgm_file)

            for dialogue in scene.dialogue:
                if dialogue.audio_file:
                    assets.append(dialogue.audio_file)

        if state.final_video_path:
            assets.append(state.final_video_path)

        return assets
