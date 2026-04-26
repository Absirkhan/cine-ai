"""
Phase 5: Edit Agent
Main interface for natural language video editing with undo/redo
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Any

from .intent_parser import IntentParser
from .executor import EditExecutor
from shared.schema import PipelineState, EditIntent
from shared.state_manager import StateManager


class EditAgent:
    """Natural language editing agent with undo/redo support"""

    def __init__(self):
        self.parser = IntentParser()
        self.executor = EditExecutor()

    def edit(
        self,
        edit_command: str,
        state: PipelineState,
        state_manager: StateManager
    ) -> tuple[PipelineState, EditIntent]:
        """
        Execute natural language edit command

        Args:
            edit_command: User's edit command in natural language
            state: Current pipeline state
            state_manager: State manager for versioning

        Returns:
            Tuple of (updated state, parsed intent)
        """
        print("\n" + "=" * 80)
        print("✏️  EDIT AGENT")
        print("=" * 80)
        print(f"\nCommand: \"{edit_command}\"")

        # Parse intent
        print("\n📋 Parsing intent...")
        intent = self.parser.parse(edit_command)

        print(f"\nParsed Intent:")
        print(f"  Type: {intent.intent_type}")
        print(f"  Target: {intent.target}")
        print(f"  Scope: {intent.scope or 'all'}")
        print(f"  Parameters: {intent.parameters}")

        # Execute edit
        updated_state = self.executor.execute(intent, state, state_manager)

        print("\n✓ Edit complete!")
        print("  Use undo() to revert this change")
        print("=" * 80)

        return updated_state, intent

    def undo(
        self,
        state_manager: StateManager,
        steps: int = 1
    ) -> PipelineState:
        """
        Undo last N edits

        Args:
            state_manager: State manager
            steps: Number of steps to undo

        Returns:
            Previous pipeline state
        """
        print(f"\n↶ Undoing {steps} edit(s)...")

        history = state_manager.get_history()
        if len(history) < 2:
            print("  ✗ No edits to undo")
            return state_manager.get_latest_state()

        # Get version before last N edits
        target_version = max(1, len(history) - steps)
        previous_state = state_manager.revert(target_version)

        if previous_state:
            print(f"  ✓ Reverted to version {target_version}")
            return previous_state
        else:
            print("  ✗ Failed to revert")
            return state_manager.get_latest_state()

    def redo(
        self,
        state_manager: StateManager,
        steps: int = 1
    ) -> PipelineState:
        """
        Redo last N undone edits

        Args:
            state_manager: State manager
            steps: Number of steps to redo

        Returns:
            Next pipeline state
        """
        print(f"\n↷ Redoing {steps} edit(s)...")

        history = state_manager.get_history()
        current_version = state_manager.current_version

        if current_version >= len(history):
            print("  ✗ No edits to redo")
            return state_manager.get_latest_state()

        # Get version after N steps
        target_version = min(len(history), current_version + steps)
        next_state = state_manager.revert(target_version)

        if next_state:
            print(f"  ✓ Advanced to version {target_version}")
            return next_state
        else:
            print("  ✗ Failed to advance")
            return state_manager.get_latest_state()

    def get_edit_history(
        self,
        state_manager: StateManager
    ) -> List[Dict[str, Any]]:
        """
        Get edit history with descriptions

        Args:
            state_manager: State manager

        Returns:
            List of version metadata
        """
        return state_manager.get_history()

    def supports_edit_type(self, edit_type: str) -> bool:
        """Check if an edit type is supported"""
        supported = [
            "change_voice",
            "change_mood",
            "change_bgm",
            "regenerate_scene",
            "adjust_duration",
            "apply_filter",
            "change_script",
            "full_regenerate"
        ]
        return edit_type in supported
