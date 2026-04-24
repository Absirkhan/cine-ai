"""
CineAI FastAPI Application
Main entry point for the web application
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
from pathlib import Path
from datetime import datetime

import config
from orchestrator import PipelineOrchestrator

# Initialize FastAPI app
app = FastAPI(
    title="CineAI",
    description="AI-Powered Animated Video Generation System",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = PipelineOrchestrator()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[run_id] = websocket

    def disconnect(self, run_id: str):
        if run_id in self.active_connections:
            del self.active_connections[run_id]

    async def send_progress(self, run_id: str, data: dict):
        if run_id in self.active_connections:
            try:
                await self.active_connections[run_id].send_json(data)
            except:
                self.disconnect(run_id)

manager = ConnectionManager()


# Request/Response Models
class GenerateRequest(BaseModel):
    prompt: str
    genre: str = "Sci-Fi"
    tone: str = "Cinematic"
    duration: str = "60s"
    aspect: str = "16:9"


class GenerateResponse(BaseModel):
    run_id: str
    status: str
    message: str


class PhaseRerunRequest(BaseModel):
    run_id: str
    phase: str


class EditRequest(BaseModel):
    run_id: str
    command: str


class UndoRequest(BaseModel):
    run_id: str
    steps: int = 1


# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "running",
        "app": "CineAI",
        "version": "0.1.0",
        "phases_available": ["script", "audio", "video", "edit"]
    }


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_video(request: GenerateRequest):
    """
    Start video generation pipeline
    Returns run_id for tracking progress via WebSocket
    """
    try:
        # Start pipeline in background
        run_id = await orchestrator.start_pipeline(
            user_prompt=request.prompt,
            params={
                "genre": request.genre,
                "tone": request.tone,
                "duration": request.duration,
                "aspect": request.aspect
            },
            progress_callback=lambda data: asyncio.create_task(
                manager.send_progress(run_id, data)
            ) if run_id else None
        )

        return GenerateResponse(
            run_id=run_id,
            status="started",
            message="Pipeline started successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/runs/{run_id}/status")
async def get_run_status(run_id: str):
    """Get current status of a pipeline run"""
    try:
        status = orchestrator.get_run_status(run_id)
        if not status:
            raise HTTPException(status_code=404, detail="Run not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/runs/{run_id}/output")
async def get_run_output(run_id: str):
    """Get the output JSON for a completed run"""
    try:
        output_file = config.OUTPUTS_DIR / run_id / "phase2_output.json"
        if not output_file.exists():
            # Try phase1 output
            output_file = config.OUTPUTS_DIR / run_id / "phase1_output.json"

        if not output_file.exists():
            raise HTTPException(status_code=404, detail="Output not found")

        with open(output_file, "r") as f:
            return json.load(f)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/runs/{run_id}/assets/{asset_name}")
async def get_asset(run_id: str, asset_name: str):
    """Serve generated assets (audio, images, videos)"""
    try:
        asset_path = config.OUTPUTS_DIR / run_id / "assets" / asset_name

        if not asset_path.exists():
            raise HTTPException(status_code=404, detail="Asset not found")

        return FileResponse(asset_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/phases/rerun")
async def rerun_phase(request: PhaseRerunRequest):
    """Re-run a specific phase of the pipeline"""
    try:
        result = await orchestrator.rerun_phase(
            run_id=request.run_id,
            phase=request.phase,
            progress_callback=lambda data: asyncio.create_task(
                manager.send_progress(request.run_id, data)
            )
        )

        return {
            "status": "success",
            "phase": request.phase,
            "message": f"Phase {request.phase} re-run successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/progress/{run_id}")
async def websocket_progress(websocket: WebSocket, run_id: str):
    """
    WebSocket endpoint for real-time progress updates
    """
    await manager.connect(run_id, websocket)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except WebSocketDisconnect:
                break

    except Exception as e:
        print(f"WebSocket error: {e}")

    finally:
        manager.disconnect(run_id)


@app.get("/api/runs")
async def list_runs():
    """List all pipeline runs"""
    try:
        runs = []
        if config.OUTPUTS_DIR.exists():
            for run_dir in config.OUTPUTS_DIR.iterdir():
                if run_dir.is_dir() and run_dir.name.startswith("run_"):
                    # Try to get status
                    status_file = run_dir / "phase3_output.json"
                    if not status_file.exists():
                        status_file = run_dir / "phase2_output.json"
                    if not status_file.exists():
                        status_file = run_dir / "phase1_output.json"

                    if status_file.exists():
                        with open(status_file, "r") as f:
                            data = json.load(f)
                            runs.append({
                                "run_id": run_dir.name,
                                "timestamp": data.get("timestamp"),
                                "prompt": data.get("user_prompt"),
                                "status": "completed"
                            })

        return {"runs": runs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/edit")
async def execute_edit(request: EditRequest):
    """Execute natural language edit command"""
    try:
        result = await orchestrator.execute_edit(
            run_id=request.run_id,
            edit_command=request.command,
            progress_callback=lambda data: asyncio.create_task(
                manager.send_progress(request.run_id, data)
            )
        )

        return {
            "status": "success",
            "message": "Edit executed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/undo")
async def undo_edit(request: UndoRequest):
    """Undo last N edits"""
    try:
        state = await orchestrator.undo_edit(
            run_id=request.run_id,
            steps=request.steps
        )

        return {
            "status": "success",
            "message": f"Undone {request.steps} edit(s)",
            "current_version": state.version if state else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/runs/{run_id}/history")
async def get_edit_history(run_id: str):
    """Get edit history for a run"""
    try:
        from shared.state_manager import StateManager

        state_manager = StateManager(run_id)
        history = state_manager.get_history()

        return {"history": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Test endpoints for individual phases
@app.post("/api/test/image")
async def test_image_generation(prompt: str = "a beautiful sunset over mountains"):
    """Test image generation independently without running full pipeline"""
    try:
        from phase3_video.image_generator import ImageGenerator

        generator = ImageGenerator()
        run_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'='*60}")
        print(f"Testing image generation with prompt: {prompt}")
        print(f"{'='*60}\n")

        image_path = generator.generate_image(
            prompt=prompt,
            run_id=run_id,
            scene_id="test_scene",
            retries=3
        )

        if image_path:
            return {
                "status": "success",
                "image_path": image_path,
                "message": "Image generated successfully",
                "asset_url": f"/api/runs/{run_id}/assets/{Path(image_path).name}"
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to generate image after retries"
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# Serve frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    # Serve index.html at root
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend index.html"""
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Frontend not found"}

    # Serve static files
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("🎬 CineAI - AI-Powered Video Generation System")
    print("=" * 80)
    print(f"\n🚀 Starting server on http://{config.HOST}:{config.PORT}")
    print(f"\n📱 Frontend: http://localhost:{config.PORT}")
    print(f"📡 API Docs: http://localhost:{config.PORT}/docs")
    print(f"🔌 WebSocket: ws://localhost:{config.PORT}/ws/progress/{{run_id}}")
    print("\n" + "=" * 80)

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )
