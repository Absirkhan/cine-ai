"""
Orchestrator State
Manages the runtime state of the orchestrator
"""

from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class RunState:
    """State for a single pipeline run"""
    run_id: str
    status: str  # "running", "completed", "failed"
    phase: str  # current phase name
    progress: int  # 0-100
    started_at: str
    user_prompt: str
    params: Dict[str, Any]
    completed_at: Optional[str] = None
    error: Optional[str] = None
    message: str = ""


class OrchestratorState:
    """
    Manages state for all active pipeline runs

    This allows the orchestrator to:
    - Track multiple concurrent runs
    - Resume runs after restart
    - Provide status updates
    """

    def __init__(self):
        self.active_runs: Dict[str, RunState] = {}

    def create_run(
        self,
        run_id: str,
        user_prompt: str,
        params: Dict[str, Any]
    ) -> RunState:
        """Create a new run"""
        run_state = RunState(
            run_id=run_id,
            status="running",
            phase="initializing",
            progress=0,
            started_at=datetime.utcnow().isoformat(),
            user_prompt=user_prompt,
            params=params
        )
        self.active_runs[run_id] = run_state
        return run_state

    def get_run(self, run_id: str) -> Optional[RunState]:
        """Get run state"""
        return self.active_runs.get(run_id)

    def update_run(
        self,
        run_id: str,
        phase: Optional[str] = None,
        progress: Optional[int] = None,
        status: Optional[str] = None,
        message: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update run state"""
        if run_id not in self.active_runs:
            return

        run = self.active_runs[run_id]

        if phase is not None:
            run.phase = phase
        if progress is not None:
            run.progress = progress
        if status is not None:
            run.status = status
            if status == "completed":
                run.completed_at = datetime.utcnow().isoformat()
        if message is not None:
            run.message = message
        if error is not None:
            run.error = error
            run.status = "failed"

    def complete_run(self, run_id: str):
        """Mark a run as completed"""
        self.update_run(run_id, status="completed", progress=100)

    def fail_run(self, run_id: str, error: str):
        """Mark a run as failed"""
        self.update_run(run_id, status="failed", error=error)

    def list_runs(self) -> Dict[str, RunState]:
        """List all active runs"""
        return self.active_runs
