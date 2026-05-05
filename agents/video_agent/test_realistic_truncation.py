"""
Test Realistic Prompt Truncation Scenarios
Tests real-world prompts from the visual continuity system
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from phase3_video.image_generator import ImageGenerator


def test_football_scene_continuity():
    """Test a realistic multi-scene football scenario"""
    print("\n" + "=" * 80)
    print("Test: Realistic Football Scene with Continuity")
    print("=" * 80)

    gen = ImageGenerator()

    # This is what the visual context manager would generate
    scene1_prompt = (
        "Cinematic shot of a young boy playing football on a sunny outdoor field, "
        "energetic sports photography style, wide angle view showing the action"
    )

    scene2_prompt = (
        "Style: Cinematic Sports Drama\n"
        "Characters (MAINTAIN EXACT APPEARANCE):\n"
        "  - Alex: A young boy with short brown hair, wearing a blue football jersey with number 10\n"
        "Scene showing the same young boy celebrating after scoring a goal, arms raised in triumph. "
        "Maintain consistent visual style, lighting, and character appearance from previous scene. "
        "Same outdoor football field setting with sunny weather and green grass."
    )

    print("\n--- SCENE 1 (First appearance) ---")
    print(f"Original: {scene1_prompt}")
    print(f"Length: {len(scene1_prompt)} chars, {len(scene1_prompt.split())} words")
    result1 = gen._truncate_prompt(scene1_prompt)
    print(f"\nResult: {result1}")

    print("\n--- SCENE 2 (With continuity) ---")
    print(f"Original: {scene2_prompt}")
    print(f"Length: {len(scene2_prompt)} chars, {len(scene2_prompt.split())} words")
    result2 = gen._truncate_prompt(scene2_prompt)
    print(f"\nResult: {result2}")

    # Verify scene 2 has character info
    assert "boy" in result2.lower(), "Character should be preserved"
    assert "blue" in result2.lower() or "jersey" in result2.lower(), "Character details should be preserved"

    # Verify scene 2 has action
    assert "celebrating" in result2.lower() or "scoring" in result2.lower() or "goal" in result2.lower(), \
        "Scene action should be preserved"

    print("\n[PASS] Football scene continuity preserved correctly")


def test_character_aging_issue():
    """Test the specific issue: boy in scene 1, man in scene 2"""
    print("\n" + "=" * 80)
    print("Test: Character Age Consistency (Boy -> Boy, not Boy -> Man)")
    print("=" * 80)

    gen = ImageGenerator()

    # Scene 1: Establish character as young boy
    scene1 = (
        "Style: Cinematic\n"
        "A young boy with short brown hair playing football on a sunny field, "
        "wearing a blue jersey, athletic and energetic"
    )

    # Scene 2: MUST maintain "young boy" not become "man"
    scene2 = (
        "Style: Cinematic\n"
        "Characters (MAINTAIN EXACT APPEARANCE):\n"
        "  - Alex: young boy (NOT man, NOT adult), short brown hair, blue football jersey\n"
        "Scene showing the young boy celebrating after scoring. "
        "CRITICAL: Character must remain a YOUNG BOY, same age as previous scene."
    )

    print("\nScene 1:")
    result1 = gen._truncate_prompt(scene1)
    print(result1)

    print("\nScene 2:")
    result2 = gen._truncate_prompt(scene2)
    print(result2)

    # Critical check: ensure "young boy" is in result, not just "boy" or "man"
    assert "young boy" in result2.lower() or ("boy" in result2.lower() and "man" not in result2.lower()), \
        "Character age must be preserved as 'young boy'"

    print("\n[PASS] Character age consistency maintained")


def test_environment_continuity():
    """Test that environment details are preserved across scenes"""
    print("\n" + "=" * 80)
    print("Test: Environment Continuity (Same Location)")
    print("=" * 80)

    gen = ImageGenerator()

    scene_with_environment = (
        "Style: Cinematic\n"
        "Characters (MAINTAIN EXACT APPEARANCE):\n"
        "  - Sarah: young woman with long blonde hair, wearing red jacket\n"
        "Scene showing Sarah walking through a foggy forest path at dusk. "
        "Environment: dense pine forest, misty atmosphere, dim evening light filtering through trees. "
        "CONTINUITY: Same forest location as previous scene, maintain foggy atmosphere and lighting."
    )

    print(f"\nOriginal ({len(scene_with_environment)} chars):")
    print(scene_with_environment)

    result = gen._truncate_prompt(scene_with_environment)

    print(f"\nTruncated ({len(result)} chars):")
    print(result)

    # Check character preserved
    assert "sarah" in result.lower() or "woman" in result.lower(), "Character should be preserved"

    # Check scene action preserved
    assert "walking" in result.lower() or "forest" in result.lower(), "Scene action/location should be preserved"

    print("\n[PASS] Environment continuity preserved")


if __name__ == "__main__":
    try:
        test_football_scene_continuity()
        test_character_aging_issue()
        test_environment_continuity()

        print("\n" + "=" * 80)
        print("[PASS] ALL REALISTIC TRUNCATION TESTS PASSED")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("- Character descriptions are preserved with exact details")
        print("- Scene actions (playing, celebrating, walking) are maintained")
        print("- Character ages stay consistent (boy stays boy, not becoming man)")
        print("- Environment and continuity notes are included when possible")
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
