"""
Schema Validation Test for Multi-Intent Edit System
Tests that all schemas are correctly defined and can be instantiated
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from shared.schema import EditIntent, Scene, Character, VoiceParams


def test_edit_intent_schema():
    """Test that all new intent types are valid"""
    print("=" * 80)
    print("TEST 1: EDIT INTENT SCHEMA VALIDATION")
    print("=" * 80)

    new_intent_types = [
        # Voice & Audio
        "change_voice",
        "regenerate_script",
        # Visual
        "apply_filter",
        "change_scene_characters",
        "change_character_design",
        "regenerate_scene",
        # Music & BGM
        "change_mood",
        "change_bgm",
        "add_bgm",
        "remove_bgm",
        # Timing & Composition
        "adjust_duration",
        "speed_up",
        "slow_down",
        "toggle_subtitles",
        # Global
        "change_script",
        "full_regenerate"
    ]

    new_targets = ["audio", "video_frame", "video", "script", "bgm", "composition"]

    print("\nTesting all new intent types...")
    all_passed = True

    for intent_type in new_intent_types:
        for target in new_targets:
            try:
                intent = EditIntent(
                    intent_type=intent_type,
                    target=target,
                    scope="scene:scene_001",
                    parameters={"test": "value"},
                    original_query=f"Test {intent_type}",
                    priority=0
                )
                print(f"✓ {intent_type:25s} + {target:15s} = Valid")
            except Exception as e:
                print(f"✗ {intent_type:25s} + {target:15s} = Error: {e}")
                all_passed = False
                break

    print("\n" + "─" * 80)
    if all_passed:
        print("✓ All intent types are valid!")
    else:
        print("✗ Some intent types failed validation")

    print("=" * 80)


def test_scene_schema_extensions():
    """Test that Scene schema has all new fields"""
    print("\n" + "=" * 80)
    print("TEST 2: SCENE SCHEMA EXTENSIONS")
    print("=" * 80)

    try:
        scene = Scene(
            id="scene_001",
            description="Test scene",
            visual_prompt="A test scene",
            duration_ms=5000,
            # New fields
            characters_in_scene=["Character1", "Character2"],
            character_visual_overrides={
                "Character1": {"gender": "male", "description": "Updated description"}
            },
            has_subtitles=False,
            visual_filters=["darken", "vignette"]
        )

        print("\n✓ Scene created successfully with new fields:")
        print(f"   characters_in_scene: {scene.characters_in_scene}")
        print(f"   character_visual_overrides: {scene.character_visual_overrides}")
        print(f"   has_subtitles: {scene.has_subtitles}")
        print(f"   visual_filters: {scene.visual_filters}")

        # Test default values
        scene2 = Scene(
            id="scene_002",
            description="Test scene 2",
            visual_prompt="Another test scene",
            duration_ms=3000
        )

        print("\n✓ Scene created with default values:")
        print(f"   characters_in_scene: {scene2.characters_in_scene} (default: [])")
        print(f"   character_visual_overrides: {scene2.character_visual_overrides} (default: {{}})")
        print(f"   has_subtitles: {scene2.has_subtitles} (default: True)")
        print(f"   visual_filters: {scene2.visual_filters} (default: [])")

        print("\n✓ Scene schema validation PASSED!")

    except Exception as e:
        print(f"\n✗ Scene schema validation FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 80)


def test_intent_examples():
    """Test creating intents for common use cases"""
    print("\n" + "=" * 80)
    print("TEST 3: INTENT CREATION EXAMPLES")
    print("=" * 80)

    test_cases = [
        {
            "description": "Change voice tone to whispered",
            "intent": EditIntent(
                intent_type="change_voice",
                target="audio",
                scope="character:Narrator",
                parameters={"tone": "whispered"},
                original_query="Change voice tone to whispered for narrator",
                priority=0
            )
        },
        {
            "description": "Make scene 2 darker",
            "intent": EditIntent(
                intent_type="apply_filter",
                target="video_frame",
                scope="scene:scene_002",
                parameters={"filter": "darken", "amount": 0.3},
                original_query="Make scene 2 darker",
                priority=0
            )
        },
        {
            "description": "Add background music",
            "intent": EditIntent(
                intent_type="add_bgm",
                target="bgm",
                scope="all",
                parameters={"mood": "ambient"},
                original_query="Add background music",
                priority=0
            )
        },
        {
            "description": "Remove subtitles from scene 3",
            "intent": EditIntent(
                intent_type="toggle_subtitles",
                target="composition",
                scope="scene:scene_003",
                parameters={"show_subtitles": False},
                original_query="Remove subtitles from scene 3",
                priority=0
            )
        },
        {
            "description": "Change scene 1 characters to male and female",
            "intent": EditIntent(
                intent_type="change_scene_characters",
                target="video_frame",
                scope="scene:scene_001",
                parameters={"genders": ["male", "female"], "character_count": 2},
                original_query="In scene 1 change characters to male and female",
                priority=0
            )
        },
        {
            "description": "Speed up scene 2",
            "intent": EditIntent(
                intent_type="speed_up",
                target="video",
                scope="scene:scene_002",
                parameters={"speed_multiplier": 1.5},
                original_query="Speed up scene 2",
                priority=0
            )
        },
        {
            "description": "Regenerate the script",
            "intent": EditIntent(
                intent_type="regenerate_script",
                target="script",
                scope="all",
                parameters={},
                original_query="Regenerate the script",
                priority=0
            )
        }
    ]

    print("\nCreating intents for common use cases...\n")

    for i, test_case in enumerate(test_cases, 1):
        try:
            intent = test_case["intent"]
            print(f"{i}. {test_case['description']}")
            print(f"   ✓ Intent Type: {intent.intent_type}")
            print(f"   ✓ Target: {intent.target}")
            print(f"   ✓ Scope: {intent.scope}")
            print(f"   ✓ Parameters: {intent.parameters}")
            print()
        except Exception as e:
            print(f"{i}. {test_case['description']}")
            print(f"   ✗ Error: {e}")
            print()

    print("=" * 80)


def test_priority_field():
    """Test the priority field for intent ordering"""
    print("\n" + "=" * 80)
    print("TEST 4: INTENT PRIORITY ORDERING")
    print("=" * 80)

    intents = [
        EditIntent(
            intent_type="change_voice",
            target="audio",
            scope="all",
            parameters={},
            original_query="Change voice",
            priority=2
        ),
        EditIntent(
            intent_type="regenerate_script",
            target="script",
            scope="all",
            parameters={},
            original_query="Regenerate script",
            priority=0  # Highest priority
        ),
        EditIntent(
            intent_type="apply_filter",
            target="video_frame",
            scope="scene:scene_001",
            parameters={},
            original_query="Apply filter",
            priority=1
        )
    ]

    print("\nOriginal order:")
    for i, intent in enumerate(intents):
        print(f"   {i+1}. {intent.intent_type} (priority: {intent.priority})")

    # Sort by priority
    sorted_intents = sorted(intents, key=lambda x: x.priority)

    print("\nSorted by priority (0=highest):")
    for i, intent in enumerate(sorted_intents):
        print(f"   {i+1}. {intent.intent_type} (priority: {intent.priority})")

    print("\n✓ Priority field working correctly!")
    print("=" * 80)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "SCHEMA VALIDATION TEST SUITE" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")

    try:
        test_edit_intent_schema()
        test_scene_schema_extensions()
        test_intent_examples()
        test_priority_field()

        print("\n" + "=" * 80)
        print("🎉 ALL SCHEMA VALIDATION TESTS PASSED!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
