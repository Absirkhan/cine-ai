# Quick Command Reference

## 🚀 Testing & Running

### Run Full Pipeline Demo
```bash
cd backend
python test_pipeline.py
```

### Run Unit Tests
```bash
cd backend
pytest phase1_story/tests.py -v          # Test Phase 1
pytest phase2_audio/tests.py -v          # Test Phase 2
pytest -v                                 # Test all phases
```

### Check BGM Library Status
```bash
cd backend
python -m phase2_audio.music_selector
```

---

## 🔧 Environment Setup

### Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## 📁 File & Directory Commands

### View Output Directory
```bash
# Windows
dir ..\outputs\run_* /s

# macOS/Linux
ls -la ../outputs/run_*/
```

### Play Generated Audio
```bash
# Windows
start ..\outputs\run_20260423_160000\assets\audio_scene_001_dialogue_00.mp3

# macOS
open ../outputs/run_20260423_160000/assets/audio_scene_001_dialogue_00.mp3

# Linux
xdg-open ../outputs/run_20260423_160000/assets/audio_scene_001_dialogue_00.mp3
```

### View JSON Output
```bash
# Windows
type ..\outputs\run_*\phase1_output.json

# macOS/Linux
cat ../outputs/run_*/phase1_output.json | jq .  # Pretty print with jq
```

---

## 🧪 Testing Specific Components

### Test Story Generation Only
```python
# Create test_story.py
from phase1_story.agent import StoryAgent

agent = StoryAgent()
state = agent.generate(
    "A robot learns to paint",
    {"genre": "Drama", "tone": "Warm", "duration": "30s", "aspect": "16:9"}
)
print(f"Title: {state.story.title}")
```

Run:
```bash
python test_story.py
```

### Test BGM Selection
```python
# Create test_bgm.py
from phase2_audio.music_selector import select_bgm_for_scene, get_available_moods
from shared.schema import MoodType

print("Available moods:", get_available_moods())
bgm = select_bgm_for_scene(MoodType.CALM, "test_run", "scene_001")
print(f"Selected: {bgm}")
```

Run:
```bash
python test_bgm.py
```

---

## 🔍 Debugging Commands

### Check Python Version
```bash
python --version
```

### Check Installed Packages
```bash
pip list | grep langchain
pip list | grep groq
pip list | grep elevenlabs
```

### Verify Environment Variables
```bash
# Windows
type ..\.env

# macOS/Linux
cat ../.env
```

### Test API Keys
```python
# Create test_apis.py
import config

try:
    config.validate_config()
    print("All API keys configured!")
except ValueError as e:
    print(f"Missing: {e}")
```

Run:
```bash
python test_apis.py
```

---

## 📊 Project Information

### Count Lines of Code
```bash
# Windows (PowerShell)
Get-ChildItem -Recurse -Include *.py | Get-Content | Measure-Object -Line

# macOS/Linux
find . -name "*.py" -not -path "./venv/*" | xargs wc -l
```

### View Project Structure
```bash
# Windows
tree /F /A

# macOS/Linux
tree -L 3
```

### Check Git Status
```bash
git status
git log --oneline -5
```

---

## 🧹 Cleanup Commands

### Remove Output Files
```bash
# Windows
rmdir /s /q ..\outputs

# macOS/Linux
rm -rf ../outputs/*
```

### Clean Python Cache
```bash
# Windows
del /s /q *.pyc
rmdir /s /q __pycache__

# macOS/Linux
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
```

### Reset Database (if needed)
```bash
# Windows
del cineai.db

# macOS/Linux
rm -f cineai.db
```

---

## 🎯 Quick Workflows

### Full Test Workflow
```bash
cd backend
pytest -v                    # Run all tests
python test_pipeline.py      # Run full demo
cd ..\outputs
dir run_* /s                 # View all outputs
```

### Development Workflow
```bash
cd backend
# 1. Make code changes
# 2. Run specific tests
pytest phase1_story/tests.py -v
# 3. Test integration
python test_pipeline.py
# 4. Check outputs
start ..\outputs\run_*\assets\
```

### New Session Workflow
```bash
cd backend
venv\Scripts\activate         # Activate environment
git pull                      # Get latest changes
pip install -r requirements.txt  # Update deps
pytest -v                     # Verify all tests pass
```

---

## 📝 Common Python Operations

### Interactive Python Testing
```bash
cd backend
python

# In Python shell:
>>> from phase1_story.agent import StoryAgent
>>> from shared import schema
>>> import config
>>>
>>> # Test code here
>>> exit()
```

### Check Module Imports
```bash
python -c "import langchain; print('LangChain OK')"
python -c "import langgraph; print('LangGraph OK')"
python -c "import groq; print('Groq OK')"
python -c "from elevenlabs import ElevenLabs; print('ElevenLabs OK')"
```

---

## 🛠️ Maintenance Commands

### Update Project Documentation
```bash
# After making changes, update:
# 1. .claude/project_context.md
# 2. IMPLEMENTATION_STATUS.md
# 3. Git commit with message
git add .
git commit -m "Implement Phase 3: Video generation"
git push
```

### Backup Outputs
```bash
# Windows
xcopy ..\outputs backup\outputs /E /I

# macOS/Linux
cp -r ../outputs/ backup/outputs/
```

### Generate Requirements
```bash
pip freeze > requirements.txt
```

---

## 🎓 Learning Commands

### View Code Structure
```bash
# Count files per phase
ls phase*/ | wc -l

# View file sizes
ls -lh phase*/*.py
```

### Read Source Code
```bash
# Windows
type shared\schema.py

# macOS/Linux
cat shared/schema.py
less shared/schema.py  # Scrollable view
```

---

## ⚡ Power User Tips

### Run with Different Configs
```bash
# Use custom env file
GROQ_API_KEY=xxx python test_pipeline.py

# Run with debug mode
DEBUG=true python test_pipeline.py
```

### Batch Testing
```bash
# Run multiple tests in sequence
for i in 1 2 3; do
  python test_pipeline.py < test_input_$i.txt
done
```

### Monitor Resource Usage
```bash
# Windows
python test_pipeline.py & tasklist | findstr python

# macOS/Linux
python test_pipeline.py &
top -p $!
```

---

## 📞 Quick Reference Links

- **Start Testing:** `python test_pipeline.py`
- **Run Tests:** `pytest -v`
- **Check BGM:** `python -m phase2_audio.music_selector`
- **View Docs:** See [START_HERE.md](START_HERE.md)
- **Troubleshoot:** See [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

**Pro Tip:** Bookmark this file for quick command lookup! 📌
