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

    def _normalize_scene_id(self, scope: str) -> Optional[str]:
        """
        Normalize scene ID from scope string

        Converts:
        - "scene:2" -> "scene_001" (1-indexed user input to 0-indexed scene ID)
        - "scene:scene_002" -> "scene_002"
        - "scene:scene_2" -> "scene_002"
        - "scene:scene_1" -> "scene_000"

        Returns None if no scene scope provided
        """
        if not scope or not scope.startswith("scene:"):
            return None

        raw_id = scope.split(":")[1]

        # If it's already in scene_XXX format (3 digits), return as-is
        if raw_id.startswith("scene_") and len(raw_id) == 9:  # scene_XXX = 9 chars
            return raw_id

        # If it's just a number, convert to scene_XXX format (0-indexed)
        if raw_id.isdigit():
            return f"scene_{int(raw_id)-1:03d}"

        # Try to extract number from formats like "scene_2" or "scene2"
        import re
        match = re.search(r'\d+', raw_id)
        if match:
            num = int(match.group())
            # Always treat as 1-indexed and convert to 0-indexed
            return f"scene_{num-1:03d}"

        return raw_id

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

        elif intent.intent_type == "add_bgm":
            state = self._add_bgm(intent, state)

        elif intent.intent_type == "remove_bgm":
            state = self._remove_bgm(intent, state)

        elif intent.intent_type == "apply_filter":
            state = self._apply_filter(intent, state)

        elif intent.intent_type == "adjust_duration":
            state = self._adjust_duration(intent, state)

        elif intent.intent_type == "speed_up":
            state = self._speed_up(intent, state)

        elif intent.intent_type == "slow_down":
            state = self._slow_down(intent, state)

        elif intent.intent_type == "toggle_subtitles":
            state = self._toggle_subtitles(intent, state)

        elif intent.intent_type == "change_scene_characters":
            state = self._change_scene_characters(intent, state)

        elif intent.intent_type == "change_character_design":
            state = self._change_character_design(intent, state)

        elif intent.intent_type == "regenerate_scene":
            state = self._regenerate_scene(intent, state)

        elif intent.intent_type == "change_script":
            state = self._change_script(intent, state)

        elif intent.intent_type == "regenerate_script":
            state = self._regenerate_script(intent, state)

        elif intent.intent_type == "full_regenerate":
            state = self._full_regenerate(intent, state)

        # Create snapshot after edit
        state_manager.snapshot(
            state,
            f"After edit: {intent.original_query}",
            self._get_current_assets(state)
        )

        return state

    def _change_voice(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Change voice parameters (requires TTS re-generation)"""
        # Parse combined scope: "character:Narrator, scene:2" or just "character:Narrator"
        character_name = None
        scene_id = None

        if intent.scope:
            # Split by comma to handle combined scopes
            scope_parts = [s.strip() for s in intent.scope.split(",")]

            for part in scope_parts:
                if part.startswith("character:"):
                    character_name = part.split(":", 1)[1].strip()
                elif part.startswith("scene:"):
                    scene_id = self._normalize_scene_id(part)

        # If scene-specific, modify dialogue in that scene only
        if scene_id:
            modified_count = 0
            for scene in state.scenes:
                if scene.id == scene_id:
                    for dialogue in scene.dialogue:
                        if not character_name or dialogue.character == character_name:
                            # Clear audio to force regeneration with new tone
                            dialogue.audio_file = None
                            dialogue.duration_ms = None

                            # Add tone modifier to the dialogue text
                            if "tone" in intent.parameters:
                                tone = intent.parameters["tone"]
                                # Check if tone modifier already exists
                                if not dialogue.text.startswith(f"[{tone}]"):
                                    dialogue.text = f"[{tone}] {dialogue.text}"

                            modified_count += 1

                    if modified_count > 0:
                        print(f"   ✓ Updated voice tone for {character_name or 'all characters'} in {scene.id} ({modified_count} dialogue(s))")

        # Otherwise, update character's global voice params
        else:
            for character in state.characters:
                if not character_name or character.name == character_name:
                    if "tone" in intent.parameters:
                        character.voice_params.tone = intent.parameters["tone"]
                    if "speed" in intent.parameters:
                        character.voice_params.speed = float(intent.parameters["speed"])
                    if "pitch" in intent.parameters:
                        character.voice_params.pitch = float(intent.parameters["pitch"])

                    print(f"   ✓ Updated voice params for {character.name} (all scenes)")

        state.phase_status["audio"] = "needs_regeneration"
        return state

    def _change_bgm(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Change background music by changing scene mood"""
        new_mood = intent.parameters.get("mood", "calm")

        # Get scene if specified
        scene_id = self._normalize_scene_id(intent.scope)

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
        scene_id = self._normalize_scene_id(intent.scope)

        # Apply filter to scenes
        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                if not scene.image_file:
                    print(f"   ⚠ No image for {scene.id}")
                    continue

                # Create filtered image path using version number for clean naming
                original_path = scene.image_file
                path_obj = Path(original_path)

                # Use state version for unique naming: image_scene_000_v4_darken.png
                # This avoids chained names like image_scene_000_darken_brighten_contrast.png
                filtered_filename = f"{path_obj.stem}_v{state.version}_{filter_type}{path_obj.suffix}"
                filtered_path = str(path_obj.parent / filtered_filename)

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

        scene_id = self._normalize_scene_id(intent.scope)

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                scene.duration_ms = int(new_duration)
                print(f"   ✓ Adjusted duration for {scene.id} to {new_duration}ms")

        state.phase_status["video"] = "needs_regeneration"
        return state

    def _add_bgm(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Add background music to scene(s)"""
        mood = intent.parameters.get("mood", "ambient")

        scene_id = self._normalize_scene_id(intent.scope)

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                scene.mood = MoodType(mood)
                new_bgm = select_bgm_for_scene(scene.mood, state.run_id, scene.id)
                if new_bgm:
                    scene.bgm_file = new_bgm
                    print(f"   ✓ Added BGM to {scene.id}")

        state.phase_status["video"] = "needs_recomposition"
        return state

    def _remove_bgm(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Remove background music from scene(s)"""
        scene_id = self._normalize_scene_id(intent.scope)

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                scene.bgm_file = None
                print(f"   ✓ Removed BGM from {scene.id}")

        state.phase_status["video"] = "needs_recomposition"
        return state

    def _speed_up(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Speed up scene(s) by adjusting duration"""
        speed_multiplier = intent.parameters.get("speed_multiplier", 1.5)

        scene_id = self._normalize_scene_id(intent.scope)

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                new_duration = int(scene.duration_ms / speed_multiplier)
                scene.duration_ms = new_duration
                print(f"   ✓ Sped up {scene.id} to {new_duration}ms (speed: {speed_multiplier}x)")

        state.phase_status["video"] = "needs_regeneration"
        return state

    def _slow_down(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Slow down scene(s) by adjusting duration"""
        speed_multiplier = intent.parameters.get("speed_multiplier", 0.75)

        scene_id = self._normalize_scene_id(intent.scope)

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                new_duration = int(scene.duration_ms / speed_multiplier)
                scene.duration_ms = new_duration
                print(f"   ✓ Slowed down {scene.id} to {new_duration}ms (speed: {speed_multiplier}x)")

        state.phase_status["video"] = "needs_regeneration"
        return state

    def _toggle_subtitles(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Toggle subtitle visibility for scene(s)"""
        show_subtitles = intent.parameters.get("show_subtitles", False)

        scene_id = self._normalize_scene_id(intent.scope)

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                scene.has_subtitles = show_subtitles
                status = "shown" if show_subtitles else "hidden"
                print(f"   ✓ Subtitles {status} for {scene.id}")

        state.phase_status["video"] = "needs_recomposition"
        return state

    def _change_scene_characters(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Change character composition for a scene"""
        genders = intent.parameters.get("genders", [])
        character_count = intent.parameters.get("character_count", len(genders))

        scene_id = self._normalize_scene_id(intent.scope)

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                # Update character genders for this scene
                if genders:
                    # Map genders to existing characters or create overrides
                    for i, gender in enumerate(genders[:character_count]):
                        if i < len(state.characters):
                            char_name = state.characters[i].name
                            if char_name not in scene.character_visual_overrides:
                                scene.character_visual_overrides[char_name] = {}
                            scene.character_visual_overrides[char_name]["gender"] = gender

                # Update characters in scene list
                scene.characters_in_scene = [c.name for c in state.characters[:character_count]]

                print(f"   ✓ Updated character composition for {scene.id}: {genders}")
                print(f"   Characters in scene: {scene.characters_in_scene}")

        state.phase_status["video"] = "needs_regeneration"
        return state

    def _change_character_design(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Change character visual design (requires re-generation)"""
        # Extract scope (which scene to modify)
        scene_id = self._normalize_scene_id(intent.scope)

        # Extract parameters
        character_name = intent.parameters.get("character_name") or intent.parameters.get("reference_character")
        reference_scene = intent.parameters.get("reference_scene")
        new_description = intent.parameters.get("visual_description")
        new_gender = intent.parameters.get("gender")

        # If reference_scene is provided, extract character description from that scene
        reference_prompt = None
        if reference_scene:
            # Clean scene ID (remove "scene:" prefix if present)
            ref_scene_id = reference_scene.replace("scene:", "")

            for scene in state.scenes:
                if scene.id == ref_scene_id:
                    reference_prompt = scene.visual_prompt
                    print(f"   Using reference prompt from {ref_scene_id}")
                    break

        # Update the target scene(s)
        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                # If we have a reference prompt, we need to modify this scene's prompt
                # to match the character appearance from the reference scene
                if reference_prompt and character_name:
                    # For now, add an override instruction to the visual prompt
                    # In a more sophisticated version, we'd parse and merge the prompts
                    override_instruction = f"\n\nIMPORTANT: {character_name} should have the same visual appearance (age, features, style) as in the reference image."

                    if override_instruction not in scene.visual_prompt:
                        scene.visual_prompt += override_instruction
                        print(f"   ✓ Added appearance override for {character_name} in {scene.id}")

                # Clear image to force regeneration with updated prompt
                if scene.image_file:
                    scene.image_file = None
                    scene.video_file = None
                    print(f"   ✓ Cleared assets for {scene.id} to force regeneration")

        # Also update global character metadata if new_description provided
        for character in state.characters:
            if character_name and character.name == character_name:
                if new_description:
                    character.visual_description = new_description
                if new_gender:
                    character.voice_params.gender = new_gender
                print(f"   ✓ Updated visual design for {character.name}")

        state.phase_status["video"] = "needs_regeneration"
        return state

    def _regenerate_scene(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Mark scene for regeneration with optional prompt modifications"""
        scene_id = self._normalize_scene_id(intent.scope)

        # Extract modification parameters
        activity = intent.parameters.get("activity")
        reason = intent.parameters.get("reason")
        new_description = intent.parameters.get("description")

        for scene in state.scenes:
            if not scene_id or scene.id == scene_id:
                # Modify prompt if specific changes requested
                if activity:
                    # Replace activity/sport mentions in the prompt
                    # This is a simple replacement - could be made more sophisticated
                    scene.visual_prompt = f"Scene showing {activity}. " + scene.visual_prompt
                    scene.description = f"Scene showing {activity}"
                    print(f"   ✓ Updated scene activity to: {activity}")

                if new_description:
                    # Add custom description modification
                    scene.visual_prompt = new_description + "\n\n" + scene.visual_prompt
                    scene.description = new_description
                    print(f"   ✓ Updated scene description")

                # Clear existing assets to force regeneration
                scene.image_file = None
                scene.video_file = None
                print(f"   ✓ Marked {scene.id} for regeneration")

        state.phase_status["video"] = "needs_regeneration"
        return state

    def _regenerate_script(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Mark script for regeneration"""
        print("   ✓ Marked script for regeneration")
        state.phase_status["script"] = "needs_regeneration"
        return state

    def _change_script(self, intent: EditIntent, state: PipelineState) -> PipelineState:
        """Modify dialogue text or scene descriptions"""
        scene_id = self._normalize_scene_id(intent.scope)

        # Parameters for script modification
        new_text = intent.parameters.get("new_text")
        character_name = intent.parameters.get("character")
        tone_change = intent.parameters.get("tone")  # e.g., "more dramatic", "casual"

        modified_count = 0

        # If scope is a specific scene, modify that scene's dialogue/description
        if scene_id:
            for scene in state.scenes:
                if scene.id == scene_id:
                    # Modify scene description if new_text provided
                    if new_text and not character_name:
                        scene.description = new_text
                        print(f"   ✓ Updated description for {scene.id}")
                        modified_count += 1

                    # Modify specific character's dialogue in this scene
                    elif character_name:
                        for dialogue in scene.dialogue:
                            if dialogue.character == character_name:
                                if new_text:
                                    dialogue.text = new_text
                                    # Clear audio to force TTS regeneration
                                    dialogue.audio_file = None
                                    dialogue.duration_ms = None
                                    print(f"   ✓ Updated dialogue for {character_name} in {scene.id}")
                                    modified_count += 1

                    # Add tone instruction to all dialogue in scene
                    elif tone_change:
                        for dialogue in scene.dialogue:
                            dialogue.text = f"[{tone_change}] {dialogue.text}"
                            dialogue.audio_file = None
                            dialogue.duration_ms = None
                        print(f"   ✓ Applied tone '{tone_change}' to all dialogue in {scene.id}")
                        modified_count += len(scene.dialogue)

        # If no scene specified, apply to entire story
        else:
            if tone_change:
                for scene in state.scenes:
                    for dialogue in scene.dialogue:
                        if not dialogue.text.startswith(f"[{tone_change}]"):
                            dialogue.text = f"[{tone_change}] {dialogue.text}"
                            dialogue.audio_file = None
                            dialogue.duration_ms = None
                            modified_count += 1
                print(f"   ✓ Applied tone '{tone_change}' to all dialogue ({modified_count} lines)")

        if modified_count > 0:
            state.phase_status["audio"] = "needs_regeneration"
            state.phase_status["video"] = "needs_regeneration"
            print(f"   ✓ Modified {modified_count} script element(s)")
        else:
            print("   ⚠ No script elements were modified")

        return state

    def _full_regenerate(self, _: EditIntent, state: PipelineState) -> PipelineState:
        """Clear all generated assets and mark all phases for regeneration"""
        print("   🔄 Initiating full pipeline regeneration...")

        # Clear all scene assets
        cleared_assets = 0
        for scene in state.scenes:
            if scene.image_file:
                scene.image_file = None
                cleared_assets += 1
            if scene.video_file:
                scene.video_file = None
                cleared_assets += 1
            if scene.bgm_file:
                scene.bgm_file = None
                cleared_assets += 1

            # Clear dialogue audio
            for dialogue in scene.dialogue:
                if dialogue.audio_file:
                    dialogue.audio_file = None
                    dialogue.duration_ms = None
                    cleared_assets += 1

        # Clear final video
        if state.final_video_path:
            state.final_video_path = None
            cleared_assets += 1

        # Clear audio manifest
        if state.audio_manifest:
            state.audio_manifest = None

        # Mark all phases for regeneration
        state.phase_status["script"] = "needs_regeneration"
        state.phase_status["audio"] = "needs_regeneration"
        state.phase_status["video"] = "needs_regeneration"

        print(f"   ✓ Cleared {cleared_assets} asset(s)")
        print(f"   ✓ Marked all phases for regeneration")
        print(f"   ⚠ Next pipeline run will regenerate everything from scratch")

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
