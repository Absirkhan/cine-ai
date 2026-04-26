# 🚀 START HERE - Test Your CineAI Implementation

Your environment is **ready to go!** ✅

## ✅ Verified Setup

- ✅ Python 3.11 installed
- ✅ Virtual environment exists
- ✅ All dependencies installed
- ✅ API keys configured (.env file)
- ✅ BGM library populated (21 music tracks across 7 moods!)

---

## 🎬 Run Your First Test (2 minutes)

Open your terminal and run:

```bash
cd backend
python test_pipeline.py
```

This will:
1. Validate your API keys
2. Let you enter a story prompt (or use default)
3. Generate a complete story with scenes and characters (Phase 1)
4. Generate AI voices and background music (Phase 2)
5. Save everything to `outputs/` folder

---

## 📝 Quick Test Example

```bash
cd backend
python test_pipeline.py
```

When prompted:
- **Story prompt:** Press Enter to use default (or type your own)
- **Genre:** `Sci-Fi` (or press Enter for default)
- **Tone:** `Cinematic` (or press Enter)
- **Duration:** `60s` (or press Enter)
- **Aspect:** `16:9` (or press Enter)

Wait 2-3 minutes while the AI:
- ✨ Writes your story
- 👥 Creates characters
- 💬 Generates dialogue
- 🎙️ Synthesizes voices
- 🎵 Selects background music

---

## 🎯 What You'll Get

After the test completes, check `outputs/run_YYYYMMDD_HHMMSS/`:

```
outputs/run_20260423_160000/
├── assets/
│   ├── audio_scene_001_dialogue_00.mp3  ← AI voice dialogue
│   ├── audio_scene_001_dialogue_01.mp3
│   ├── bgm_scene_001_calm.mp3           ← Background music
│   ├── bgm_scene_002_tense.mp3
│   └── ...
├── states/
│   └── v001/                            ← Version snapshot (for undo)
│       ├── state.json
│       └── snapshot.json
├── phase1_output.json                   ← Story & script data
└── phase2_output.json                   ← Audio manifest
```

**Play the audio files!** You'll hear:
- AI-generated character voices speaking the dialogue
- Background music matching the scene mood

---

## 🧪 Alternative: Run Unit Tests First

If you want to test without using API credits:

```bash
cd backend

# Test Phase 1 (uses mocks, no API calls)
pytest phase1_story/tests.py -v

# Test Phase 2 (uses mocks, no API calls)
pytest phase2_audio/tests.py -v
```

All tests should **PASS** ✅

---

## 📊 Your Current Status

**Implemented:** 40% (Phase 1 & 2 complete)

| Phase | Status | What It Does |
|-------|--------|--------------|
| Phase 1 | ✅ DONE | Generates story, scenes, characters, dialogue |
| Phase 2 | ✅ DONE | Synthesizes voices, selects BGM |
| Phase 3 | 🚧 Next | Will generate images and compose video |
| Phase 4 | 🚧 Later | Web interface with FastAPI |
| Phase 5 | 🚧 Later | Edit agent with undo/redo |

---

## 🎨 Try Different Prompts

After your first test, try these:

**Fantasy:**
```
Prompt: A young wizard discovers a forbidden spell in an ancient library
Genre: Fantasy
Tone: Dark
Duration: 30s
```

**Documentary:**
```
Prompt: Deep-sea creatures communicate through bioluminescence
Genre: Documentary
Tone: Cinematic
Duration: 60s
```

**Comedy:**
```
Prompt: A robot chef tries to make the perfect pizza but keeps burning it
Genre: Comedy
Tone: Playful
Duration: 45s
```

---

## 🐛 If Something Goes Wrong

### "Configuration errors: GROQ_API_KEY is not set"
- Check `.env` file exists in project root
- Verify API keys are on the correct lines
- No spaces around the `=` sign

### "ElevenLabs API Error"
- Check you have credits remaining (free tier: 10,000 chars/month)
- Visit https://elevenlabs.io to verify account

### "Module not found"
```bash
cd backend
pip install -r requirements.txt
```

### Need help?
- Read [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed troubleshooting
- Check [NEXT_STEPS.md](NEXT_STEPS.md) for what to do after testing

---

## 📖 Understanding the Output

### phase1_output.json
Contains the complete story structure:
- Title and summary
- 3-5 scenes with descriptions
- Character profiles with voice parameters
- Dialogue for each scene
- Visual prompts for future image generation

### phase2_output.json
Contains audio generation results:
- File paths to all generated audio
- BGM selections per scene
- Timing information for A/V sync

### Audio Files
- `audio_*.mp3` - Character dialogue synthesized with ElevenLabs
- `bgm_*.mp3` - Background music selected from your library based on scene mood

---

## 🎯 What to Check

Listen to the audio and verify:
- [ ] Dialogue is clear and understandable
- [ ] Voices match character types (calm vs energetic, male vs female)
- [ ] Background music matches scene mood (calm scenes have calm music, tense scenes have tense music)
- [ ] Multiple characters have distinct voices

Review the JSON and verify:
- [ ] Story has a coherent structure
- [ ] Scenes have mood tags (calm, tense, upbeat, etc.)
- [ ] Characters have voice parameters
- [ ] Dialogue fits the scene descriptions

---

## ✨ Cool Features to Notice

1. **Mood-Based Music Selection**
   - Phase 1 assigns a mood to each scene
   - Phase 2 automatically picks matching music from your library
   - Different scenes get different music based on narrative arc

2. **Character Voice Consistency**
   - Same character uses same voice throughout
   - Voice parameters (gender, tone) determine which ElevenLabs voice is used

3. **Version Control**
   - Every run is saved with version snapshots
   - Ready for Phase 5 undo/redo functionality

4. **Timing Manifest**
   - Audio segments track start and end times
   - Prepared for Phase 3 video synchronization

---

## 🚀 After Testing

Once you've verified everything works:

1. **Explore the code:**
   - Check `backend/phase1_story/agent.py` to see the LangGraph workflow
   - Review `backend/shared/schema.py` to understand data structures
   - Look at `backend/phase2_audio/generator.py` for TTS integration

2. **Read the docs:**
   - [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - What's done
   - [NEXT_STEPS.md](NEXT_STEPS.md) - How to continue
   - [.claude/project_context.md](.claude/project_context.md) - Full context

3. **Continue development:**
   - Implement Phase 3 (video generation)
   - Follow the patterns from Phase 1 & 2
   - Test incrementally as you build

---

## 🎬 Ready? Let's Go!

```bash
cd backend
python test_pipeline.py
```

**Enjoy watching your AI create stories and voices! 🎉**
