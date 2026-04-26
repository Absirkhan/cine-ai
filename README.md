# CineAI - AI-Powered Animated Video Generation System

**From Prompt to Polished Short Film — End-to-End with LLM Agents**

A multi-phase agentic pipeline built with LangChain/LangGraph that autonomously generates story, dialogue, character voices, visual scenes, and a final MP4. Features a full-stack web dashboard with real-time progress tracking, phase-level re-runs, and an intelligent edit agent that accepts free-text commands with full undo/version history.

## 🎬 Project Overview

CineAI transforms a single natural language prompt into a complete animated short film with:
- **Automated Story & Script Writing** (Groq + Llama 3.3-70b)
- **Character Voice Synthesis** (ElevenLabs TTS)
- **Mood-Based Background Music** (Royalty-free library)
- **AI-Generated Visuals** (Hugging Face FLUX.1-schnell)
- **Video Composition** (MoviePy + FFmpeg)
- **Natural Language Editing** (LangGraph edit agent with full undo)

## 🏗️ System Architecture

### Pipeline Phases

1. **Phase 1: Story & Script Generation** ✅
   - LangGraph multi-agent workflow
   - Scene-by-scene breakdown with mood tags
   - Character profiles with voice parameters
   - Dialogue generation
   - Visual prompts for image generation

2. **Phase 2: Audio Generation** ✅
   - ElevenLabs TTS per character
   - Mood-based BGM selection
   - Audio timing manifest

3. **Phase 3: Video Composition** ✅
   - FLUX.1 image generation
   - MoviePy animation (zoom/pan with Ken Burns effects)
   - A/V synchronization
   - Final MP4 export with FFmpeg

4. **Phase 4: Web Interface** ✅
   - FastAPI backend with WebSocket
   - Real-time progress tracking
   - Phase-level re-runs
   - React frontend (complete)

5. **Phase 5: Edit Agent** ✅
   - Natural language edit commands
   - Intent classification with LangGraph
   - OpenCV filters (10+ types)
   - Version control with full undo/redo

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- API Keys:
  - [Groq API](https://console.groq.com)
  - [ElevenLabs API](https://elevenlabs.io)
  - [Hugging Face API](https://huggingface.co/settings/tokens)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd cine-ai

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your API keys

# Setup BGM library
python -m phase2_audio.music_selector
# Follow instructions to add music files
```

### Running Tests

```bash
# Phase 1 tests
pytest phase1_story/tests.py -v

# Phase 2 tests
pytest phase2_audio/tests.py -v
```

## 📁 Project Structure

```
cine-ai/
├── backend/
│   ├── shared/           # Shared schemas and utilities ✅
│   ├── phase1_story/     # Story generation ✅
│   ├── phase2_audio/     # Audio synthesis ✅
│   ├── phase3_video/     # Video composition ✅
│   ├── phase5_edit/      # Edit agent ✅
│   ├── assets/music/     # BGM library
│   ├── config.py         # Configuration ✅
│   ├── orchestrator.py   # Pipeline coordinator ✅
│   └── main.py           # FastAPI app ✅
├── frontend/             # React UI ✅
├── outputs/              # Generated videos
└── .env                  # Environment variables
```

## 🎨 Frontend Features (Complete)

- **Home Screen**: Prompt input with genre, tone, duration controls
- **Pipeline Dashboard**: Phase-by-phase status and re-run buttons
- **Progress Screen**: Real-time logs and vertical stepper
- **Preview Screen**: Video player with download
- **Edit Agent**: Natural language editing interface

## 📚 Technology Stack

- **Backend**: FastAPI, LangChain, LangGraph
- **LLM**: Groq (Llama 3.3-70b-versatile)
- **TTS**: ElevenLabs API
- **Image Gen**: Hugging Face FLUX.1-schnell
- **Video**: MoviePy, FFmpeg
- **Frontend**: React (existing)
- **Database**: SQLite (state persistence)

## 🎵 BGM Library Setup

Organize royalty-free music in:
```
backend/assets/music/
├── calm/
├── tense/
├── upbeat/
├── mysterious/
├── dramatic/
├── sad/
└── ambient/
```

**Recommended Sources:**
- [Free Music Archive](https://freemusicarchive.org)
- [YouTube Audio Library](https://youtube.com/audiolibrary)
- [Incompetech](https://incompetech.com)

## 📊 Implementation Status

See [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) for detailed progress.

**Overall: 100% Complete - Ready for Testing & Demo**
- ✅ Shared infrastructure
- ✅ Phase 1 (Story generation with LangGraph)
- ✅ Phase 2 (Audio generation with ElevenLabs + BGM)
- ✅ Phase 3 (Video composition with FLUX.1 + MoviePy)
- ✅ Phase 4 (Web interface with FastAPI + WebSocket)
- ✅ Phase 5 (Edit agent with natural language + undo/redo)

## 🔧 Development Roadmap

### Completed Implementation ✅
1. ✅ Phase 3 (Video generation with FLUX.1 + MoviePy)
2. ✅ Phase 4 (FastAPI orchestration + WebSocket)
3. ✅ Phase 5 (Edit agent with 10+ filters)
4. ✅ Complete pipeline integration

### Next Steps (User Testing & Demo)
1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure API keys** in `.env` file
3. **Test full pipeline** with sample prompts
4. **Create demo video** showing:
   - Full pipeline execution
   - 3 different edits
   - 2 undo operations
5. **Write final report** (8-12 pages)
6. **Prepare presentation** slides

### Future Enhancements
- Docker deployment
- Cloud storage integration
- Batch processing
- Advanced editing features

## 📝 License

MIT License - see LICENSE file

## 👥 Contributors

Group Members:
- Member 1: Phase 1 (Story & Script)
- Member 2: Phase 2 (Audio)
- Member 3: Phase 3 (Video)
- Member 4: Phase 4 & 5 (Web + Edit Agent)

## 📞 Support

For issues and questions:
- Check [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)
- Review test files for usage examples
- See frontend JSX files for UI examples

---

**🚀 CineAI - Democratizing Animated Film Production with Agentic AI**
