"""
Intent Decomposer for Complex Multi-Part Commands
Breaks down complex edit commands into atomic, independent intents
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
import re
from typing import List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

import config


class IntentDecomposer:
    """Decomposes complex multi-part edit commands into simple atomic commands"""

    def __init__(self):
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0.2,  # Low temperature for consistent decomposition
        )

    def decompose(self, complex_command: str) -> List[str]:
        """
        Break complex edit command into atomic sub-commands

        Args:
            complex_command: User's potentially complex edit command

        Returns:
            List of simple, independent edit commands
        """
        # Check if command is already simple (single action, single target)
        if self._is_simple_command(complex_command):
            return [complex_command]

        prompt = f"""You are a video editing command decomposer. Break the following complex edit command into SEPARATE, INDEPENDENT edit commands.

USER COMMAND: "{complex_command}"

RULES:
1. Each output command should target ONE scene OR ONE character OR ONE element
2. Each command should perform ONE action
3. Preserve the original intent and details from the user command
4. If a command mentions multiple scenes, create separate commands for each scene
5. If a command has multiple actions, create separate commands for each action
6. Maintain scene numbers, character names, and parameter values exactly as specified
7. If the command says "keep scene X same", SKIP that scene (don't output a command for it)

OUTPUT FORMAT:
Return a JSON array of strings, where each string is a simple edit command.

EXAMPLES:

Input: "Make scene 1 darker and scene 3 brighter"
Output: ["Make scene 1 darker", "Make scene 3 brighter"]

Input: "Change narrator's voice to whispered and add background music"
Output: ["Change narrator's voice to whispered", "Add background music"]

Input: "In scene 1 change characters to male and female, keep scene 2 same, in scene 3 also male and female, only one female in scene 4"
Output: [
  "In scene 1 change characters to male and female",
  "In scene 3 change characters to male and female",
  "In scene 4 change characters to only one female"
]

Input: "Remove subtitles from scene 2 and speed up scene 3"
Output: ["Remove subtitles from scene 2", "Speed up scene 3"]

Input: "Change voice tone to calm"
Output: ["Change voice tone to calm"]

Input: "Regenerate the entire script"
Output: ["Regenerate the entire script"]

Now decompose the user command above. Respond with ONLY a JSON array of strings."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result_text = response.content.strip()

            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                commands = json.loads(json_match.group(0))
                # Filter out empty strings
                commands = [cmd.strip() for cmd in commands if cmd.strip()]
                return commands if commands else [complex_command]
            else:
                # Fallback: treat as single command
                return [complex_command]

        except Exception as e:
            print(f"⚠️  Decomposition failed: {e}")
            print(f"   Treating as single command")
            return [complex_command]

    def _is_simple_command(self, command: str) -> bool:
        """
        Heuristic check if command is already simple (single action, single target)

        Args:
            command: Edit command

        Returns:
            True if command appears to be simple/atomic
        """
        command_lower = command.lower()

        # Check for conjunction words that suggest multiple actions
        multi_action_indicators = [
            ' and ', ' also ', ' then ', ', ', ' but ', ' however ',
            'first', 'second', 'third', 'last', 'finally'
        ]

        for indicator in multi_action_indicators:
            if indicator in command_lower:
                return False

        # Check for multiple scene references (e.g., "scene 1", "scene 2")
        scene_matches = re.findall(r'scene\s+\d+', command_lower)
        if len(scene_matches) > 1:
            return False

        # If no complexity indicators found, treat as simple
        return True


if __name__ == "__main__":
    # Test the decomposer
    decomposer = IntentDecomposer()

    test_commands = [
        "Change voice tone to whispered",
        "Make scene 1 darker and scene 3 brighter",
        "In scene 1 change characters to male and female, keep scene 2 same, in scene 3 also male and female",
        "Remove subtitles and add background music to scene 2",
        "Speed up scene 1, then make scene 2 darker, finally regenerate scene 3"
    ]

    print("=" * 80)
    print("INTENT DECOMPOSER TEST")
    print("=" * 80)

    for cmd in test_commands:
        print(f"\n📝 Input: {cmd}")
        decomposed = decomposer.decompose(cmd)
        print(f"✂️  Decomposed into {len(decomposed)} command(s):")
        for i, sub_cmd in enumerate(decomposed, 1):
            print(f"   {i}. {sub_cmd}")
