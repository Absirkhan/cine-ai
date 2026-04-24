"""
Intent Parser for Edit Commands
Uses LangGraph to classify user edit intentions
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
import re
from typing import Dict, Any
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
- change_voice: Change character voice parameters (tone, speed, pitch)
- change_mood: Change scene mood for BGM selection
- change_bgm: Change background music
- regenerate_scene: Regenerate a specific scene
- adjust_duration: Change scene or video duration
- apply_filter: Apply visual filter to scene/video
- change_script: Modify dialogue or story
- full_regenerate: Regenerate entire video

Identify the target:
- audio: Targets TTS or voice synthesis
- video_frame: Targets single scene image/video
- video: Targets entire video composition
- script: Targets story/dialogue
- bgm: Targets background music

Extract scope if mentioned:
- character:Name (e.g., "character:Narrator")
- scene:ID (e.g., "scene:scene_001")
- all (applies to all scenes/characters)

Extract parameters as key-value pairs.

Respond with ONLY a JSON object in this exact format:
{{
  "intent_type": "change_voice|change_mood|change_bgm|regenerate_scene|adjust_duration|apply_filter|change_script|full_regenerate",
  "target": "audio|video_frame|video|script|bgm",
  "scope": "character:Name|scene:ID|all|null",
  "parameters": {{"key": "value"}}
}}

Examples:

Input: "Change voice tone to whispered for the narrator"
Output: {{"intent_type": "change_voice", "target": "audio", "scope": "character:Narrator", "parameters": {{"tone": "whispered"}}}}

Input: "Make scene 2 darker"
Output: {{"intent_type": "apply_filter", "target": "video_frame", "scope": "scene:scene_002", "parameters": {{"filter": "darken", "amount": 0.3}}}}

Input: "Change background music to tense"
Output: {{"intent_type": "change_mood", "target": "bgm", "scope": "all", "parameters": {{"mood": "tense"}}}}

Input: "Regenerate the entire video"
Output: {{"intent_type": "full_regenerate", "target": "video", "scope": "all", "parameters": {{}}}}

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
