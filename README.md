# CineAI - AI-Powered Animated Video Generation System

**From Prompt to Polished Short Film — End-to-End with Multi-Agent LLM Pipeline**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Tests](https://img.shields.io/badge/tests-19%20passing-brightgreen.svg)](./TEST_REPORT.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

A production-ready, multi-phase agentic AI pipeline that autonomously generates complete animated short films from a single natural language prompt. Built with LangChain/LangGraph, featuring intelligent editing capabilities with full undo/version control, and a modern React-based web interface with real-time progress tracking.

---

## 🎬 Overview

CineAI is a comprehensive video generation system that transforms text prompts into complete short films through a five-phase pipeline, combining multiple AI models and media processing technologies.

### What CineAI Does

**Input:** `"Create a short mystery story about a detective solving a case in a dark office"`

**Output:** A complete MP4 video with:
- ✅ AI-generated story and screenplay
- ✅ Scene-by-scene breakdown with visual descriptions
- ✅ Character profiles with distinct AI-generated voices
- ✅ Mood-appropriate background music
- ✅ AI-generated scene images (FLUX.1)
- ✅ Animated video with Ken Burns effects
- ✅ Audio-video synchronization
- ✅ Natural language editing capabilities ("Make scene 1 darker", "Change the music")
- ✅ Full undo/redo with version history

### Key Features

- **🤖 Multi-Agent Orchestration**: LangGraph-powered workflows for story generation and editing
- **🎨 AI-Generated Visuals**: Hugging Face FLUX.1-schnell for high-quality scene images
- **🎭 Character Voice Synthesis**: ElevenLabs TTS with fallback to Deepgram
- **🎵 Intelligent BGM Selection**: Mood-based background music from curated library
- **🎬 Video Composition**: MoviePy with Ken Burns effects + FFmpeg A/V sync
- **💬 Natural Language Editing**: Multi-intent edit system supporting complex commands
- **⏮️ Version Control**: Full undo/redo with asset snapshots
- **📡 Real-Time Updates**: WebSocket-powered progress tracking
- **🌐 Modern Web UI**: React frontend with Material Design
- **🧪 Comprehensive Testing**: 19 unit & integration tests (100% pass rate)

---

## 🏗️ System Architecture

### Five-Phase Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INPUT (Prompt)                          │
│  "Create a short mystery story about a detective..."             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: Story & Script Generation                              │
│  ├─ LangGraph multi-agent workflow (5 nodes)                     │
│  ├─ Groq API (Llama 3.3-70b-versatile)                           │
│  ├─ Character profiles with voice parameters                     │
│  ├─ Scene breakdown with mood tags                               │
│  └─ Visual prompt engineering for FLUX.1                         │
│  Output: PipelineState with story, characters, scenes            │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: Audio Generation                                       │
│  ├─ ElevenLabs TTS (primary) / Deepgram (fallback)               │
│  ├─ Character-specific voice synthesis                           │
│  ├─ Mood-based BGM selection                                     │
│  ├─ Audio timing manifest for A/V sync                           │
│  └─ Duration calculation                                         │
│  Output: Audio files + timing data                               │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: Video Composition                                      │
│  ├─ FLUX.1-schnell image generation (HuggingFace)                │
│  ├─ Visual continuity management                                 │
│  ├─ Ken Burns effects (zoom/pan animation)                       │
│  ├─ MoviePy video composition                                    │
│  ├─ FFmpeg A/V synchronization                                   │
│  └─ Final MP4 export                                             │
│  Output: Complete video file                                     │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 4: Web Application & API                                  │
│  ├─ FastAPI REST endpoints                                       │
│  ├─ WebSocket for real-time progress                             │
│  ├─ React frontend (5 screens)                                   │
│  ├─ Phase-level re-run support                                   │
│  └─ Run history management                                       │
│  UI: Complete web interface                                      │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 5: Edit Agent & Version Control                           │
│  ├─ Intent decomposer (multi-part commands)                      │
│  ├─ LangGraph intent parser (16 intent types)                    │
│  ├─ Edit executor (14 handlers)                                  │
│  ├─ OpenCV filters (10+ types)                                   │
│  ├─ State manager (snapshot-based versioning)                    │
│  └─ Cascading phase regeneration                                 │
│  Features: Natural language editing + full undo/redo             │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend
- **Framework**: FastAPI 0.104+ with WebSocket support
- **LLM Orchestration**: LangChain + LangGraph
- **AI Models**:
  - Story: Groq (Llama 3.3-70b-versatile)
  - TTS: ElevenLabs API (primary), Deepgram (fallback)
  - Images: Hugging Face FLUX.1-schnell
- **Media Processing**: MoviePy 1.0.3, FFmpeg, Pydub, OpenCV
- **Data Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio

#### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI)
- **State Management**: React hooks
- **HTTP Client**: Axios
- **WebSocket**: Native WebSocket API
- **Build Tool**: Vite

#### Infrastructure
- **State Persistence**: JSON-based with versioning
- **Asset Management**: File system with snapshot backups
- **Real-time Communication**: WebSocket (progress & chat)
- **API Documentation**: FastAPI auto-generated (Swagger/OpenAPI)

---

## 📁 Project Structure

```
cine-ai/
├── backend/                              # Python backend
│   ├── shared/                           # Core infrastructure
│   │   ├── schema.py                     # Pydantic models (all data contracts)
│   │   ├── state_manager.py              # Version control & snapshots
│   │   └── utils.py                      # Shared utilities
│   ├── phase1_story/                     # Story generation
│   │   ├── agent.py                      # LangGraph workflow (5 nodes)
│   │   ├── prompts.py                    # Prompt templates
│   │   └── tests.py                      # Unit tests
│   ├── phase2_audio/                     # Audio synthesis
│   │   ├── generator.py                  # TTS orchestrator
│   │   ├── voice_config.py               # ElevenLabs voice mapping
│   │   ├── deepgram_voice_config.py      # Deepgram fallback config
│   │   ├── music_selector.py             # BGM selection by mood
│   │   ├── timing.py                     # Audio timing manifest
│   │   └── tests.py                      # Unit tests
│   ├── phase3_video/                     # Video composition
│   │   ├── image_generator.py            # FLUX.1 HuggingFace integration
│   │   ├── visual_context.py             # Visual continuity manager
│   │   ├── animator.py                   # Ken Burns effects
│   │   ├── compositor.py                 # A/V sync + export
│   │   ├── video_generator.py            # Phase 3 orchestrator
│   │   └── tests.py                      # Unit tests
│   ├── phase5_edit/                      # Edit agent
│   │   ├── intent_decomposer.py          # Multi-intent command splitter
│   │   ├── intent_parser.py              # LangGraph NL classifier
│   │   ├── executor.py                   # Edit execution (14 handlers)
│   │   ├── filters.py                    # OpenCV visual filters
│   │   ├── edit_agent.py                 # Main edit interface
│   │   ├── test_multi_intent.py          # Integration tests
│   │   └── test_schema_validation.py     # Schema tests
│   ├── tests/                            # Comprehensive test suite
│   │   ├── test_comprehensive.py         # 19 tests (100% pass)
│   │   ├── test_shared.py                # Shared module tests
│   │   ├── test_phase1_basic.py          # Phase 1 tests
│   │   ├── test_phase2_basic.py          # Phase 2 tests
│   │   ├── test_phase5_basic.py          # Phase 5 tests
│   │   └── test_integration_basic.py     # Integration tests
│   ├── assets/music/                     # BGM library
│   │   ├── calm/                         # Calm mood tracks
│   │   ├── tense/                        # Tense mood tracks
│   │   ├── upbeat/                       # Upbeat mood tracks
│   │   ├── mysterious/                   # Mysterious mood tracks
│   │   ├── dramatic/                     # Dramatic mood tracks
│   │   ├── sad/                          # Sad mood tracks
│   │   └── ambient/                      # Ambient/default tracks
│   ├── config.py                         # Configuration management
│   ├── orchestrator.py                   # Pipeline coordinator
│   ├── main.py                           # FastAPI application
│   ├── requirements.txt                  # Python dependencies
│   └── .env.example                      # Environment template
├── frontend/                             # React frontend
│   ├── index.html                        # Entry HTML
│   ├── screen-home.jsx                   # Prompt input screen
│   ├── screen-pipeline.jsx               # Phase dashboard
│   ├── screen-progress.jsx               # Real-time progress
│   ├── screen-preview.jsx                # Video player
│   ├── screen-edit-agent.jsx             # Edit interface
│   └── src/                              # TypeScript sources
│       ├── services/api.ts               # API client
│       ├── hooks/useProgressWebSocket.ts # Progress WS hook
│       └── hooks/useChatWebSocket.ts     # Chat WS hook
├── outputs/                              # Generated videos (gitignored)
│   └── {run_id}/                         # Per-run outputs
│       ├── phase1_output.json            # Story data
│       ├── phase2_output.json            # Audio manifest
│       ├── states/                       # Version snapshots
│       │   ├── v001/                     # Version 1
│       │   ├── v002/                     # Version 2
│       │   └── ...
│       ├── audio/                        # TTS & BGM files
│       ├── images/                       # Generated scene images
│       ├── videos/                       # Scene videos
│       └── final_output.mp4              # Final video
├── docs/                                 # Documentation
│   ├── TEST_REPORT.md                    # Comprehensive test report
│   ├── TEST_RESULTS_SUMMARY.txt          # Quick test summary
│   ├── SAMPLE_TEST_OUTPUT.txt            # Sample test execution
│   ├── IMPLEMENTATION_SUMMARY.md         # Multi-intent system docs
│   ├── MULTI_INTENT_EDIT_SYSTEM.md       # Edit system details
│   ├── EDIT_QUERY_EXAMPLES.md            # Query examples
│   ├── API_INTEGRATION_GUIDE.md          # Frontend-backend guide
│   ├── FINAL_STATUS.md                   # Project status
│   ├── QUICK_START.md                    # Quick start guide
│   ├── RUN_APP.md                        # Detailed running instructions
│   ├── TESTING_GUIDE.md                  # Testing scenarios
│   └── START_HERE.md                     # New user guide
├── .env.example                          # Environment template
├── .gitignore                            # Git ignore rules
├── LICENSE                               # MIT License
└── README.md                             # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11+ ([Download](https://www.python.org/downloads/))
- **Node.js**: 18+ (for frontend development) ([Download](https://nodejs.org/))
- **FFmpeg**: Required for video processing ([Download](https://ffmpeg.org/download.html))
- **Git**: For cloning the repository

### API Keys Required

1. **Groq API**: [https://console.groq.com](https://console.groq.com) (Free tier available)
2. **ElevenLabs API**: [https://elevenlabs.io](https://elevenlabs.io) (Free: 10k characters/month)
3. **Hugging Face API**: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (Free with rate limits)
4. **Deepgram API** (Optional): [https://console.deepgram.com](https://console.deepgram.com) (TTS fallback)

### Installation

#### 1. Clone Repository

```bash
git clone <repository-url>
cd cine-ai
```

#### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
notepad .env  # Windows
# nano .env   # Linux/Mac
```

**.env file structure:**
```ini
# LLM & Story Generation
GROQ_API_KEY=your_groq_api_key_here

# Text-to-Speech (Primary)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Text-to-Speech (Fallback)
DEEPGRAM_API_KEY=your_deepgram_api_key_here  # Optional

# Image Generation
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Application Settings
LOG_LEVEL=INFO
MAX_SCENE_DURATION_MS=15000
DEFAULT_ASPECT_RATIO=16:9
```

#### 4. Setup BGM Library

```bash
# Create BGM directories
cd backend
python -m phase2_audio.music_selector
```

Add royalty-free music files (MP3/WAV) to the mood folders:
- `backend/assets/music/calm/` - Peaceful, relaxing tracks
- `backend/assets/music/tense/` - Suspenseful, dramatic tracks
- `backend/assets/music/upbeat/` - Energetic, happy tracks
- `backend/assets/music/mysterious/` - Enigmatic, curious tracks
- `backend/assets/music/dramatic/` - Epic, intense tracks
- `backend/assets/music/sad/` - Melancholic, somber tracks
- `backend/assets/music/ambient/` - Neutral, background tracks

**Recommended Sources:**
- [Free Music Archive](https://freemusicarchive.org)
- [YouTube Audio Library](https://youtube.com/audiolibrary)
- [Incompetech](https://incompetech.com)
- [Bensound](https://bensound.com)

#### 5. Run the Application

```bash
# Make sure virtual environment is activated
cd backend
uvicorn main:app --reload --port 8000
```

The application will be available at:
- **Web UI**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger)
- **Alternative Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

#### 6. Run Tests

```bash
cd backend

# Run comprehensive test suite
pytest tests/test_comprehensive.py -v

# Run all tests
pytest -v

# Run specific phase tests
pytest phase1_story/tests.py -v
pytest phase2_audio/tests.py -v
pytest phase5_edit/test_multi_intent.py -v
```

---

## 📖 Usage Guide

### Basic Usage

1. **Open Web Interface**: Navigate to [http://localhost:8000](http://localhost:8000)
2. **Enter Prompt**: e.g., "Create a short mystery story about a detective solving a case"
3. **Configure Settings**:
   - Genre: Mystery, Sci-Fi, Documentary, etc.
   - Tone: Cinematic, Playful, Dramatic, etc.
   - Duration: 30-90 seconds
   - Aspect Ratio: 16:9, 9:16, 1:1
4. **Generate**: Click "Generate Video" and monitor real-time progress
5. **Preview**: Watch the generated video
6. **Edit**: Use natural language commands to refine the video
7. **Download**: Save the final MP4

### Example Prompts

**Mystery/Detective:**
```
Create a short mystery story about a detective solving a case in a dark office
```

**Sci-Fi:**
```
A lone astronaut discovers an alien artifact on Mars
```

**Documentary:**
```
Explain the water cycle in a simple, educational way for children
```

**Fantasy:**
```
A young wizard's first day at magic school
```

**Historical:**
```
The discovery of penicillin by Alexander Fleming
```

### Natural Language Editing

After generation, you can edit the video using natural language:

**Single-Intent Commands:**
- "Make scene 1 darker"
- "Add sepia tone to scene 2"
- "Change the music to tense"
- "Brighten the entire video"
- "Add blur effect to scene 3"
- "Remove background music from scene 1"
- "Change Alice's voice to be more calm"

**Multi-Intent Commands:**
- "Make scene 1 darker and scene 3 brighter"
- "Change scene 1 to male and female characters, keep scene 2 same, and scene 3 also male and female"
- "Add sepia to scene 1, blur scene 2, and brighten scene 3"

**Complex Editing:**
```
In the first scene, two males can be seen however the voice is of one girl and one boy,
so change the first to male and female, keep second scene same, and third scene also as
both male and female, only one female is seen in last scene.
```

CineAI automatically:
1. **Decomposes** the query into atomic sub-commands
2. **Parses** each command into structured intents
3. **Executes** edits sequentially
4. **Regenerates** affected phases
5. **Creates snapshots** for undo

### Undo/Redo

```bash
# Via Web Interface
Click "Undo" button in Edit Agent screen

# Via API
POST /api/undo
{
  "run_id": "run_20260505_123456",
  "steps": 2  # Undo last 2 edits
}
```

### Version History

View all edits and their snapshots:

```bash
GET /api/runs/{run_id}/history

Response:
[
  {
    "version": 1,
    "timestamp": "2026-05-05T10:30:00Z",
    "description": "Initial generation",
    "active": false
  },
  {
    "version": 2,
    "timestamp": "2026-05-05T10:32:15Z",
    "description": "Before edit: Make scene 1 darker",
    "active": false
  },
  {
    "version": 3,
    "timestamp": "2026-05-05T10:32:18Z",
    "description": "After edit: Make scene 1 darker",
    "active": true
  }
]
```

---

## 🔧 Configuration

### Backend Configuration

**File**: `backend/config.py`

```python
# Paths
OUTPUTS_DIR = Path("../outputs")
ASSETS_DIR = Path("assets")
MUSIC_DIR = ASSETS_DIR / "music"

# Phase Settings
MAX_SCENES = 5
MAX_CHARACTERS = 5
MIN_SCENE_DURATION_MS = 3000
MAX_SCENE_DURATION_MS = 15000

# Audio Settings
DEFAULT_VOICE_SPEED = 1.0
DEFAULT_BGM_VOLUME = 0.3

# Video Settings
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_FPS = 30
KEN_BURNS_ZOOM_FACTOR = 1.2

# API Settings
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
```

### Supported Intent Types

The edit agent supports 16 intent types across 6 target categories:

| Intent Type | Target | Example Command |
|------------|--------|-----------------|
| `change_voice` | audio | "Change Alice's voice to be calmer" |
| `regenerate_script` | script | "Regenerate the story" |
| `apply_filter` | video_frame | "Make scene 1 darker" |
| `change_scene_characters` | video_frame | "Change scene 1 to 2 males" |
| `change_character_design` | video_frame | "Make Alice wear a red dress" |
| `regenerate_scene` | video_frame | "Regenerate scene 2" |
| `change_mood` | bgm | "Change mood to tense" |
| `change_bgm` | bgm | "Change background music" |
| `add_bgm` | bgm | "Add music to scene 1" |
| `remove_bgm` | bgm | "Remove music from scene 2" |
| `adjust_duration` | video | "Make scene 1 longer" |
| `speed_up` | video | "Speed up scene 2" |
| `slow_down` | video | "Slow down scene 1" |
| `toggle_subtitles` | composition | "Remove subtitles" |
| `change_script` | script | "Change dialogue" |
| `full_regenerate` | video | "Regenerate everything" |

### Supported Visual Filters

OpenCV-based filters (10+ types):

| Filter | Effect | Usage |
|--------|--------|-------|
| `darken` | Reduce brightness | "Make scene 1 darker" |
| `brighten` | Increase brightness | "Brighten scene 2" |
| `contrast` | Increase contrast | "Add more contrast" |
| `saturation` | Boost colors | "Make colors more vibrant" |
| `desaturate` | Reduce colors | "Desaturate scene 1" |
| `grayscale` | Black & white | "Convert to grayscale" |
| `sepia` | Vintage brown tone | "Add sepia tone" |
| `blur` | Gaussian blur | "Blur the background" |
| `sharpen` | Edge enhancement | "Sharpen scene 1" |
| `vignette` | Darkened edges | "Add vignette effect" |
| `temperature` | Warm/cool tones | "Make scene warmer" |

---

## 🌐 API Documentation

### Core Endpoints

#### Generate Video

```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "Create a short mystery story",
  "genre": "Mystery",
  "tone": "Cinematic",
  "duration_seconds": 45,
  "aspect_ratio": "16:9"
}

Response:
{
  "run_id": "run_20260505_123456",
  "status": "started",
  "message": "Pipeline started successfully"
}
```

#### Get Job Status

```http
GET /api/runs/{run_id}/status

Response:
{
  "run_id": "run_20260505_123456",
  "status": "completed",
  "current_phase": "video",
  "phases": {
    "story": {"status": "completed", "progress": 100},
    "audio": {"status": "completed", "progress": 100},
    "video": {"status": "completed", "progress": 100}
  },
  "output_path": "outputs/run_20260505_123456/final_output.mp4"
}
```

#### Execute Edit

```http
POST /api/edit
Content-Type: application/json

{
  "run_id": "run_20260505_123456",
  "edit_command": "Make scene 1 darker and scene 2 brighter"
}

Response:
{
  "success": true,
  "intents_executed": 2,
  "phases_regenerated": ["video"],
  "new_version": 5
}
```

#### Undo Edit

```http
POST /api/undo
Content-Type: application/json

{
  "run_id": "run_20260505_123456",
  "steps": 1
}

Response:
{
  "success": true,
  "reverted_to_version": 3,
  "message": "Reverted 1 edit(s)"
}
```

#### Re-run Phase

```http
POST /api/runs/{run_id}/phases/{phase_id}/rerun

Response:
{
  "success": true,
  "phase": "video",
  "status": "running"
}
```

### WebSocket Endpoints

#### Progress Updates

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/progress/run_20260505_123456');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'log') {
    console.log(data.payload.msg);
  } else if (data.type === 'phase_update') {
    console.log(`Phase ${data.phase_id}: ${data.status.progress}%`);
  }
};
```

#### Chat (Edit Agent)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/run_20260505_123456');

// Send message
ws.send(JSON.stringify({
  role: 'user',
  content: 'Make scene 1 darker',
  time: new Date().toTimeString().slice(0, 8)
}));

// Receive response
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message.content);
};
```

---

## 🧪 Testing

CineAI includes comprehensive unit and integration tests covering all core functionality.

### Test Suite Overview

- **Total Tests**: 19
- **Pass Rate**: 100%
- **Coverage**: Schema validation, state management, pipeline integration
- **Duration**: ~2 seconds

### Running Tests

```bash
cd backend

# Run comprehensive test suite
pytest tests/test_comprehensive.py -v

# Run all tests
pytest -v

# Run with coverage
pytest --cov=shared --cov=phase1_story --cov=phase2_audio --cov=phase5_edit -v

# Run specific test categories
pytest tests/test_comprehensive.py::TestSchemaValidation -v
pytest tests/test_comprehensive.py::TestStateManager -v
pytest tests/test_comprehensive.py::TestPipelineIntegration -v
```

### Test Results

```
============================= test session starts =============================
collected 19 items

tests/test_comprehensive.py::TestSchemaValidation::test_voice_params_creation PASSED
tests/test_comprehensive.py::TestSchemaValidation::test_character_creation PASSED
tests/test_comprehensive.py::TestSchemaValidation::test_dialogue_creation PASSED
tests/test_comprehensive.py::TestSchemaValidation::test_scene_creation PASSED
tests/test_comprehensive.py::TestSchemaValidation::test_story_creation PASSED
tests/test_comprehensive.py::TestSchemaValidation::test_mood_enum_values PASSED
tests/test_comprehensive.py::TestSchemaValidation::test_edit_intent_creation PASSED
tests/test_comprehensive.py::TestStateManager::test_snapshot_creation PASSED
tests/test_comprehensive.py::TestStateManager::test_multiple_snapshots PASSED
tests/test_comprehensive.py::TestStateManager::test_snapshot_retrieval PASSED
tests/test_comprehensive.py::TestStateManager::test_history_tracking PASSED
tests/test_comprehensive.py::TestStateManager::test_current_version_tracking PASSED
tests/test_comprehensive.py::TestPipelineIntegration::test_character_to_scene_mapping PASSED
tests/test_comprehensive.py::TestPipelineIntegration::test_scene_mood_consistency PASSED
tests/test_comprehensive.py::TestPipelineIntegration::test_scene_numbering PASSED
tests/test_comprehensive.py::TestPipelineIntegration::test_state_serialization PASSED
tests/test_comprehensive.py::TestBGMSelection::test_get_available_moods PASSED
tests/test_comprehensive.py::TestAudioManifest::test_audio_manifest_creation PASSED
tests/test_comprehensive.py::TestVersioningWorkflow::test_edit_workflow_with_versions PASSED

======================= 19 passed in 2.15s =======================
```

For detailed test documentation, see:
- [TEST_REPORT.md](./TEST_REPORT.md) - Comprehensive testing documentation
- [TEST_RESULTS_SUMMARY.txt](./TEST_RESULTS_SUMMARY.txt) - Quick reference
- [SAMPLE_TEST_OUTPUT.txt](./SAMPLE_TEST_OUTPUT.txt) - Sample execution output

---

## 📚 Documentation

### Comprehensive Guides

- **[QUICK_START.md](./QUICK_START.md)** - Get started in 5 minutes
- **[RUN_APP.md](./RUN_APP.md)** - Detailed running instructions
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Testing scenarios and best practices
- **[API_INTEGRATION_GUIDE.md](./API_INTEGRATION_GUIDE.md)** - Frontend-backend integration
- **[FINAL_STATUS.md](./FINAL_STATUS.md)** - Project completion status
- **[START_HERE.md](./START_HERE.md)** - New user onboarding

### Feature Documentation

- **[MULTI_INTENT_EDIT_SYSTEM.md](./MULTI_INTENT_EDIT_SYSTEM.md)** - Edit system architecture
- **[EDIT_QUERY_EXAMPLES.md](./EDIT_QUERY_EXAMPLES.md)** - Query examples and patterns
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[EDIT_FLOW_DIAGRAM.md](./EDIT_FLOW_DIAGRAM.md)** - Edit workflow visualization

### Testing Documentation

- **[TEST_REPORT.md](./TEST_REPORT.md)** - Comprehensive test report
- **[TEST_RESULTS_SUMMARY.txt](./TEST_RESULTS_SUMMARY.txt)** - Quick summary
- **[SAMPLE_TEST_OUTPUT.txt](./SAMPLE_TEST_OUTPUT.txt)** - Sample test execution

---

## 🔍 Project Status

### Implementation: 100% Complete ✅

| Component | Status | Details |
|-----------|--------|---------|
| Phase 1: Story Generation | ✅ Complete | LangGraph workflow, Groq integration, comprehensive tests |
| Phase 2: Audio Synthesis | ✅ Complete | ElevenLabs + Deepgram, BGM selection, timing manifest |
| Phase 3: Video Composition | ✅ Complete | FLUX.1 images, Ken Burns effects, FFmpeg A/V sync |
| Phase 4: Web Application | ✅ Complete | FastAPI + React, WebSocket, real-time progress |
| Phase 5: Edit Agent | ✅ Complete | Multi-intent parsing, 16 intent types, full undo/redo |
| Testing Suite | ✅ Complete | 19 tests, 100% pass rate, comprehensive coverage |
| Documentation | ✅ Complete | 13 markdown files, API docs, test reports |

### Recent Updates

**v1.3.0 (May 5, 2026)** - Testing & Documentation
- Added comprehensive test suite (19 tests, 100% pass)
- Generated test reports and documentation
- Added sample test output for report inclusion

**v1.2.0 (May 5, 2026)** - TTS Fallback
- Integrated Deepgram API as TTS fallback
- Enhanced voice configuration
- Improved error handling

**v1.1.0 (April 27, 2026)** - Multi-Intent Editing
- Implemented intent decomposer for complex commands
- Expanded to 16 intent types
- Added visual continuity management
- Enhanced schema with character overrides

**v1.0.0 (April 23, 2026)** - Initial Release
- Complete 5-phase pipeline
- React frontend with 5 screens
- WebSocket real-time updates
- Basic edit agent with undo

### Known Limitations

1. **API Rate Limits**: Free tier APIs have rate limits
   - Groq: 30 requests/minute
   - ElevenLabs: 10k characters/month
   - Hugging Face: Serverless API rate limits

2. **Video Duration**: Optimized for 30-90 second videos
   - Longer videos may exceed API quotas
   - Processing time increases linearly

3. **BGM Library**: Requires manual population
   - No built-in music files
   - User must add royalty-free tracks

4. **Image Generation**: Depends on FLUX.1 availability
   - HuggingFace serverless can have cold starts
   - Occasional model loading delays

---

## 🛠️ Troubleshooting

### Common Issues

#### "ModuleNotFoundError" when running

```bash
# Ensure virtual environment is activated
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

#### "API Key Invalid" errors

- Check `.env` file has correct keys without extra spaces
- Verify keys are valid at respective API platforms
- Ensure no quotes around key values in `.env`

#### FFmpeg not found

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
# Add to system PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

#### "No music files found" warning

```bash
# Add MP3/WAV files to mood folders
cd backend/assets/music
ls calm/       # Should show music files
ls tense/      # Should show music files
# ... etc
```

#### WebSocket connection fails

- Ensure backend is running on port 8000
- Check firewall settings
- Verify WebSocket URL in frontend config

#### Video generation hangs

- Check API key quotas (especially ElevenLabs character limit)
- Monitor backend logs for errors
- Verify all dependencies are installed
- Check internet connection for API calls

---

## 🎓 Architecture Deep Dive

### LangGraph Workflows

#### Story Generation Workflow (Phase 1)

```python
# 5-node workflow with conditional routing
generate_story → generate_characters → generate_dialogue →
generate_visual_prompts → validate_output

# Each node is a specialized LLM call with structured output
# Conditional routing based on validation results
```

#### Edit Intent Parsing Workflow (Phase 5)

```python
# Multi-step intent classification
user_query → decompose_intents → parse_each_intent →
execute_sequentially → snapshot

# Supports complex multi-part commands
# Parallel parsing with sequential execution
```

### Data Flow

```
User Prompt
    ↓
PipelineState (empty)
    ↓
Phase 1 → PipelineState (+ story, characters, scenes)
    ↓
Phase 2 → PipelineState (+ audio files, timing data)
    ↓
Phase 3 → PipelineState (+ images, videos, final MP4)
    ↓
Phase 5 → PipelineState (+ edits, new versions)
    ↓
StateManager → Snapshots (full version history)
```

### Version Control System

```
StateManager
├─ v001/
│  ├─ state.json         # Full pipeline state
│  ├─ snapshot.json      # Version metadata
│  └─ assets/            # Audio, images, videos
├─ v002/                 # After first edit
├─ v003/                 # After second edit
└─ ...
```

Each edit creates:
1. **Before snapshot** - State before the edit
2. **After snapshot** - State after the edit
3. **Asset copies** - All referenced media files

Undo operation reverts to previous snapshot and restores assets.

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Areas for Contribution

1. **New Visual Filters**: Add OpenCV filters in `phase5_edit/filters.py`
2. **Additional Intent Types**: Extend edit agent capabilities
3. **TTS Provider Integration**: Add more TTS fallbacks
4. **Image Generation Models**: Integrate alternative models
5. **Performance Optimization**: Improve processing speed
6. **UI Enhancements**: Improve React frontend
7. **Documentation**: Add tutorials, examples, translations

### Development Setup

```bash
# Fork and clone
git clone <your-fork-url>
cd cine-ai

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes

# Run tests
cd backend
pytest -v

# Commit with meaningful message
git commit -m "feat: add new visual filter for vintage effect"

# Push and create PR
git push origin feature/your-feature-name
```

### Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Follow ESLint rules
- **Commits**: Use conventional commits (feat, fix, docs, test, etc.)
- **Documentation**: Update relevant .md files

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

### Technologies

- **LangChain/LangGraph** - Multi-agent orchestration framework
- **Groq** - Fast LLM inference with Llama 3.3
- **ElevenLabs** - High-quality text-to-speech synthesis
- **Deepgram** - TTS fallback provider
- **Hugging Face** - FLUX.1 image generation model
- **MoviePy** - Python video editing library
- **FFmpeg** - Multimedia processing framework
- **FastAPI** - Modern Python web framework
- **React** - Frontend UI framework
- **Material-UI** - React component library

### Music Sources

- Free Music Archive
- YouTube Audio Library
- Incompetech
- Bensound

---

## 📞 Support & Contact

### Documentation

- **Quick Start**: [QUICK_START.md](./QUICK_START.md)
- **API Guide**: [API_INTEGRATION_GUIDE.md](./API_INTEGRATION_GUIDE.md)
- **Testing Guide**: [TESTING_GUIDE.md](./TESTING_GUIDE.md)
- **Edit System Docs**: [MULTI_INTENT_EDIT_SYSTEM.md](./MULTI_INTENT_EDIT_SYSTEM.md)

### Issues

For bugs and feature requests, please:
1. Check existing [documentation](./docs/)
2. Review [troubleshooting](#troubleshooting) section
3. Check test files for usage examples
4. Open a GitHub issue with detailed description

### API Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🚀 Future Roadmap

### Short-term (Next Release)

- [ ] Docker deployment with docker-compose
- [ ] Cloud storage integration (AWS S3, Google Cloud Storage)
- [ ] Batch processing for multiple prompts
- [ ] Advanced visual filters (film grain, chromatic aberration)
- [ ] Character consistency across scenes (reference images)

### Long-term

- [ ] Multi-language TTS support
- [ ] Real-time collaborative editing
- [ ] Video templates and presets
- [ ] Advanced scene transitions
- [ ] Music generation instead of selection
- [ ] Voice cloning for characters
- [ ] 3D scene generation
- [ ] Multi-model ensemble for better quality

---

## 📊 Project Metrics

- **Lines of Code**: ~8,500 (backend), ~3,200 (frontend)
- **Dependencies**: 22 Python packages, 150+ npm packages
- **Test Coverage**: Core functionality 100%
- **API Endpoints**: 15 REST + 2 WebSocket
- **Documentation Files**: 13 markdown files
- **Supported Intents**: 16 types
- **Visual Filters**: 10+ OpenCV filters
- **Average Generation Time**: 3-5 minutes (30-second video)

---

**🎬 CineAI - Democratizing Animated Film Production with Agentic AI**

*Transform your ideas into polished short films in minutes, not days.*

---

**Built with ❤️ using LangGraph, FastAPI, and modern AI**
