"""
Intent Parser for Edit Commands
Uses LangGraph to classify user edit intentions
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
import re
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from shared.schema import EditIntent
import config


class IntentParser:
    """Parses natural language edit commands into structured intents"""

    def __init__(self):
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0.3,  # Lower temperature for more consistent parsing
        )

    def parse(self, edit_command: str) -> EditIntent:
        """
        Parse natural language edit command into structured intent

        Args:
            edit_command: User's edit command in natural language

        Returns:
            EditIntent with classified type, target, scope, and parameters
        """
        prompt = f"""You are an intent classifier for video editing commands. Parse the following edit command into a structured JSON format.

USER COMMAND: "{edit_command}"

Classify the command into one of these intent types:

VOICE & AUDIO:
- change_voice: Change character voice parameters (tone, speed, pitch)
- regenerate_script: Re-invoke LLM to regenerate story/script

VISUAL:
- apply_filter: Apply visual filter to scene/video (darken, brighten, blur, etc.)
- change_scene_characters: Change which characters appear in a scene or their genders
- change_character_design: Re-generate character with different visual description
- regenerate_scene: Regenerate a specific scene's visuals

MUSIC & BGM:
- change_mood: Change scene mood for BGM selection
- change_bgm: Change background music to specific track
- add_bgm: Add background music to a scene
- remove_bgm: Remove background music from a scene

TIMING & COMPOSITION:
- adjust_duration: Change scene or video duration
- speed_up: Increase playback speed of scene/video
- slow_down: Decrease playback speed of scene/video
- toggle_subtitles: Show/hide subtitle burn-in

GLOBAL:
- change_script: Modify dialogue or story text
- full_regenerate: Regenerate entire video from scratch

Identify the target:
- audio: Targets TTS or voice synthesis
- video_frame: Targets single scene image/video
- video: Targets entire video composition
- script: Targets story/dialogue
- bgm: Targets background music
- composition: Targets video composition/rendering settings

Extract scope if mentioned:
- character:Name (e.g., "character:Narrator")
- scene:ID (e.g., "scene:scene_001", "scene:scene_002") - Use EXACT scene numbers from command
- all (applies to all scenes/characters)

Extract parameters as key-value pairs. Common parameters:
- tone, speed, pitch (for voice)
- filter, amount (for visual filters)
- mood (for BGM)
- duration_ms (for duration)
- genders (e.g., ["male", "female"])
- character_count (number of characters)
- speed_multiplier (for speed changes)

Respond with ONLY a JSON object in this exact format:
{{
  "intent_type": "...",
  "target": "...",
  "scope": "...",
  "parameters": {{...}},
  "priority": 0
}}

Examples:

Input: "Change voice tone to whispered for the narrator"
Output: {{"intent_type": "change_voice", "target": "audio", "scope": "character:Narrator", "parameters": {{"tone": "whispered"}}, "priority": 0}}

Input: "Make scene 2 darker"
Output: {{"intent_type": "apply_filter", "target": "video_frame", "scope": "scene:scene_002", "parameters": {{"filter": "darken", "amount": 0.3}}, "priority": 0}}

Input: "Add background music"
Output: {{"intent_type": "add_bgm", "target": "bgm", "scope": "all", "parameters": {{"mood": "ambient"}}, "priority": 0}}

Input: "Remove the subtitle from scene 3"
Output: {{"intent_type": "toggle_subtitles", "target": "composition", "scope": "scene:scene_003", "parameters": {{"show_subtitles": false}}, "priority": 0}}

Input: "In scene 1 change characters to male and female"
Output: {{"intent_type": "change_scene_characters", "target": "video_frame", "scope": "scene:scene_001", "parameters": {{"genders": ["male", "female"], "character_count": 2}}, "priority": 0}}

Input: "Speed up scene 2"
Output: {{"intent_type": "speed_up", "target": "video", "scope": "scene:scene_002", "parameters": {{"speed_multiplier": 1.5}}, "priority": 0}}

Input: "Regenerate the script"
Output: {{"intent_type": "regenerate_script", "target": "script", "scope": "all", "parameters": {{}}, "priority": 0}}

Input: "In scene 3, they are playing basketball not football"
Output: {{"intent_type": "regenerate_scene", "target": "video_frame", "scope": "scene:scene_003", "parameters": {{"activity": "basketball", "reason": "change activity from football to basketball"}}, "priority": 0}}

Input: "Change the narration text in scene 2 to be more dramatic"
Output: {{"intent_type": "change_script", "target": "script", "scope": "scene:scene_002", "parameters": {{"tone": "dramatic"}}, "priority": 0}}

IMPORTANT DISTINCTION:
- Use "regenerate_scene" when the visual content/activity needs to change (e.g., different sport, different action, different setting)
- Use "change_script" only when modifying narration/dialogue text WITHOUT changing visuals

Now parse the user command above."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        result_text = response.content.strip()

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
        else:
            # Fallback: treat as general edit
            result = {
                "intent_type": "change_script",
                "target": "script",
                "scope": None,
                "parameters": {"description": edit_command}
            }

        # Create EditIntent object
        intent = EditIntent(
            intent_type=result.get("intent_type", "change_script"),
            target=result.get("target", "script"),
            scope=result.get("scope"),
            parameters=result.get("parameters", {}),
            original_query=edit_command
        )

        return intent

    def parse_multiple(self, edit_commands: List[str]) -> List[EditIntent]:
        """
        Parse multiple edit commands into structured intents

        Args:
            edit_commands: List of user edit commands

        Returns:
            List of EditIntent objects
        """
        intents = []
        for cmd in edit_commands:
            intent = self.parse(cmd)
            intents.append(intent)
        return intents

    def get_scene_id_from_scope(self, scope: str) -> str:
        """Extract scene ID from scope string"""
        if scope and scope.startswith("scene:"):
            return scope.split(":")[1]
        return None

    def get_character_name_from_scope(self, scope: str) -> str:
        """Extract character name from scope string"""
        if scope and scope.startswith("character:"):
            return scope.split(":")[1]
        return None
