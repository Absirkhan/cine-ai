"""
Visual Context Manager for maintaining continuity across scenes
Ensures consistent character appearance, settings, and visual style
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class CharacterAppearance:
    """Persistent visual attributes of a character"""
    name: str
    base_description: str  # From character profile

    # Extracted/locked visual attributes for consistency
    age: Optional[str] = None  # e.g., "young boy", "elderly man", "middle-aged woman"
    gender: Optional[str] = None
    build: Optional[str] = None  # e.g., "athletic", "slim", "stocky"
    hair: Optional[str] = None  # e.g., "short brown hair", "long red hair"
    clothing: Optional[str] = None  # e.g., "blue jersey", "formal suit"
    distinctive_features: Optional[str] = None  # e.g., "wears glasses", "has a scar"

    # Scene-specific overrides
    scene_specific_notes: Dict[str, str] = field(default_factory=dict)

    def get_consistent_description(self, scene_id: Optional[str] = None) -> str:
        """
        Generate a consistent character description for image generation

        Args:
            scene_id: Optional scene ID for scene-specific overrides

        Returns:
            Detailed character description with locked attributes
        """
        parts = [self.base_description]

        # Add locked attributes if available
        if self.age:
            parts.append(f"{self.age}")
        if self.build:
            parts.append(f"{self.build} build")
        if self.hair:
            parts.append(f"with {self.hair}")
        if self.clothing:
            parts.append(f"wearing {self.clothing}")
        if self.distinctive_features:
            parts.append(f"{self.distinctive_features}")

        # Add scene-specific notes if available
        if scene_id and scene_id in self.scene_specific_notes:
            parts.append(self.scene_specific_notes[scene_id])

        return ", ".join(parts)


@dataclass
class EnvironmentContext:
    """Persistent environmental/setting attributes"""
    location_type: Optional[str] = None  # e.g., "football field", "city street", "forest"
    time_of_day: Optional[str] = None  # e.g., "bright sunny day", "sunset", "night"
    weather: Optional[str] = None  # e.g., "clear sky", "rainy", "foggy"
    lighting_style: Optional[str] = None  # e.g., "natural sunlight", "dramatic shadows"
    color_palette: Optional[str] = None  # e.g., "warm earthy tones", "cool blues"

    # Scene-specific environment changes
    scene_environments: Dict[str, str] = field(default_factory=dict)

    def get_consistent_environment(self, scene_id: Optional[str] = None) -> str:
        """
        Generate consistent environment description

        Args:
            scene_id: Optional scene ID for scene-specific environment

        Returns:
            Environment description maintaining continuity
        """
        # Check for scene-specific environment
        if scene_id and scene_id in self.scene_environments:
            return self.scene_environments[scene_id]

        # Use global environment context
        parts = []
        if self.location_type:
            parts.append(self.location_type)
        if self.time_of_day:
            parts.append(f"during {self.time_of_day}")
        if self.weather:
            parts.append(f"{self.weather}")
        if self.lighting_style:
            parts.append(f"{self.lighting_style}")
        if self.color_palette:
            parts.append(f"{self.color_palette}")

        return ", ".join(parts) if parts else ""


class VisualContextManager:
    """
    Manages visual continuity across all scenes
    Maintains character appearances, environment settings, and overall visual style
    """

    def __init__(self):
        self.characters: Dict[str, CharacterAppearance] = {}
        self.environment = EnvironmentContext()
        self.overall_style: Optional[str] = None  # e.g., "cinematic", "animated", "photorealistic"
        self.aspect_ratio: str = "16:9"
        self.genre: str = "general"

        # Track what has been established in previous scenes
        self.scene_history: List[Dict[str, Any]] = []

    def initialize_from_characters(self, characters: List[Any], genre: str, tone: str, aspect: str):
        """
        Initialize visual context from character profiles and story metadata

        Args:
            characters: List of Character objects from schema
            genre: Story genre
            tone: Story tone
            aspect: Aspect ratio
        """
        self.genre = genre
        self.overall_style = tone
        self.aspect_ratio = aspect

        # Create character appearances from character profiles
        for char in characters:
            self.characters[char.name] = CharacterAppearance(
                name=char.name,
                base_description=char.visual_description
            )

    def extract_and_lock_character_attributes(
        self,
        character_name: str,
        scene_description: str,
        scene_id: str
    ):
        """
        Extract and lock character visual attributes from first scene appearance
        This ensures the character looks the same in subsequent scenes

        Args:
            character_name: Name of the character
            scene_description: Description of the scene
            scene_id: Scene identifier
        """
        if character_name not in self.characters:
            return

        char = self.characters[character_name]

        # Only lock attributes on first appearance (if not already locked)
        # This could be enhanced with LLM extraction, but for now we rely on base_description
        # In future iterations, could parse generated image or use LLM to extract from scene
        pass

    def extract_environment_context(self, scene_description: str, scene_id: str):
        """
        Extract and maintain environment context from scene descriptions

        Args:
            scene_description: Scene description text
            scene_id: Scene identifier
        """
        # Could be enhanced with LLM to extract environment details
        # For now, we'll track scene-specific environments
        self.environment.scene_environments[scene_id] = scene_description

    def build_context_prompt(
        self,
        scene_description: str,
        scene_id: str,
        characters_in_scene: List[str],
        previous_scene_id: Optional[str] = None
    ) -> str:
        """
        Build a context-aware prompt segment to prepend to visual prompts

        Args:
            scene_description: Current scene description
            scene_id: Current scene identifier
            characters_in_scene: List of character names in this scene
            previous_scene_id: ID of previous scene for continuity reference

        Returns:
            Context prompt to ensure visual continuity
        """
        context_parts = []

        # Add overall style continuity
        if self.overall_style:
            context_parts.append(f"Style: {self.overall_style} {self.genre}")

        # Add character continuity instructions
        if characters_in_scene:
            char_descriptions = []
            for char_name in characters_in_scene:
                if char_name in self.characters:
                    char_desc = self.characters[char_name].get_consistent_description(scene_id)
                    char_descriptions.append(f"{char_name}: {char_desc}")

            if char_descriptions:
                context_parts.append("Characters (MAINTAIN EXACT APPEARANCE):")
                context_parts.extend([f"  - {desc}" for desc in char_descriptions])

        # Add environment continuity
        env_desc = self.environment.get_consistent_environment(scene_id)
        if env_desc:
            context_parts.append(f"Environment: {env_desc}")

        # Add reference to previous scene for continuity
        if previous_scene_id and self.scene_history:
            # Find previous scene in history
            prev_scenes = [s for s in self.scene_history if s.get('scene_id') == previous_scene_id]
            if prev_scenes:
                prev_scene = prev_scenes[0]
                context_parts.append(
                    f"CONTINUITY NOTE: This scene follows immediately after the previous scene. "
                    f"Maintain consistent visual style, lighting, and character appearances from: "
                    f"{prev_scene.get('description', '')[:100]}"
                )

        return "\n".join(context_parts)

    def add_to_history(
        self,
        scene_id: str,
        description: str,
        visual_prompt: str,
        characters_in_scene: List[str],
        image_path: Optional[str] = None
    ):
        """
        Add scene to history for future reference

        Args:
            scene_id: Scene identifier
            description: Scene description
            visual_prompt: Generated visual prompt
            characters_in_scene: Characters in this scene
            image_path: Path to generated image (if available)
        """
        self.scene_history.append({
            'scene_id': scene_id,
            'description': description,
            'visual_prompt': visual_prompt,
            'characters': characters_in_scene,
            'image_path': image_path
        })

    def get_previous_scene_context(self, current_scene_index: int) -> Optional[Dict[str, Any]]:
        """
        Get context from previous scene

        Args:
            current_scene_index: Index of current scene (0-based)

        Returns:
            Previous scene context dict or None
        """
        if current_scene_index > 0 and len(self.scene_history) >= current_scene_index:
            return self.scene_history[current_scene_index - 1]
        return None

    def update_character_for_scene(
        self,
        character_name: str,
        scene_id: str,
        scene_specific_note: str
    ):
        """
        Add scene-specific character note (e.g., "wearing muddy clothes" after falling)

        Args:
            character_name: Character name
            scene_id: Scene ID
            scene_specific_note: Scene-specific modification
        """
        if character_name in self.characters:
            self.characters[character_name].scene_specific_notes[scene_id] = scene_specific_note

    def set_character_attribute(self, character_name: str, attribute: str, value: str):
        """
        Lock a specific character attribute for continuity

        Args:
            character_name: Character name
            attribute: Attribute name (age, hair, clothing, etc.)
            value: Attribute value
        """
        if character_name not in self.characters:
            return

        char = self.characters[character_name]
        if hasattr(char, attribute):
            setattr(char, attribute, value)

    def set_environment_attribute(self, attribute: str, value: str):
        """
        Set a global environment attribute

        Args:
            attribute: Attribute name
            value: Attribute value
        """
        if hasattr(self.environment, attribute):
            setattr(self.environment, attribute, value)
