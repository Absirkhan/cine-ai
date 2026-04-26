# 🚀 How to Run the CineAI Web Application

## Quick Start (30 seconds)

```bash
cd backend
python main.py
```

Then open your browser to:
**http://localhost:8000**

That's it! 🎉

---

## Detailed Steps

### 1. Make Sure Environment is Ready

```bash
cd backend

# Check you're in the virtual environment
# You should see (venv) in your terminal

# If not, activate it:
venv\Scripts\activate  # Windows
```

### 2. Install/Update Dependencies (if needed)

```bash
pip install -r requirements.txt
```

### 3. Verify Configuration

Make sure your `.env` file has all API keys:

```bash
# Windows
type ..\.env

# Should show:
# GROQ_API_KEY=gsk_...
# ELEVENLABS_API_KEY=sk_...
# HUGGINGFACE_API_KEY=hf_...
```

### 4. Start the Server

```bash
python main.py
```

You should see:

```
================================================================================
🎬 CineAI - AI-Powered Video Generation System
================================================================================

🚀 Starting server on http://0.0.0.0:8000

📱 Frontend: http://localhost:8000
📡 API Docs: http://localhost:8000/docs
🔌 WebSocket: ws://localhost:8000/ws/progress/{run_id}

================================================================================
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 5. Open the Web App

Open your browser and go to:

**http://localhost:8000**

You'll see the CineAI home screen! ✨

---

## Using the Web App

### Home Screen (Generate)

1. **Enter your story prompt** in the text area
   - Example: "A lonely astronaut discovers a glowing crystal on Mars"

2. **Select parameters:**
   - **Genre:** Sci-Fi, Fantasy, Drama, Thriller, Comedy, Documentary
   - **Tone:** Cinematic, Playful, Dark, Warm, Suspense
   - **Duration:** 30s, 60s, 90s, 2 min
   - **Aspect Ratio:** 16:9, 9:16, 1:1

3. **Click "Generate Video"**

4. **Watch the progress** in real-time:
   - Phase 1: Story generation (~30-60 sec)
   - Phase 2: Audio generation (~1-2 min)
   - Phase 3: Video generation (~3-5 min)

5. **Preview your video** in the UI player

6. **Edit with natural language:**
   - "Make scene 1 darker"
   - "Add sepia tone to scene 2"
   - "Change music to tense"

7. **Undo edits** if needed

8. **Download final video** as MP4

9. **Check all outputs** in `outputs/run_YYYYMMDD_HHMMSS/`

---

## API Endpoints Available

### Generate Video
```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "Your story here",
  "genre": "Sci-Fi",
  "tone": "Cinematic",
  "duration": "60s",
  "aspect": "16:9"
}
```

### Get Run Status
```http
GET /api/runs/{run_id}/status
```

### Get Generated Output
```http
GET /api/runs/{run_id}/output
```

### Get Asset (Audio/Video)
```http
GET /api/runs/{run_id}/assets/{filename}
```

### Execute Edit
```http
POST /api/edit
Content-Type: application/json

{
  "run_id": "run_20260424_120000",
  "command": "Make scene 1 darker"
}
```

### Undo Edit
```http
POST /api/undo
Content-Type: application/json

{
  "run_id": "run_20260424_120000",
  "steps": 2
}
```

### Get Edit History
```http
GET /api/runs/{run_id}/history
```

### WebSocket Progress
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/progress/run_123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.message);  // Progress updates
};
```

---

## Testing the API (Alternative to Frontend)

### Using curl:

```bash
# Generate video
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A robot learns to paint","genre":"Drama","tone":"Warm","duration":"30s","aspect":"16:9"}'

# Get run status
curl http://localhost:8000/api/runs/run_20260423_160000/status

# List all runs
curl http://localhost:8000/api/runs
```

### Using Python:

```python
import requests

# Generate video
response = requests.post('http://localhost:8000/api/generate', json={
    "prompt": "A robot learns to paint",
    "genre": "Drama",
    "tone": "Warm",
    "duration": "30s",
    "aspect": "16:9"
})

print(response.json())
# {'run_id': 'run_20260423_160000', 'status': 'started', 'message': '...'}

# Get status
run_id = response.json()['run_id']
status = requests.get(f'http://localhost:8000/api/runs/{run_id}/status')
print(status.json())
```

---

## Interactive API Documentation

FastAPI provides automatic interactive docs:

**Swagger UI:** http://localhost:8000/docs

This lets you:
- See all API endpoints
- Test endpoints directly in browser
- View request/response schemas
- No code needed!

---

## Development Mode

### Run with Auto-Reload

Edit `.env` and set:
```env
DEBUG=true
```

Then:
```bash
python main.py
```

Now the server will auto-reload when you edit code!

### View Logs

All progress updates and errors are logged to console:

```
INFO:     Application startup complete.
Pipeline started: run_20260423_160000
Phase 1 progress: 20% - Generating story structure...
Phase 1 complete!
Phase 2 progress: 50% - Synthesizing voices...
```

---

## Troubleshooting

