"""
Test Prompt Truncation for Free-Tier Limits
Validates that prompts are intelligently shortened while preserving key information
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from phase3_video.image_generator import ImageGenerator


def test_short_prompt_unchanged():
    """Test that short prompts are not modified"""
    print("\n" + "=" * 80)
    print("Test: Short Prompt Unchanged")
    print("=" * 80)

    gen = ImageGenerator()

    short_prompt = "A young boy playing football on a sunny field"
    result = gen._truncate_prompt(short_prompt)

    print(f"\nOriginal: {short_prompt}")
    print(f"Result: {result}")

    assert result == short_prompt, "Short prompt should not be modified"
    print("\n[PASS] Short prompt remains unchanged")


def test_long_prompt_truncated():
    """Test that overly long prompts are truncated"""
    print("\n" + "=" * 80)
    print("Test: Long Prompt Truncation")
    print("=" * 80)

    gen = ImageGenerator()

    # Create a very long prompt
    long_prompt = (
        "Style: Cinematic Sports Drama\n"
        "Characters (MAINTAIN EXACT APPEARANCE):\n"
        "  - Alex: A young boy with short brown hair, wearing a blue football jersey, number 10, athletic build\n"
        "  - Coach: A middle-aged man with grey hair, wearing a red coaching uniform with whistle\n"
        "Scene showing a young boy playing football on a bright sunny field with green grass. "
        "The scene is shot in cinematic widescreen format with dramatic lighting. "
        "The atmosphere is energetic and upbeat with warm golden hour lighting. "
        "In the background, there are stadium bleachers with spectators cheering. "
        "The composition follows the rule of thirds with the main subject positioned on the left. "
        "Additional details include: white goalposts, colorful team banners, a clear blue sky with few clouds, "
        "and dynamic motion blur to convey movement and action. "
        "The overall color palette consists of vibrant greens, blues, and warm golden tones. "
        "Camera angle is low and dynamic, capturing the intensity of the moment."
    )

    print(f"\nOriginal length: {len(long_prompt)} chars, {len(long_prompt.split())} words")

    result = gen._truncate_prompt(long_prompt)

    print(f"Truncated length: {len(result)} chars, {len(result.split())} words")
    print(f"\nTruncated prompt:\n{result}")

    # Verify truncation
    assert len(result) <= gen.max_prompt_length, f"Result should be <= {gen.max_prompt_length} chars"
    assert len(result.split()) <= gen.max_words, f"Result should be <= {gen.max_words} words"

    # Verify key information preserved
    assert "Alex" in result or "boy" in result, "Character information should be preserved"
    assert any(word in result.lower() for word in ["football", "playing", "field"]), "Main scene action should be preserved"

    print("\n[PASS] Long prompt truncated correctly")


def test_character_priority():
    """Test that character descriptions are prioritized in truncation"""
    print("\n" + "=" * 80)
    print("Test: Character Description Priority")
    print("=" * 80)

    gen = ImageGenerator()

    prompt_with_characters = (
        "A detailed atmospheric scene with complex lighting effects and intricate background details. "
        "Character: A young boy with short brown hair wearing a blue football jersey. "
        "The environment features lush green grass, stadium lights creating dramatic shadows, "
        "and a crowd of spectators in the distance. The weather is sunny with scattered clouds. "
        "Additional environmental details include goalposts, team banners, and various equipment scattered around. "
        "The cinematography uses advanced techniques including depth of field, motion blur, and color grading. "
        "The overall mood is energetic and triumphant with warm golden tones throughout the composition."
    )

    result = gen._truncate_prompt(prompt_with_characters)

    print(f"\nOriginal length: {len(prompt_with_characters)} chars")
    print(f"Truncated length: {len(result)} chars")
    print(f"\nTruncated prompt:\n{result}")

    # Character info should be preserved
    assert "boy" in result.lower(), "Character description should be preserved"
    assert "blue" in result.lower() or "jersey" in result.lower(), "Character clothing should be preserved"

    print("\n[PASS] Character descriptions prioritized correctly")


def test_continuity_preservation():
    """Test that continuity instructions are preserved"""
    print("\n" + "=" * 80)
    print("Test: Continuity Instruction Preservation")
    print("=" * 80)

    gen = ImageGenerator()

    prompt_with_continuity = (
        "Style: Cinematic\n"
        "Characters (MAINTAIN EXACT APPEARANCE):\n"
        "  - Alex: young boy, short brown hair, blue jersey\n"
        "Scene showing celebration after scoring goal. "
        "Very detailed background with many elements including crowd, lights, grass, equipment. "
        "Lots of atmospheric effects and complex lighting setups. "
        "Multiple layers of detail that are not critical to the main scene. "
        "CONTINUITY: Maintain exact visual style, character appearances, and environment consistency with previous scene."
    )

    result = gen._truncate_prompt(prompt_with_continuity)

    print(f"\nOriginal length: {len(prompt_with_continuity)} chars, {len(prompt_with_continuity.split())} words")
    print(f"Truncated length: {len(result)} chars, {len(result.split())} words")
    print(f"\nTruncated prompt:\n{result}")

    # Check for continuity-related content
    assert "maintain" in result.lower() or "exact" in result.lower() or "character" in result.lower(), \
        "Continuity instructions should be preserved"

    print("\n[PASS] Continuity instructions preserved")


if __name__ == "__main__":
    try:
        test_short_prompt_unchanged()
        test_long_prompt_truncated()
        test_character_priority()
        test_continuity_preservation()

        print("\n" + "=" * 80)
        print("[PASS] ALL PROMPT TRUNCATION TESTS PASSED")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
