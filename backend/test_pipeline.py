"""
Test script to run Phase 1 and Phase 2 end-to-end
This demonstrates the current implementation working together
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from phase1_story.agent import StoryAgent
from phase2_audio.generator import AudioGenerator
from shared.state_manager import StateManager
import config

def main():
    print("=" * 80)
    print("CineAI - Phase 1 & 2 Demo")
    print("=" * 80)
    print()

    # Validate API keys
    print("1️⃣  Validating configuration...")
    try:
        config.validate_config()
        print("   ✅ API keys configured")
    except ValueError as e:
        print(f"   ❌ Configuration error: {e}")
        print("\nPlease update your .env file with valid API keys:")
        print("  - GROQ_API_KEY")
        print("  - ELEVENLABS_API_KEY")
        print("  - HUGGINGFACE_API_KEY")
        return

    # Check BGM library
    print("\n2️⃣  Checking BGM library...")
    from phase2_audio.music_selector import get_available_moods
    available_moods = get_available_moods()
    if available_moods:
        print(f"   ✅ BGM library ready: {', '.join(available_moods)}")
    else:
        print("   ⚠️  No BGM files found. Run: python -m phase2_audio.music_selector")

    # User input
    print("\n3️⃣  Story generation parameters:")
    print("-" * 80)

    # Example prompt
    user_prompt = input("\nEnter your story prompt (or press Enter for default):\n> ").strip()
    if not user_prompt:
        user_prompt = "A lonely astronaut discovers a glowing crystal on Mars that begins to pulse with mysterious energy"
        print(f"Using default: {user_prompt}")

    # Parameters
    genre = input("\nGenre (Sci-Fi/Fantasy/Drama/Thriller) [Sci-Fi]: ").strip() or "Sci-Fi"
    tone = input("Tone (Cinematic/Playful/Dark/Suspense) [Cinematic]: ").strip() or "Cinematic"
    duration = input("Duration (30s/60s/90s/2min) [60s]: ").strip() or "60s"
    aspect = input("Aspect Ratio (16:9/9:16/1:1) [16:9]: ").strip() or "16:9"

    params = {
        "genre": genre,
        "tone": tone,
        "duration": duration,
        "aspect": aspect
    }

    print("\n" + "=" * 80)
    print("🎬 PHASE 1: Story & Script Generation")
    print("=" * 80)

    try:
        # Initialize Phase 1
        print("\nInitializing LangGraph agent with Groq...")
        story_agent = StoryAgent()

        print("Generating story (this may take 30-60 seconds)...\n")

        # Generate story
        state = story_agent.generate(user_prompt, params)

        # Display results
        print("\n✅ STORY GENERATED SUCCESSFULLY!\n")
        print("-" * 80)
        print(f"Title: {state.story.title}")
        print(f"Genre: {state.story.genre}")
        print(f"Summary: {state.story.summary}")
        print(f"\nScenes: {len(state.scenes)}")
        print(f"Characters: {len(state.characters)}")
        print("-" * 80)

        # Show scenes
        print("\n📋 SCENES:")
        for i, scene in enumerate(state.scenes, 1):
            print(f"\n  Scene {i} ({scene.id})")
            print(f"  Mood: {scene.mood.value}")
            print(f"  Duration: {scene.duration_ms / 1000:.1f}s")
            print(f"  Description: {scene.description[:80]}...")
            print(f"  Dialogue lines: {len(scene.dialogue)}")

        # Show characters
        print("\n👥 CHARACTERS:")
        for char in state.characters:
            print(f"\n  {char.name} ({char.role})")
            print(f"  Voice: {char.voice_params.gender}, {char.voice_params.tone}")
            print(f"  Description: {char.visual_description[:60]}...")

        # Save state
        print("\n💾 Saving state...")
        state_manager = StateManager(state.run_id)
        state_manager.snapshot(state, "Initial story generation", [])

        # Save JSON for inspection
        output_file = config.OUTPUTS_DIR / state.run_id / "phase1_output.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(state.dict(), f, indent=2, default=str)

        print(f"   ✅ State saved: {output_file}")

    except Exception as e:
        print(f"\n❌ Phase 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Phase 2
    print("\n" + "=" * 80)
    print("🎙️  PHASE 2: Audio Generation")
    print("=" * 80)

    proceed = input("\nProceed with audio generation? (y/n) [y]: ").strip().lower()
    if proceed and proceed != 'y':
        print("\nStopping here. Your Phase 1 output is saved!")
        print(f"Run ID: {state.run_id}")
        return

    try:
        print("\nInitializing ElevenLabs TTS...")
        audio_generator = AudioGenerator()

        print("Generating audio for all scenes (this may take 1-2 minutes)...\n")

        # Generate audio
        state = audio_generator.generate(state)

        # Display results
        print("\n✅ AUDIO GENERATED SUCCESSFULLY!\n")
        print("-" * 80)

        # Show audio details
        for i, scene in enumerate(state.scenes, 1):
            print(f"\nScene {i} ({scene.id}):")
            print(f"  BGM: {Path(scene.bgm_file).name if scene.bgm_file else 'None'}")
            print(f"  Mood: {scene.mood.value}")
            print(f"  Dialogue:")
            for j, dialogue in enumerate(scene.dialogue, 1):
                audio_file = Path(dialogue.audio_file).name if dialogue.audio_file else "Not generated"
                print(f"    {j}. {dialogue.character}: \"{dialogue.text[:50]}...\"")
                print(f"       Audio: {audio_file}")
                print(f"       Duration: {dialogue.duration_ms / 1000:.1f}s" if dialogue.duration_ms else "")

        # Save updated state
        print("\n💾 Saving updated state...")
        state_manager.snapshot(state, "Audio generation complete", [])

        # Save JSON
        output_file = config.OUTPUTS_DIR / state.run_id / "phase2_output.json"
        with open(output_file, "w") as f:
            json.dump(state.dict(), f, indent=2, default=str)

        print(f"   ✅ State saved: {output_file}")

        # Show asset locations
        print("\n📁 Generated Assets:")
        asset_dir = config.OUTPUTS_DIR / state.run_id / "assets"
        if asset_dir.exists():
            audio_files = list(asset_dir.glob("audio_*"))
            bgm_files = list(asset_dir.glob("bgm_*"))
            print(f"   Audio files: {len(audio_files)}")
            print(f"   BGM files: {len(bgm_files)}")
            print(f"   Location: {asset_dir}")

    except Exception as e:
        print(f"\n❌ Phase 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Summary
    print("\n" + "=" * 80)
    print("🎉 SUCCESS!")
    print("=" * 80)
    print(f"\nRun ID: {state.run_id}")
    print(f"Story: {state.story.title}")
    print(f"Scenes: {len(state.scenes)}")
    print(f"Characters: {len(state.characters)}")
    print(f"Phase 1 Status: {state.phase_status['script']}")
    print(f"Phase 2 Status: {state.phase_status['audio']}")

    print(f"\n📂 Output directory: {config.OUTPUTS_DIR / state.run_id}")
    print("\nNext steps:")
    print("  1. Check the generated audio files in outputs/{run_id}/assets/")
    print("  2. Review the JSON output in outputs/{run_id}/phase2_output.json")
    print("  3. Continue with Phase 3 implementation (video generation)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
