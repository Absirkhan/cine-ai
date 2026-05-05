"""
Phase 1: Story & Script Generation Agent
Uses LangGraph with Groq LLaMA for multi-step story creation
"""

import json
import re
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.schema import Story, Scene, Character, Dialogue, VoiceParams, MoodType, PipelineState
from shared.utils import generate_scene_id, parse_duration
import config
from .prompts import (
    STORY_GENERATION_PROMPT,
    CHARACTER_GENERATION_PROMPT,
    DIALOGUE_GENERATION_PROMPT,
    VISUAL_PROMPT_GENERATION,
    MOOD_CLASSIFICATION_PROMPT
)


class StoryAgent:
    """LangGraph-based agent for story generation"""

    def __init__(self):
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0.7,
        )

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""

        # Define state schema
        workflow = StateGraph(dict)

        # Add nodes (agent steps)
        workflow.add_node("generate_story", self._generate_story)
        workflow.add_node("generate_characters", self._generate_characters)
        workflow.add_node("generate_dialogue", self._generate_dialogue)
        workflow.add_node("generate_visuals", self._generate_visual_prompts)
        workflow.add_node("validate", self._validate_output)

        # Define edges (flow)
        workflow.set_entry_point("generate_story")
        workflow.add_edge("generate_story", "generate_characters")
        workflow.add_edge("generate_characters", "generate_dialogue")
        workflow.add_edge("generate_dialogue", "generate_visuals")
        workflow.add_edge("generate_visuals", "validate")
        workflow.add_edge("validate", END)

        return workflow.compile()

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response (handles markdown code blocks)"""
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError(f"No JSON found in response: {text[:200]}")

        return json.loads(json_str)

    def _generate_story(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate story structure and scenes"""
        user_input = state["user_input"]
        params = state["params"]

        prompt = STORY_GENERATION_PROMPT.format(
            user_prompt=user_input,
            genre=params.get("genre", "Sci-Fi"),
            tone=params.get("tone", "Cinematic"),
            duration=params.get("duration", "60s"),
            aspect_ratio=params.get("aspect", "16:9")
        )

        response = self.llm.invoke([HumanMessage(content=prompt)])
        result = self._extract_json(response.content)

        # Convert to our schema
        total_duration_ms = parse_duration(params.get("duration", "60s"))

        story = Story(
            title=result["title"],
            summary=result["summary"],
            genre=params.get("genre", "Sci-Fi"),
            tone=params.get("tone", "Cinematic"),
            total_duration_ms=total_duration_ms
        )

        # Create scene objects
        scenes = []
        for idx, scene_data in enumerate(result["scenes"]):
            # Validate and map mood to valid MoodType
            raw_mood = scene_data.get("mood", "ambient").lower()

            # Map invalid moods to valid ones
            mood_mapping = {
                "playful": "upbeat",
                "happy": "upbeat",
                "cheerful": "upbeat",
                "scary": "tense",
                "suspenseful": "mysterious",
                "melancholic": "sad",
                "somber": "sad",
                "peaceful": "calm",
                "serene": "calm",
                "ambient": "calm",
                "intense": "dramatic",
                "exciting": "dramatic",
                "action": "dramatic",
            }

            # Use mapping if mood is invalid, otherwise use the mood directly
            if raw_mood not in [m.value for m in MoodType]:
                mapped_mood = mood_mapping.get(raw_mood, "calm")
                print(f"⚠ Mapped invalid mood '{raw_mood}' to '{mapped_mood}'")
                mood = MoodType(mapped_mood)
            else:
                mood = MoodType(raw_mood)

            scene = Scene(
                id=generate_scene_id(idx),
                description=scene_data["description"],
                mood=mood,
                duration_ms=int(scene_data.get("duration_s", 15) * 1000),
                visual_prompt="",  # Will be generated later
                dialogue=[]  # Will be generated later
            )
            scenes.append(scene)

        state["story"] = story
        state["scenes"] = scenes
        state["progress"] = "Story structure created"

        return state

    def _generate_characters(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate character profiles"""
        story = state["story"]
        scenes = state["scenes"]

        scenes_summary = "\n".join([
            f"Scene {i+1}: {scene.description}"
            for i, scene in enumerate(scenes)
        ])

        prompt = CHARACTER_GENERATION_PROMPT.format(
            story_summary=story.summary,
            scenes_summary=scenes_summary
        )

        response = self.llm.invoke([HumanMessage(content=prompt)])
        result = self._extract_json(response.content)

        # Convert to our schema
        characters = []
        for char_data in result["characters"]:
            character = Character(
                name=char_data["name"],
                role=char_data["role"],
                voice_params=VoiceParams(
                    gender=char_data.get("voice_gender", "neutral"),
                    tone=char_data.get("voice_tone", "calm"),
                    accent=char_data.get("voice_accent"),
                    speed=1.0,
                    pitch=1.0
                ),
                visual_description=char_data["visual_description"]
            )
            characters.append(character)

        state["characters"] = characters
        state["progress"] = "Characters created"

        return state

    def _generate_dialogue(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dialogue for each scene"""
        scenes = state["scenes"]
        characters = state["characters"]

        characters_list = "\n".join([
            f"- {char.name} ({char.role})"
            for char in characters
        ])

        # Generate dialogue for each scene
        for scene in scenes:
            prompt = DIALOGUE_GENERATION_PROMPT.format(
                scene_description=scene.description,
                characters_list=characters_list,
                mood=scene.mood.value,
                duration_s=scene.duration_ms / 1000
            )

            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = self._extract_json(response.content)

            # Convert to dialogue objects
            dialogue_list = []
            for dialogue_data in result["dialogue"]:
                dialogue = Dialogue(
                    character=dialogue_data["character"],
                    text=dialogue_data["text"]
                )
                dialogue_list.append(dialogue)

            scene.dialogue = dialogue_list

        state["scenes"] = scenes
        state["progress"] = "Dialogue generated"

        return state

    def _generate_visual_prompts(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visual prompts for each scene"""
        scenes = state["scenes"]
        params = state["params"]

        for scene in scenes:
            prompt = VISUAL_PROMPT_GENERATION.format(
                scene_description=scene.description,
                genre=params.get("genre", "Sci-Fi"),
                tone=params.get("tone", "Cinematic"),
                aspect_ratio=params.get("aspect", "16:9")
            )

            response = self.llm.invoke([HumanMessage(content=prompt)])
            scene.visual_prompt = response.content.strip()

        state["scenes"] = scenes
        state["progress"] = "Visual prompts created"

        return state

    def _validate_output(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated output"""
        # Basic validation
        assert state.get("story"), "Story is missing"
        assert state.get("scenes"), "Scenes are missing"
        assert state.get("characters"), "Characters are missing"

        for scene in state["scenes"]:
            assert scene.dialogue, f"Scene {scene.id} has no dialogue"
            assert scene.visual_prompt, f"Scene {scene.id} has no visual prompt"

        state["progress"] = "Validation complete"
        state["status"] = "complete"

        return state

    def generate(self, user_prompt: str, params: Dict[str, Any], run_id: str = None) -> PipelineState:
        """
        Generate complete story, characters, and script

        Args:
            user_prompt: User's story idea
            params: Generation parameters (genre, tone, duration, aspect)
            run_id: Optional run ID (will generate if not provided)

        Returns:
            PipelineState with populated story, scenes, and characters
        """
        from shared.utils import generate_run_id
        from datetime import datetime

        # Initialize state with provided or generated run_id
        if run_id is None:
            run_id = generate_run_id()

        initial_state = {
            "user_input": user_prompt,
            "params": params,
            "run_id": run_id
        }

        # Run the workflow
        result = self.workflow.invoke(initial_state)

        # Build PipelineState
        pipeline_state = PipelineState(
            run_id=run_id,
            version=1,
            timestamp=datetime.utcnow().isoformat(),
            user_prompt=user_prompt,
            user_params=params,
            story=result["story"],
            scenes=result["scenes"],
            characters=result["characters"],
            phase_status={
                "script": "complete",
                "audio": "pending",
                "video": "pending",
                "web": "pending",
                "edit": "pending"
            }
        )

        return pipeline_state
