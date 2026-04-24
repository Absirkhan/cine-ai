"""
State Manager for Version Control and Undo/Redo
Implements snapshot-based versioning with full asset tracking
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from .schema import PipelineState, VersionSnapshot
import config


class StateManager:
    """Manages pipeline state with full version history and undo/redo support"""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.state_dir = config.OUTPUTS_DIR / run_id / "states"
        self.assets_dir = config.OUTPUTS_DIR / run_id / "assets"

        # Create directories
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        self.current_version = 0
        self.history: List[VersionSnapshot] = []

    def snapshot(
        self,
        state: PipelineState,
        change_description: str,
        asset_paths: Optional[List[str]] = None
    ) -> int:
        """
        Create a new version snapshot

        Args:
            state: Current pipeline state
            change_description: Human-readable description of changes
            asset_paths: List of asset file paths to preserve

        Returns:
            Version number of created snapshot
        """
        self.current_version += 1
        version = self.current_version

        # Update state version
        state.version = version
        state.timestamp = datetime.utcnow().isoformat()

        # Create version directory
        version_dir = self.state_dir / f"v{version:03d}"
        version_dir.mkdir(exist_ok=True)

        # Save state JSON
        state_file = version_dir / "state.json"
        with open(state_file, "w") as f:
            json.dump(state.dict(), f, indent=2)

        # Copy assets to version directory
        version_assets_dir = version_dir / "assets"
        version_assets_dir.mkdir(exist_ok=True)

        preserved_paths = []
        if asset_paths:
            for asset_path in asset_paths:
                src = Path(asset_path)
                if src.exists():
                    dst = version_assets_dir / src.name
                    shutil.copy2(src, dst)
                    preserved_paths.append(str(dst))

        # Create snapshot record
        snapshot = VersionSnapshot(
            version=version,
            timestamp=state.timestamp,
            state=state,
            change_description=change_description,
            asset_paths=preserved_paths
        )

        self.history.append(snapshot)

        # Save snapshot metadata
        snapshot_file = version_dir / "snapshot.json"
        with open(snapshot_file, "w") as f:
            json.dump(snapshot.dict(), f, indent=2)

        return version

    def revert(self, version: int) -> Optional[PipelineState]:
        """
        Revert to a previous version

        Args:
            version: Version number to revert to

        Returns:
            PipelineState at that version, or None if version not found
        """
        version_dir = self.state_dir / f"v{version:03d}"

        if not version_dir.exists():
            return None

        # Load state
        state_file = version_dir / "state.json"
        with open(state_file, "r") as f:
            state_data = json.load(f)

        state = PipelineState(**state_data)

        # Restore assets
        version_assets_dir = version_dir / "assets"
        if version_assets_dir.exists():
            for asset_file in version_assets_dir.glob("*"):
                # Copy back to main assets directory
                dst = self.assets_dir / asset_file.name
                shutil.copy2(asset_file, dst)

        self.current_version = version
        return state

    def get_history(self) -> List[dict]:
        """
        Get version history summary

        Returns:
            List of version metadata dicts
        """
        history_summary = []

        for version_dir in sorted(self.state_dir.glob("v*")):
            snapshot_file = version_dir / "snapshot.json"
            if snapshot_file.exists():
                with open(snapshot_file, "r") as f:
                    snapshot_data = json.load(f)

                history_summary.append({
                    "version": snapshot_data["version"],
                    "timestamp": snapshot_data["timestamp"],
                    "description": snapshot_data["change_description"],
                    "asset_count": len(snapshot_data.get("asset_paths", []))
                })

        return history_summary

    def get_snapshot(self, version: int) -> Optional[VersionSnapshot]:
        """Get a specific snapshot by version number"""
        version_dir = self.state_dir / f"v{version:03d}"
        snapshot_file = version_dir / "snapshot.json"

        if not snapshot_file.exists():
            return None

        with open(snapshot_file, "r") as f:
            snapshot_data = json.load(f)

        return VersionSnapshot(**snapshot_data)

    def get_latest_state(self) -> Optional[PipelineState]:
        """Get the most recent state"""
        if self.current_version == 0:
            return None

        return self.revert(self.current_version)

    def delete_version(self, version: int) -> bool:
        """
        Delete a specific version (use with caution)

        Args:
            version: Version number to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        version_dir = self.state_dir / f"v{version:03d}"

        if not version_dir.exists():
            return False

        shutil.rmtree(version_dir)

        # Remove from history
        self.history = [s for s in self.history if s.version != version]

        return True

    def cleanup_old_versions(self, keep_last_n: int = 10):
        """
        Clean up old versions, keeping only the last N

        Args:
            keep_last_n: Number of most recent versions to keep
        """
        version_dirs = sorted(self.state_dir.glob("v*"))

        if len(version_dirs) <= keep_last_n:
            return

        # Delete old versions
        for version_dir in version_dirs[:-keep_last_n]:
            shutil.rmtree(version_dir)

    @staticmethod
    def load_or_create(run_id: str, initial_state: Optional[PipelineState] = None) -> "StateManager":
        """
        Load existing state manager or create new one

        Args:
            run_id: Run identifier
            initial_state: Initial state if creating new

        Returns:
            StateManager instance
        """
        manager = StateManager(run_id)

        # Check if run already exists
        if manager.state_dir.exists() and list(manager.state_dir.glob("v*")):
            # Load existing history
            for version_dir in sorted(manager.state_dir.glob("v*")):
                snapshot_file = version_dir / "snapshot.json"
                if snapshot_file.exists():
                    with open(snapshot_file, "r") as f:
                        snapshot_data = json.load(f)
                    manager.history.append(VersionSnapshot(**snapshot_data))

            if manager.history:
                manager.current_version = manager.history[-1].version
        elif initial_state:
            # Create initial snapshot
            manager.snapshot(initial_state, "Initial pipeline state", [])

        return manager
