# 🚀 QUICK START - Run Your CineAI App in 30 Seconds

## Windows

```bash
cd backend
run_server.bat
```

## macOS/Linux

```bash
cd backend
./run_server.sh
```

## Or Manually

```bash
cd backend
python main.py
```

---

## Then Open Your Browser

**http://localhost:8000**

---

## What You'll See

1. **Home Screen** - Enter your story prompt and parameters
2. **Real-time Progress** - Watch AI generate your story and voices
3. **Generated Outputs** - Audio files and JSON data

---

## Example First Run

1. Start server (as above)
2. Open http://localhost:8000
3. Use default prompt or enter: "A robot discovers emotions while painting"
4. Click "Generate Video"
5. Wait 2-3 minutes
6. Check `outputs/run_*/assets/` for audio files

---

## Troubleshooting

### Server won't start?
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Port already in use?
Edit `.env` and change `PORT=8001`

### Frontend not loading?
Make sure you're in the `backend` directory when running `python main.py`

---

## Full Documentation

- **Detailed Guide:** [RUN_APP.md](RUN_APP.md)
- **Testing:** [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Commands:** [COMMANDS.md](COMMANDS.md)

---

**That's it! Start creating AI-powered videos! 🎬**