### Port 8000 Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>

# Or use different port:
# Edit .env:
PORT=8001
```

### Frontend Not Loading

**Error:** Blank page or 404

**Solution:**
- Make sure `frontend/` directory exists next to `backend/`
- Check `frontend/index.html` exists
- Try accessing http://localhost:8000/index.html directly

### WebSocket Connection Failed

**Error:** WebSocket connection refused

**Solution:**
- Make sure server is running on `0.0.0.0`, not `localhost` only
- Check firewall settings
- Verify WebSocket URL uses `ws://` not `wss://`

### API Returns 500 Error

**Check server logs** in the terminal running `python main.py`

Common issues:
- Missing API keys (.env file)
- Missing dependencies (`pip install -r requirements.txt`)
- BGM library empty (run `python -m phase2_audio.music_selector`)

---

## Checking What's Running

### Verify Server is Running

```bash
curl http://localhost:8000/
# Should return: {"status":"running","app":"CineAI",...}
```

### Check Active Runs

```bash
curl http://localhost:8000/api/runs
# Lists all pipeline runs
```

### View Generated Files

```bash
# Windows
dir ..\outputs\run_*\assets

# macOS/Linux
ls -la ../outputs/run_*/assets/
```

---

## Stopping the Server

Press **Ctrl+C** in the terminal running `python main.py`

---

## ✅ ALL PHASES NOW WORKING!

### 🎉 Complete Feature List (100% Implemented)

**Phase 1: Story Generation**
- ✅ Story generation with LangGraph + Groq
- ✅ Character creation with voice parameters
- ✅ Scene-by-scene breakdown
- ✅ Dialogue generation
- ✅ Visual prompt engineering

**Phase 2: Audio Generation**
- ✅ ElevenLabs TTS voice synthesis
- ✅ Mood-based BGM selection
- ✅ Audio timing manifest
- ✅ Voice ID mapping per character

**Phase 3: Video Composition**
- ✅ FLUX.1 image generation (Hugging Face)
- ✅ Ken Burns effects (zoom/pan animation)
- ✅ A/V synchronization with FFmpeg
- ✅ Final MP4 export with all layers

**Phase 4: Web Application**
- ✅ FastAPI backend with CORS
- ✅ WebSocket real-time progress
- ✅ Complete REST API endpoints
- ✅ React frontend integration
- ✅ File serving (audio/video)
- ✅ Run status tracking

**Phase 5: Edit Agent & Undo**
- ✅ Natural language intent parsing
- ✅ 10+ OpenCV filters (darken, brighten, sepia, etc.)
- ✅ BGM mood changes
- ✅ Full undo/redo with asset versioning

### What You Get From a Full Pipeline Run

When you generate a video now:
1. ✅ Complete story with scenes and characters
2. ✅ AI-generated voice audio for all dialogue
3. ✅ Background music matched to scene moods
4. ✅ AI-generated images for each scene (FLUX.1)
5. ✅ Animated video clips with Ken Burns effects
6. ✅ Final composed MP4 video
7. ✅ Real-time progress updates
8. ✅ Natural language editing capabilities
9. ✅ Full undo/redo functionality
10. ✅ Complete version history

---

## Example Full Workflow

```bash
# 1. Start server
cd backend
python main.py

# 2. Open browser
# Go to http://localhost:8000

# 3. Enter prompt
"A robot discovers emotions while painting in a quiet studio"

# 4. Select parameters
Genre: Drama
Tone: Warm
Duration: 30s
Aspect: 16:9

# 5. Click "Generate Video"

# 6. Wait 2-3 minutes

# 7. Check outputs
cd ..\outputs
dir run_* /s

# 8. Play generated audio
start run_20260423_160000\assets\audio_scene_001_dialogue_00.mp3

# 9. View JSON data
type run_20260423_160000\phase2_output.json
```

---

## Pro Tips

### 1. Keep Terminal Open
Keep the terminal with `python main.py` visible to see real-time logs

### 2. Test API First
Before using the UI, test with curl to verify backend works

### 3. Check Outputs
After each run, check the `outputs/run_*/` directory to see all generated files

### 4. Monitor API Credits
- ElevenLabs free tier: 10,000 characters/month
- Check usage at https://elevenlabs.io
- Each 60s video uses ~500-1000 characters

### 5. Use Short Durations for Testing
Start with 30s videos to save API credits while testing

---

## What's Next?

🎉 **All phases are complete!** Here's what to do:

1. ✅ Test the complete pipeline end-to-end
2. ✅ Try different story prompts and genres
3. ✅ Test all edit commands
4. ✅ Verify undo/redo functionality
5. ✅ Download and review final videos

**For your semester project:**
- 📹 Create demo video (5-7 minutes)
- 📝 Write final report (8-12 pages)
- 📊 Prepare presentation slides (15-20 slides)
- 🗓️ **Deadline: May 5, 2026**

---

## 🎬 Ready to Run!

```bash
cd backend
python main.py
```

**Open http://localhost:8000 and start creating! 🚀**
