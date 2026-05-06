"""
Test Visual Continuity Manager
Validates that visual context is properly maintained across scenes
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from visual_context import VisualContextManager, CharacterAppearance
from shared.schema import Character, VoiceParams


def test_character_appearance_consistency():
    """Test that character appearances are tracked and consistent"""
    print("\n" + "=" * 80)
    print("Testing Character Appearance Consistency")
    print("=" * 80)

    # Create character appearance
    char = CharacterAppearance(
        name="Alex",
        base_description="A young person playing football",
        age="young boy",
        hair="short brown hair",
        clothing="blue football jersey"
    )

    # Get consistent description
    desc1 = char.get_consistent_description()
    print(f"\nScene 1 Description:\n{desc1}")

    # Add scene-specific note
    char.scene_specific_notes["scene_002"] = "covered in mud from the game"

    # Get scene-specific description
    desc2 = char.get_consistent_description("scene_002")
    print(f"\nScene 2 Description (with mud):\n{desc2}")

    # Verify consistency
    assert "young boy" in desc1, "Age should be in description"
    assert "young boy" in desc2, "Age should persist in scene 2"
    assert "blue football jersey" in desc1, "Clothing should be consistent"
    assert "blue football jersey" in desc2, "Clothing should persist"
    assert "mud" in desc2, "Scene-specific note should appear"
    assert "mud" not in desc1, "Scene-specific note should not affect earlier scenes"

    print("\n[PASS] Character appearance consistency test PASSED")


def test_visual_context_manager():
    """Test the full visual context manager workflow"""
    print("\n" + "=" * 80)
    print("Testing Visual Context Manager")
    print("=" * 80)

    # Create mock characters
    characters = [
        Character(
            name="Alex",
            role="protagonist",
            voice_params=VoiceParams(gender="male", tone="energetic"),
            visual_description="A young boy with short brown hair, wearing a blue football jersey"
        ),
        Character(
            name="Coach",
            role="supporting",
            voice_params=VoiceParams(gender="male", tone="authoritative"),
            visual_description="A middle-aged man with grey hair and a coaching uniform"
        )
    ]

    # Initialize context manager
    context_manager = VisualContextManager()
    context_manager.initialize_from_characters(
        characters=characters,
        genre="Sports Drama",
        tone="Cinematic",
        aspect="16:9"
    )

    print("\n[OK] Context manager initialized")
    print(f"  Characters tracked: {list(context_manager.characters.keys())}")

    # Test scene 1 context
    scene1_context = context_manager.build_context_prompt(
        scene_description="Alex playing football on a sunny field",
        scene_id="scene_000",
        characters_in_scene=["Alex"],
        previous_scene_id=None
    )

    print(f"\nScene 1 Context Prompt:\n{scene1_context}")
    assert "Alex" in scene1_context, "Character should be in context"
    assert "Cinematic" in scene1_context or "Sports Drama" in scene1_context, "Style should be in context"

    # Add scene 1 to history
    context_manager.add_to_history(
        scene_id="scene_000",
        description="Alex playing football on a sunny field",
        visual_prompt="Cinematic shot of a young boy with brown hair...",
        characters_in_scene=["Alex"]
    )

    print("\n[OK] Scene 1 added to history")

    # Test scene 2 context with continuity
    scene2_context = context_manager.build_context_prompt(
        scene_description="Alex celebrating after scoring a goal",
        scene_id="scene_001",
        characters_in_scene=["Alex", "Coach"],
        previous_scene_id="scene_000"
    )

    print(f"\nScene 2 Context Prompt (with continuity):\n{scene2_context}")
    assert "CONTINUITY" in scene2_context or "previous scene" in scene2_context.lower(), \
        "Should reference previous scene for continuity"
    assert "Alex" in scene2_context, "Alex should be in context"
    assert "Coach" in scene2_context, "Coach should be in context"

    # Verify history
    assert len(context_manager.scene_history) == 1, "Should have 1 scene in history"
    prev_context = context_manager.get_previous_scene_context(1)
    assert prev_context is not None, "Should retrieve previous scene context"
    assert prev_context['scene_id'] == "scene_000", "Previous scene should be scene_000"

    print("\n[PASS] Visual Context Manager test PASSED")


def test_character_attribute_locking():
    """Test that we can lock character attributes for consistency"""
    print("\n" + "=" * 80)
    print("Testing Character Attribute Locking")
    print("=" * 80)

    context_manager = VisualContextManager()

    # Create a character
    character = Character(
        name="Samantha",
        role="protagonist",
        voice_params=VoiceParams(gender="female", tone="calm"),
        visual_description="A young woman"
    )

    context_manager.initialize_from_characters(
        characters=[character],
        genre="Drama",
        tone="Realistic",
        aspect="16:9"
    )

    # Lock specific attributes based on first generation
    context_manager.set_character_attribute("Samantha", "age", "young woman in her 20s")
    context_manager.set_character_attribute("Samantha", "hair", "long blonde hair")
    context_manager.set_character_attribute("Samantha", "clothing", "casual jeans and white t-shirt")

    # Get description
    desc = context_manager.characters["Samantha"].get_consistent_description()
    print(f"\nLocked Character Description:\n{desc}")

    assert "young woman in her 20s" in desc, "Locked age should appear"
    assert "long blonde hair" in desc, "Locked hair should appear"
    assert "casual jeans and white t-shirt" in desc, "Locked clothing should appear"

    print("\n[PASS] Character attribute locking test PASSED")


if __name__ == "__main__":
    try:
        test_character_appearance_consistency()
        test_visual_context_manager()
        test_character_attribute_locking()

        print("\n" + "=" * 80)
        print("[PASS] ALL VISUAL CONTINUITY TESTS PASSED")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
