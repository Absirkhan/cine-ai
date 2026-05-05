#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for voice validation system
Tests that only allowlisted voices are accepted
"""

import sys
import os

# Set console encoding to UTF-8 for Windows
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from phase2_audio.voice_config import (
    validate_voice_id,
    select_voice_by_character,
    select_voice_by_genre,
    select_voice_by_tone,
    get_voice_info,
    ALLOWED_VOICES,
    ALLOWED_VOICE_IDS
)


def test_allowlist():
    """Test that allowlist contains exactly 8 voices"""
    print("=" * 60)
    print("TEST 1: Allowlist Configuration")
    print("=" * 60)

    print(f"\nAllowed voices count: {len(ALLOWED_VOICES)}")
    print(f"Expected: 8")
    assert len(ALLOWED_VOICES) == 8, "Should have exactly 8 voices"
    print("✓ PASS: Allowlist has 8 voices\n")

    print("Allowed voices:")
    for key, info in ALLOWED_VOICES.items():
        print(f"  - {info['name']:15} | {info['voice_id']} | {info['description']}")


def test_voice_validation():
    """Test voice ID validation"""
    print("\n" + "=" * 60)
    print("TEST 2: Voice ID Validation")
    print("=" * 60)

    # Test valid voices
    print("\nTesting VALID voice IDs:")
    valid_ids = [
        "JBFqnCBsd6RMkjVDRZzb",  # George
        "cgSgspJ2msm6clMCkdW9",  # Jessica
        "SOYHLrjzK2X1ezoPC6cr",  # Harry
    ]

    for voice_id in valid_ids:
        result = validate_voice_id(voice_id)
        info = get_voice_info(voice_id)
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {voice_id} ({info['name'] if info else 'Unknown'})")
        assert result, f"Valid voice {voice_id} should pass validation"

    # Test invalid voices (would cause 402 errors)
    print("\nTesting INVALID voice IDs (should be blocked):")
    invalid_ids = [
        "EXAVITQu4vr4xnSDxMaL",  # Bella (premium)
        "21m00Tcm4TlvDq8ikWAM",  # Rachel (premium)
        "pNInz6obpgDQGcFmaJgB",  # Adam (premium)
        "fake_voice_id_12345",   # Fake ID
    ]

    for voice_id in invalid_ids:
        result = validate_voice_id(voice_id)
        status = "✓ PASS (blocked)" if not result else "✗ FAIL (allowed)"
        print(f"  {status}: {voice_id}")
        assert not result, f"Invalid voice {voice_id} should NOT pass validation"

    print("\n✓ ALL VALIDATION TESTS PASSED")


def test_character_selection():
    """Test character-based voice selection"""
    print("\n" + "=" * 60)
    print("TEST 3: Character Voice Selection")
    print("=" * 60)

    test_cases = [
        ("female", "calm", "Matilda"),
        ("female", "energetic", "Jessica"),
        ("male", "calm", "Will"),
        ("male", "authoritative", "Daniel"),
        ("male", "energetic", "Harry"),
        ("male", "playful", "Callum"),
    ]

    print("\nTesting character parameter mappings:")
    for gender, tone, expected_name in test_cases:
        voice_id = select_voice_by_character(gender, tone)
        info = get_voice_info(voice_id)
        actual_name = info['name'] if info else "Unknown"

        status = "✓ PASS" if actual_name == expected_name else "⚠ MAPPED"
        print(f"  {status}: ({gender}, {tone}) -> {actual_name} (expected: {expected_name})")

        # Ensure selected voice is in allowlist
        assert validate_voice_id(voice_id), f"Selected voice {voice_id} must be in allowlist"

    print("\n✓ ALL CHARACTER SELECTIONS ARE VALID")


def test_genre_selection():
    """Test genre-based voice selection"""
    print("\n" + "=" * 60)
    print("TEST 4: Genre-Based Voice Selection")
    print("=" * 60)

    genres = ["sci-fi", "thriller", "comedy", "drama", "fantasy", "documentary"]

    print("\nTesting genre mappings:")
    for genre in genres:
        voice_id = select_voice_by_genre(genre)
        info = get_voice_info(voice_id)
        name = info['name'] if info else "Unknown"

        print(f"  ✓ {genre:15} -> {name:15} ({voice_id})")

        # Ensure selected voice is in allowlist
        assert validate_voice_id(voice_id), f"Genre voice {voice_id} must be in allowlist"

    print("\n✓ ALL GENRE SELECTIONS ARE VALID")


def test_tone_selection():
    """Test tone-based voice selection"""
    print("\n" + "=" * 60)
    print("TEST 5: Tone-Based Voice Selection")
    print("=" * 60)

    tones = ["dark", "suspense", "playful", "warm", "professional", "calm"]

    print("\nTesting tone mappings:")
    for tone in tones:
        voice_id = select_voice_by_tone(tone)
        info = get_voice_info(voice_id)
        name = info['name'] if info else "Unknown"

        print(f"  ✓ {tone:15} -> {name:15} ({voice_id})")

        # Ensure selected voice is in allowlist
        assert validate_voice_id(voice_id), f"Tone voice {voice_id} must be in allowlist"

    print("\n✓ ALL TONE SELECTIONS ARE VALID")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ELEVENLABS FREE TIER VOICE VALIDATION TEST SUITE")
    print("=" * 60 + "\n")

    try:
        test_allowlist()
        test_voice_validation()
        test_character_selection()
        test_genre_selection()
        test_tone_selection()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! Voice validation system is working correctly.")
        print("=" * 60)
        print("\n✓ Only the 8 allowlisted voices will be used")
        print("✓ Premium voices are blocked and will not cause 402 errors")
        print("✓ All selection methods return valid voice IDs\n")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
