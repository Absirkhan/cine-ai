#!/usr/bin/env python3
"""
Temporary script to fetch ElevenLabs voices
"""
import requests
import json

# API Configuration
ELEVENLABS_API_KEY = "sk_4e6dd987f58be40e796c18acc1df48eb53103dd9f6f8a75c"
API_URL = "https://api.elevenlabs.io/v1/voices"

def fetch_voices():
    """Fetch and display all available voices from ElevenLabs"""
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }

    try:
        print("Fetching voices from ElevenLabs API...")
        print("-" * 60)

        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        voices = data.get("voices", [])

        print(f"\nFound {len(voices)} voices:\n")

        for idx, voice in enumerate(voices, 1):
            name = voice.get("name", "Unknown")
            voice_id = voice.get("voice_id", "N/A")
            labels = voice.get("labels", {})

            # Display basic info
            print(f"{idx}. {name}")
            print(f"   Voice ID: {voice_id}")

            # Display labels if available
            if labels:
                label_str = ", ".join([f"{k}: {v}" for k, v in labels.items()])
                print(f"   Labels: {label_str}")

            print()

        # Also print a simple copy-paste format
        print("\n" + "=" * 60)
        print("COPY-PASTE FORMAT (Name | Voice ID):")
        print("=" * 60)
        for voice in voices:
            print(f"{voice.get('name', 'Unknown'):<30} | {voice.get('voice_id', 'N/A')}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching voices: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    fetch_voices()
