"""
JSON Structurer Tool
Generates structured JSON output from prompts
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import json
import re
from typing import Any, Dict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import config
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class JSONStructurerTool(BaseTool):
    """
    Generate structured JSON from prompts
    Extracts and validates JSON from LLM responses
    """

    def __init__(self):
        super().__init__()
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0.7,
        )

    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="json_structurer",
            description="Generate structured JSON output from prompts",
            category="llm",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Prompt requesting JSON output"},
                    "schema": {"type": "object", "description": "Optional JSON schema for validation"},
                },
                "required": ["prompt"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "object", "description": "Parsed JSON data"}
                }
            }
        )

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response (handles markdown code blocks)"""
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError(f"No JSON found in response: {text[:200]}")

        return json.loads(json_str)

    def execute(self, prompt: str, schema: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate structured JSON

        Args:
            prompt: Prompt for JSON generation
            schema: Optional JSON schema for validation

        Returns:
            Parsed JSON data
        """
        response = self.llm.invoke([HumanMessage(content=prompt)])
        data = self._extract_json(response.content)

        # TODO: Add schema validation if provided

        return {
            "data": data,
            "raw_response": response.content
        }
