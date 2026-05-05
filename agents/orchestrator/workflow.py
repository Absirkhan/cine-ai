"""
Pipeline Orchestrator
Manages execution of all phases and state transitions
"""

import asyncio
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import json

import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.story_agent.agent import StoryAgent
from agents.audio_agent.generator import AudioGenerator
from agents.video_agent.video_generator import VideoGenerator
from agents.edit_agent.edit_agent import EditAgent
from state_manager.state_manager import StateManager
from state_manager.schema import PipelineState
from state_manager.utils import generate_run_id
import config


class PipelineOrchestrator:
    """Orchestrates the entire video generation pipeline"""

    def __init__(self):
        self.active_runs: Dict[str, Dict[str, Any]] = {}
        self.story_agent = None
        self.audio_generator = None
        self.video_generator = None
        self.edit_agent = None

    async def start_pipeline(
        self,
        user_prompt: str,
        params: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        Start a new pipeline run

        Args:
            user_prompt: User's story prompt
            params: Generation parameters (genre, tone, duration, aspect)
            progress_callback: Optional callback for progress updates

        Returns:
            run_id for tracking progress
        """
        run_id = generate_run_id()

        # Initialize run tracking
        self.active_runs[run_id] = {
            "status": "running",
            "phase": "initializing",
            "progress": 0,
            "started_at": datetime.utcnow().isoformat(),
            "user_prompt": user_prompt,
            "params": params
        }

        # Start pipeline in background
        asyncio.create_task(self._run_pipeline(run_id, user_prompt, params, progress_callback))

        return run_id

    async def _run_pipeline(
        self,
        run_id: str,
        user_prompt: str,
        params: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ):
        """Execute the pipeline phases sequentially"""

        try:
            # Phase 1: Story Generation
            await self._update_progress(run_id, "script", 0, "Initializing story generation...", progress_callback)

            if not self.story_agent:
                self.story_agent = StoryAgent()

            await self._update_progress(run_id, "script", 10, "Generating story structure...", progress_callback)

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            state = await loop.run_in_executor(
                None,
                self.story_agent.generate,
                user_prompt,
                params,
                run_id  # Pass the run_id to story agent
            )

            await self._update_progress(run_id, "script", 100, "Story generation complete!", progress_callback)

            # Save Phase 1 output
            self._save_phase_output(run_id, "phase1", state)

            # Phase 2: Audio Generation
            await self._update_progress(run_id, "audio", 0, "Initializing audio generation...", progress_callback)

            if not self.audio_generator:
                self.audio_generator = AudioGenerator()

            await self._update_progress(run_id, "audio", 20, "Synthesizing character voices...", progress_callback)

            # Run in executor
            state = await loop.run_in_executor(
                None,
                self.audio_generator.generate,
                state
            )

            await self._update_progress(run_id, "audio", 100, "Audio generation complete!", progress_callback)

            # Save Phase 2 output
            self._save_phase_output(run_id, "phase2", state)

            # Phase 3: Video Generation
            await self._update_progress(run_id, "video", 0, "Initializing video generation...", progress_callback)

            if not self.video_generator:
                self.video_generator = VideoGenerator()

            # Run in executor
            state = await loop.run_in_executor(
                None,
                self.video_generator.generate,
                state,
                None  # progress_callback for now
            )

            await self._update_progress(run_id, "video", 100, "Video generation complete!", progress_callback)

            # Save Phase 3 output
            self._save_phase_output(run_id, "phase3", state)

            # Save state snapshot
            state_manager = StateManager(run_id)
            state_manager.snapshot(state, "Pipeline completed - All phases", [])

            # Mark as complete
            self.active_runs[run_id]["status"] = "completed"
            self.active_runs[run_id]["phase"] = "completed"
            self.active_runs[run_id]["progress"] = 100
            self.active_runs[run_id]["completed_at"] = datetime.utcnow().isoformat()

            await self._update_progress(
                run_id,
                "completed",
                100,
                "Pipeline completed successfully!",
                progress_callback
            )

        except Exception as e:
            # Handle errors
            self.active_runs[run_id]["status"] = "failed"
            self.active_runs[run_id]["error"] = str(e)

            await self._update_progress(
                run_id,
                "error",
                0,
                f"Pipeline failed: {str(e)}",
                progress_callback
            )

            print(f"Pipeline error for {run_id}: {e}")
            import traceback
            traceback.print_exc()

    async def _update_progress(
        self,
        run_id: str,
        phase: str,
        progress: int,
        message: str,
        callback: Optional[Callable] = None
    ):
        """Update progress and notify via callback"""

        # Update internal state
        if run_id in self.active_runs:
            self.active_runs[run_id]["phase"] = phase
            self.active_runs[run_id]["progress"] = progress
            self.active_runs[run_id]["message"] = message

        # Call progress callback if provided
        if callback:
            try:
                callback({
                    "type": "progress",
                    "run_id": run_id,
                    "phase": phase,
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                print(f"Progress callback error: {e}")

    def _save_phase_output(self, run_id: str, phase_name: str, state: PipelineState):
        """Save phase output to JSON file"""
        output_file = config.OUTPUTS_DIR / run_id / f"{phase_name}_output.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(state.dict(), f, indent=2, default=str)

    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a run"""

        # Check active runs first
        if run_id in self.active_runs:
            active_run = self.active_runs[run_id]

            # Convert active run format to frontend format
            current_phase = active_run.get("phase", "initializing")
            progress = active_run.get("progress", 0)

            # Build phase states based on current progress
            phases = {
                "script": {"status": "pending", "progress": 0, "duration": "—", "substeps": []},
                "audio": {"status": "pending", "progress": 0, "duration": "—", "substeps": []},
                "video": {"status": "pending", "progress": 0, "duration": "—", "substeps": []},
                "web": {"status": "pending", "progress": 0, "duration": "—", "substeps": []},
                "edit": {"status": "pending", "progress": 0, "duration": "—", "substeps": []},
            }

            # Update phase states based on current phase
            if current_phase == "script" or current_phase == "initializing":
                phases["script"]["status"] = "running"
                phases["script"]["progress"] = progress
            elif current_phase == "audio":
                phases["script"]["status"] = "complete"
                phases["script"]["progress"] = 100
                phases["audio"]["status"] = "running"
                phases["audio"]["progress"] = progress
            elif current_phase == "video":
                phases["script"]["status"] = "complete"
                phases["script"]["progress"] = 100
                phases["audio"]["status"] = "complete"
                phases["audio"]["progress"] = 100
                phases["video"]["status"] = "running"
                phases["video"]["progress"] = progress
            elif current_phase == "completed":
                phases["script"]["status"] = "complete"
                phases["script"]["progress"] = 100
                phases["audio"]["status"] = "complete"
                phases["audio"]["progress"] = 100
                phases["video"]["status"] = "complete"
                phases["video"]["progress"] = 100

            return {
                "run_id": run_id,
                "status": active_run.get("status", "running"),
                "phases": phases,
                "metadata": {
                    "prompt": active_run.get("user_prompt", ""),
                    "started_at": active_run.get("started_at", ""),
                }
            }

        # Check if run exists in outputs (completed runs)
        run_dir = config.OUTPUTS_DIR / run_id
        if run_dir.exists():
            # Try to load from saved output (phase3 > phase2 > phase1)
            output_file = run_dir / "phase3_output.json"
            if not output_file.exists():
                output_file = run_dir / "phase2_output.json"
            if not output_file.exists():
                output_file = run_dir / "phase1_output.json"

            if output_file.exists():
                with open(output_file, "r") as f:
                    data = json.load(f)

                    # Determine which phases are complete based on file existence
                    has_phase1 = (run_dir / "phase1_output.json").exists()
                    has_phase2 = (run_dir / "phase2_output.json").exists()
                    has_phase3 = (run_dir / "phase3_output.json").exists()

                    phases = {
                        "script": {
                            "status": "complete" if has_phase1 else "pending",
                            "progress": 100 if has_phase1 else 0,
                            "duration": "—",
                            "substeps": ['Scene graph', 'Dialogue', 'Shotlist']
                        },
                        "audio": {
                            "status": "complete" if has_phase2 else "pending",
                            "progress": 100 if has_phase2 else 0,
                            "duration": "—",
                            "substeps": ['Voice casting', 'Narration', 'SFX', 'Score']
                        },
                        "video": {
                            "status": "complete" if has_phase3 else "pending",
                            "progress": 100 if has_phase3 else 0,
                            "duration": "—",
                            "substeps": ['Storyboard', 'Keyframes', 'Interpolation', 'Compositing']
                        },
                        "web": {
                            "status": "pending",
                            "progress": 0,
                            "duration": "—",
                            "substeps": ['Player config', 'Captions', 'Share links']
                        },
                        "edit": {
                            "status": "pending",
                            "progress": 0,
                            "duration": "—",
                            "substeps": ['Intent parser', 'Patch planner']
                        },
                    }

                    return {
                        "run_id": run_id,
                        "status": "completed",
                        "phases": phases,
                        "metadata": {
                            "prompt": data.get("user_prompt", ""),
                            "started_at": data.get("timestamp", ""),
                        }
                    }

        return None

    async def rerun_phase(
        self,
        run_id: str,
        phase: str,
        progress_callback: Optional[Callable] = None
    ):
        """Re-run a specific phase"""

        # Load existing state manager with history
        state_manager = StateManager.load_or_create(run_id)
        state = state_manager.get_latest_state()

        if not state:
            raise ValueError(f"No state found for run {run_id}")

        # Re-run the specified phase
        if phase == "script":
            if not self.story_agent:
                self.story_agent = StoryAgent()

            await self._update_progress(run_id, "script", 0, "Re-generating story...", progress_callback)

            loop = asyncio.get_event_loop()
            state = await loop.run_in_executor(
                None,
                self.story_agent.generate,
                state.user_prompt,
                state.user_params,
                run_id  # Pass the run_id to story agent
            )

            self._save_phase_output(run_id, "phase1", state)

        elif phase == "audio":
            if not self.audio_generator:
                self.audio_generator = AudioGenerator()

            await self._update_progress(run_id, "audio", 0, "Re-generating audio...", progress_callback)

            loop = asyncio.get_event_loop()
            state = await loop.run_in_executor(
                None,
                self.audio_generator.generate,
                state
            )

            self._save_phase_output(run_id, "phase2", state)

        elif phase == "video":
            if not self.video_generator:
                self.video_generator = VideoGenerator()

            await self._update_progress(run_id, "video", 0, "Re-generating video...", progress_callback)

            loop = asyncio.get_event_loop()
            state = await loop.run_in_executor(
                None,
                self.video_generator.generate,
                state,
                None
            )

            self._save_phase_output(run_id, "phase3", state)

        # Save new snapshot
        state_manager.snapshot(state, f"Re-ran phase: {phase}", [])

        await self._update_progress(run_id, phase, 100, f"Phase {phase} re-run complete!", progress_callback)

        return state

    async def execute_edit(
        self,
        run_id: str,
        edit_command: str,
        progress_callback: Optional[Callable] = None
    ):
        """Execute edit command using edit agent"""

        # Load existing state manager with history
        state_manager = StateManager.load_or_create(run_id)
        state = state_manager.get_latest_state()

        if not state:
            raise ValueError(f"No state found for run {run_id}")

        # Initialize edit agent if needed
        if not self.edit_agent:
            self.edit_agent = EditAgent()

        await self._update_progress(run_id, "edit", 0, f"Executing edit: {edit_command[:50]}...", progress_callback)

        # Execute edit in background
        loop = asyncio.get_event_loop()
        updated_state, intents = await loop.run_in_executor(
            None,
            self.edit_agent.edit,
            edit_command,
            state,
            state_manager
        )

        # Check if any phase needs re-running
        if updated_state.phase_status.get("script") == "needs_regeneration":
            await self.rerun_phase(run_id, "script", progress_callback)
            # If script regenerated, need to regenerate audio and video too
            await self.rerun_phase(run_id, "audio", progress_callback)
            await self.rerun_phase(run_id, "video", progress_callback)
        elif updated_state.phase_status.get("audio") == "needs_regeneration":
            await self.rerun_phase(run_id, "audio", progress_callback)
            # If audio regenerated, need to recompose video
            await self.rerun_phase(run_id, "video", progress_callback)
        elif updated_state.phase_status.get("video") == "needs_regeneration":
            await self.rerun_phase(run_id, "video", progress_callback)
        elif updated_state.phase_status.get("video") == "needs_recomposition":
            # Only recompose without regenerating frames
            await self.rerun_phase(run_id, "video", progress_callback)

        await self._update_progress(run_id, "edit", 100, f"Edit complete! Executed {len(intents)} intent(s)", progress_callback)

        return updated_state

    async def undo_edit(self, run_id: str, steps: int = 1):
        """Undo last N edits"""
        state_manager = StateManager.load_or_create(run_id)

        if not self.edit_agent:
            self.edit_agent = EditAgent()

        return self.edit_agent.undo(state_manager, steps)
