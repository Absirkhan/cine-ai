# CineAI Testing Guide

## 🚀 Quick Start - Test Your Implementation

### Prerequisites Checklist

Before testing, ensure you have:

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] `.env` file configured with API keys
- [ ] BGM music files added to `backend/assets/music/{mood}/` directories

---

## Step 1: Environment Setup

### Windows
```bash
cd cine-ai\backend

# Create virtual environment (if not done)
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### macOS/Linux
```bash
cd cine-ai/backend

# Create virtual environment (if not done)
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure Environment

### Create .env file

```bash
# Windows
copy ..\\.env.example ..\\.env

# macOS/Linux
cp ../.env.example ../.env
```

### Edit .env and add your API keys:

```bash
# Open in your editor
notepad ..\\.env  # Windows
nano ../.env      # macOS/Linux
```

Add your keys:
```env
GROQ_API_KEY=gsk_your_groq_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
HUGGINGFACE_API_KEY=hf_your_huggingface_key_here
```

**Where to get API keys:**
- **Groq:** https://console.groq.com (free tier available)
- **ElevenLabs:** https://elevenlabs.io (free tier: 10,000 characters/month)
- **Hugging Face:** https://huggingface.co/settings/tokens (free)

---

## Step 3: Verify BGM Library

```bash
# Check BGM library status
python -m phase2_audio.music_selector
```

You should see:
```
BGM Library Setup
==================================================

Created the following mood directories:
  calm         → backend/assets/music/calm (✓ 3 tracks)
  tense        → backend/assets/music/tense (✓ 2 tracks)
  upbeat       → backend/assets/music/upbeat (✓ 2 tracks)
  ...
```

If you see "✗ Empty", add some MP3/WAV files to those directories.

---

## Step 4: Run Unit Tests

### Test Phase 1 (Story Generation)

```bash
pytest phase1_story/tests.py -v
```

Expected output:
```
test_extract_json PASSED
test_generate_story_structure PASSED
test_generate_characters PASSED
test_mood_types PASSED
test_scene_validation PASSED
test_full_pipeline PASSED
```

### Test Phase 2 (Audio Generation)

```bash
pytest phase2_audio/tests.py -v
```

Expected output:
```
test_voice_id_mapping PASSED
test_synthesize_dialogue PASSED
test_bgm_selection PASSED
test_available_moods PASSED
test_full_audio_generation PASSED
```

**Note:** Some tests use mocks, so they work without API credits.

---

## Step 5: Run Full Pipeline Demo

### Interactive Test (Recommended)

```bash
python test_pipeline.py
```

This will:
1. ✅ Validate your API keys
2. ✅ Check BGM library
3. 📝 Prompt you for story parameters
4. 🎬 Run Phase 1 (story generation)
5. 🎙️ Run Phase 2 (audio generation)
6. 💾 Save all outputs to `outputs/run_{timestamp}/`

### What to expect:

#### Phase 1 Output:
```
✅ STORY GENERATED SUCCESSFULLY!

Title: Crystal Awakening
Genre: Sci-Fi
Summary: A lone astronaut discovers...

Scenes: 4
Characters: 2

📋 SCENES:
  Scene 1 (scene_001)
  Mood: calm
  Duration: 15.0s
  Description: Astronaut walks across barren Martian landscape...
  Dialogue lines: 2
```

#### Phase 2 Output:
```
✅ AUDIO GENERATED SUCCESSFULLY!

Scene 1 (scene_001):
  BGM: calm_01.mp3
  Mood: calm
  Dialogue:
    1. Narrator: "The red planet stretched endlessly..."
       Audio: audio_scene_001_dialogue_00.mp3
       Duration: 4.2s
```

---

## Step 6: Verify Generated Assets

### Check output directory:

```bash
# Windows
dir ..\outputs\run_*\assets

# macOS/Linux
ls -la ../outputs/run_*/assets
```

You should see:
```
audio_scene_001_dialogue_00.mp3
audio_scene_001_dialogue_01.mp3
bgm_scene_001_calm.mp3
bgm_scene_002_tense.mp3
...
```

### Play audio files:

Open the audio files in your music player to verify they contain:
- Character dialogue (spoken by AI voice)
- Background music (from your BGM library)

---

## 🧪 Advanced Testing

### Test Individual Components

#### Test Story Agent Only

```python
# Create a file: test_story_only.py
from phase1_story.agent import StoryAgent

agent = StoryAgent()
state = agent.generate(
    user_prompt="A robot learns to paint",
    params={"genre": "Drama", "tone": "Warm", "duration": "30s", "aspect": "16:9"}
)

print(f"Title: {state.story.title}")
print(f"Scenes: {len(state.scenes)}")
for scene in state.scenes:
    print(f"  - {scene.description}")
```

Run:
```bash
python test_story_only.py
```

#### Test Audio Generator Only

```python
# Create a file: test_audio_only.py
from phase2_audio.generator import AudioGenerator
from shared.schema import PipelineState, Scene, Character, Dialogue, VoiceParams, MoodType
from shared.utils import generate_run_id
from datetime import datetime

# Create minimal state
state = PipelineState(
    run_id=generate_run_id(),
    version=1,
    timestamp=datetime.utcnow().isoformat(),
    user_prompt="Test",
    user_params={},
    scenes=[
        Scene(
            id="scene_001",
            description="Test scene",
            visual_prompt="Test",
            mood=MoodType.CALM,
            duration_ms=10000,
            dialogue=[
                Dialogue(character="Narrator", text="This is a test of the audio system.")
            ]
        )
    ],
    characters=[
        Character(
            name="Narrator",
            role="narrator",
            voice_params=VoiceParams(gender="male", tone="calm"),
            visual_description="N/A"
        )
    ],
    phase_status={
        "script": "complete",
        "audio": "pending",
        "video": "pending",
        "web": "pending",
        "edit": "pending"
    }
)

# Generate audio
generator = AudioGenerator()
state = generator.generate(state)

print(f"Audio generated: {state.scenes[0].dialogue[0].audio_file}")
```

Run:
```bash
python test_audio_only.py
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langchain'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "ValueError: Configuration errors: GROQ_API_KEY is not set"

**Solution:**
1. Check `.env` file exists in project root
2. Verify API key is correctly formatted
3. Make sure no spaces around `=` sign
4. Restart your terminal/IDE

### Issue: "ElevenLabs API Error: Unauthorized"

**Solution:**
- Check your ElevenLabs API key is valid
- Verify you have credits remaining (free tier: 10,000 chars/month)
- Go to https://elevenlabs.io to check account status

### Issue: "No BGM files found"

**Solution:**
```bash
# Add MP3/WAV files to mood directories
# Example:
cp your_calm_music.mp3 backend/assets/music/calm/
cp your_tense_music.mp3 backend/assets/music/tense/
```

### Issue: "Groq rate limit exceeded"

**Solution:**
- Wait a few minutes (free tier has rate limits)
- Reduce story complexity (use 30s duration instead of 60s)
- Consider upgrading to paid tier

### Issue: "pydub can't find ffmpeg"

**Solution:**
Install FFmpeg:
- **Windows:** Download from https://ffmpeg.org or `choco install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Linux:** `apt-get install ffmpeg`

Then add to PATH and restart terminal.

---

## 📊 Performance Expectations

### Phase 1 (Story Generation)
- **Duration:** 30-60 seconds
- **API Calls:** 4-5 calls to Groq
- **Output Size:** ~10-20 KB JSON

### Phase 2 (Audio Generation)
- **Duration:** 1-2 minutes (depends on dialogue length)
- **API Calls:** 1 call per dialogue line (typically 8-12 total)
- **Output Size:** ~500 KB - 2 MB audio files

### Total for Full Pipeline Test
- **Duration:** 2-3 minutes
- **Disk Usage:** ~2-5 MB per run
- **API Credits Used:**
  - Groq: ~5,000 tokens
  - ElevenLabs: ~500-1,000 characters

---

## ✅ Success Checklist

After running `python test_pipeline.py`, you should have:

- [ ] No errors in terminal
- [ ] `outputs/run_{timestamp}/` directory created
- [ ] `phase1_output.json` and `phase2_output.json` files
- [ ] Multiple `audio_*.mp3` files in assets folder
- [ ] Multiple `bgm_*.mp3` files in assets folder
- [ ] State snapshots in `states/v001/` directory

---

## 🎯 What's Working

After successful test, you can confirm:

✅ **Phase 1:**
- LangGraph workflow executing correctly
- Groq API integration working
- Story structure with scenes and characters
- Mood tags assigned to scenes
- Visual prompts generated
- Dialogue created for all scenes

✅ **Phase 2:**
- ElevenLabs TTS synthesis working
- Character voices correctly mapped
- BGM selected based on mood
- Audio files saved to correct locations
- Timing manifest created

✅ **Infrastructure:**
- Configuration system working
- State management saving snapshots
- File structure correct
- Asset organization working

---

## 📞 Next Steps After Testing

Once testing is successful:

1. **Explore the outputs:**
   - Listen to generated audio
   - Read the JSON structure
   - Check BGM selection matches scene moods

2. **Try different prompts:**
   - Different genres (Fantasy, Drama, Thriller)
   - Different tones (Playful, Dark, Suspense)
   - Different durations (30s, 90s, 2min)

3. **Review the code:**
   - Understand the LangGraph workflow
   - See how phases communicate via PipelineState
   - Check how state versioning works

4. **Continue to Phase 3:**
   - Read [NEXT_STEPS.md](NEXT_STEPS.md)
   - Start implementing video generation
   - Follow the established patterns

---

## 📝 Sample Test Session

Here's a complete test session example:

```bash
# 1. Activate environment
cd cine-ai/backend
venv\Scripts\activate  # Windows

# 2. Run tests
pytest phase1_story/tests.py -v
pytest phase2_audio/tests.py -v

# 3. Run full demo
python test_pipeline.py

# Enter when prompted:
# Prompt: A robot learns to paint in a quiet studio
# Genre: Drama
# Tone: Warm
# Duration: 30s
# Aspect: 16:9

# Wait 2-3 minutes...

# 4. Check outputs
cd ..\outputs
dir /s  # List all generated files

# 5. Play an audio file
start run_*/assets/audio_scene_001_dialogue_00.mp3
```

---

**You're now ready to test! Run `python test_pipeline.py` and see your AI video pipeline in action! 🚀**
