"""
Test Script for Multi-Intent Edit System
Tests all the query types mentioned in requirements
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from intent_decomposer import IntentDecomposer
from intent_parser import IntentParser


def test_decomposer():
    """Test intent decomposition"""
    print("=" * 80)
    print("TEST 1: INTENT DECOMPOSER")
    print("=" * 80)

    decomposer = IntentDecomposer()

    test_commands = [
        # Simple commands (should NOT be decomposed)
        "Change voice tone to whispered",
        "Make the scene darker",
        "Add background music",

        # Multi-part commands (SHOULD be decomposed)
        "Make scene 1 darker and scene 3 brighter",
        "Change narrator's voice to whispered and add background music",
        "In scene 1 change characters to male and female, keep scene 2 same, in scene 3 also male and female, only one female in scene 4",
        "Remove subtitles from scene 2 and speed up scene 3",
        "Speed up scene 1, then make scene 2 darker, finally regenerate scene 3"
    ]

    for cmd in test_commands:
        print(f"\n📝 Input: {cmd}")
        decomposed = decomposer.decompose(cmd)
        print(f"✂️  Decomposed into {len(decomposed)} command(s):")
        for i, sub_cmd in enumerate(decomposed, 1):
            print(f"   {i}. {sub_cmd}")

    print("\n" + "=" * 80)


def test_parser():
    """Test intent parsing for all new intent types"""
    print("\n" + "=" * 80)
    print("TEST 2: INTENT PARSER (All Query Types)")
    print("=" * 80)

    parser = IntentParser()

    test_queries = {
        "Voice & Audio": [
            "Change voice tone to whispered",
            "Change narrator's voice to energetic with speed 1.2",
            "Regenerate the script"
        ],
        "Visual": [
            "Make the scene darker",
            "Apply blur filter to scene 2",
            "In scene 1 change characters to male and female",
            "Change character design for narrator",
            "Regenerate scene 3"
        ],
        "Music & BGM": [
            "Add background music",
            "Change background music to tense",
            "Remove BGM from scene 2",
            "Change mood to dramatic"
        ],
        "Timing & Composition": [
            "Remove the subtitle from scene 1",
            "Speed up scene 2",
            "Slow down this scene",
            "Adjust duration to 5000ms"
        ],
        "Global": [
            "Regenerate the entire video"
        ]
    }

    for category, queries in test_queries.items():
        print(f"\n{'─' * 80}")
        print(f"Category: {category}")
        print('─' * 80)

        for query in queries:
            print(f"\n📝 Query: \"{query}\"")
            try:
                intent = parser.parse(query)
                print(f"✓ Parsed Intent:")
                print(f"   Type: {intent.intent_type}")
                print(f"   Target: {intent.target}")
                print(f"   Scope: {intent.scope or 'all'}")
                print(f"   Parameters: {intent.parameters}")
            except Exception as e:
                print(f"✗ Error: {e}")

    print("\n" + "=" * 80)


def test_complex_multi_part():
    """Test the exact example from requirements"""
    print("\n" + "=" * 80)
    print("TEST 3: COMPLEX MULTI-PART QUERY (Your Example)")
    print("=" * 80)

    complex_query = "In the first scene, two males can be seen however the voice is of one girl and one boy, so change the first to male and female, keep second scene same, and third scene also as both male and female, only one female is seen in last scene."

    print(f"\n📝 Complex Query:")
    print(f"   \"{complex_query}\"")

    # Step 1: Decompose
    decomposer = IntentDecomposer()
    print(f"\n✂️  Step 1: Decomposition")
    sub_commands = decomposer.decompose(complex_query)
    print(f"   Decomposed into {len(sub_commands)} sub-command(s):")
    for i, cmd in enumerate(sub_commands, 1):
        print(f"   {i}. {cmd}")

    # Step 2: Parse each
    parser = IntentParser()
    print(f"\n📋 Step 2: Intent Parsing")
    for i, cmd in enumerate(sub_commands, 1):
        print(f"\n   Sub-command {i}: \"{cmd}\"")
        try:
            intent = parser.parse(cmd)
            print(f"   ✓ Intent Type: {intent.intent_type}")
            print(f"     Target: {intent.target}")
            print(f"     Scope: {intent.scope}")
            print(f"     Parameters: {intent.parameters}")
        except Exception as e:
            print(f"   ✗ Error: {e}")

    print("\n" + "=" * 80)


def test_all_requirement_queries():
    """Test all queries from the requirements table"""
    print("\n" + "=" * 80)
    print("TEST 4: ALL REQUIREMENT QUERIES")
    print("=" * 80)

    parser = IntentParser()

    requirement_queries = [
        ("Change voice tone", "change_voice", "audio"),
        ("Make the scene darker", "apply_filter", "video_frame"),
        ("Add background music", "add_bgm", "bgm"),
        ("Remove the subtitle", "toggle_subtitles", "composition"),
        ("Change character design", "change_character_design", "video_frame"),
        ("Speed up this scene", "speed_up", "video"),
        ("Regenerate the script", "regenerate_script", "script")
    ]

    print("\nQuery -> Expected Intent Type -> Expected Target")
    print("─" * 80)

    all_passed = True
    for query, expected_type, expected_target in requirement_queries:
        try:
            intent = parser.parse(query)
            passed = intent.intent_type == expected_type and intent.target == expected_target
            status = "✓" if passed else "✗"
            print(f"\n{status} \"{query}\"")
            print(f"   Expected: {expected_type} -> {expected_target}")
            print(f"   Got:      {intent.intent_type} -> {intent.target}")

            if not passed:
                all_passed = False
                print(f"   MISMATCH!")
        except Exception as e:
            print(f"\n✗ \"{query}\"")
            print(f"   Error: {e}")
            all_passed = False

    print("\n" + "─" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
    else:
        print("✗ SOME TESTS FAILED")

    print("=" * 80)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "MULTI-INTENT EDIT SYSTEM TEST" + " " * 29 + "║")
    print("╚" + "═" * 78 + "╝")

    try:
        # Run all tests
        test_decomposer()
        test_parser()
        test_complex_multi_part()
        test_all_requirement_queries()

        print("\n" + "=" * 80)
        print("🎉 TEST SUITE COMPLETE!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
