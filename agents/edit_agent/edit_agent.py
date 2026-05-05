"""
Phase 5: Edit Agent
Main interface for natural language video editing with undo/redo
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Any

from .intent_parser import IntentParser
from .intent_decomposer import IntentDecomposer
from .executor import EditExecutor
from shared.schema import PipelineState, EditIntent
from shared.state_manager import StateManager


class EditAgent:
    """Natural language editing agent with undo/redo support"""

    def __init__(self):
        self.parser = IntentParser()
        self.decomposer = IntentDecomposer()
        self.executor = EditExecutor()

    def edit(
        self,
        edit_command: str,
        state: PipelineState,
        state_manager: StateManager
    ) -> tuple[PipelineState, List[EditIntent]]:
        """
        Execute natural language edit command (supports multi-part commands)

        Args:
            edit_command: User's edit command in natural language (can be complex)
            state: Current pipeline state
            state_manager: State manager for versioning

        Returns:
            Tuple of (updated state, list of parsed intents)
        """
        print("\n" + "=" * 80)
        print("✏️  EDIT AGENT")
        print("=" * 80)
        print(f"\nCommand: \"{edit_command}\"")

        # Step 1: Decompose complex command into atomic sub-commands
        print("\n✂️  Decomposing command...")
        sub_commands = self.decomposer.decompose(edit_command)

        if len(sub_commands) > 1:
            print(f"   Decomposed into {len(sub_commands)} sub-command(s):")
            for i, cmd in enumerate(sub_commands, 1):
                print(f"   {i}. {cmd}")
        else:
            print("   Single command (no decomposition needed)")

        # Step 2: Parse each sub-command into intent
        print("\n📋 Parsing intent(s)...")
        intents = self.parser.parse_multiple(sub_commands)

        print(f"\n{len(intents)} Intent(s) Parsed:")
        for i, intent in enumerate(intents, 1):
            print(f"  {i}. Type: {intent.intent_type}")
            print(f"     Target: {intent.target}")
            print(f"     Scope: {intent.scope or 'all'}")
            print(f"     Parameters: {intent.parameters}")

        # Step 3: Execute all intents sequentially
        print(f"\n🔧 Executing {len(intents)} edit(s)...")
        for i, intent in enumerate(intents, 1):
            print(f"\n[{i}/{len(intents)}] Executing: {intent.intent_type}")
            state = self.executor.execute(intent, state, state_manager)

        print("\n✓ All edits complete!")
        print("  Use undo() to revert these changes")
        print("=" * 80)

        return state, intents

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
            # Voice & Audio
            "change_voice",
            "regenerate_script",
            # Visual
            "apply_filter",
            "change_scene_characters",
            "change_character_design",
            "regenerate_scene",
            # Music & BGM
            "change_mood",
            "change_bgm",
            "add_bgm",
            "remove_bgm",
            # Timing & Composition
            "adjust_duration",
            "speed_up",
            "slow_down",
            "toggle_subtitles",
            # Global
            "change_script",
            "full_regenerate"
        ]
        return edit_type in supported
