"""
LLM Text Generator Tool
Wraps LangChain + Groq for text generation
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from typing import Any, Dict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import config
from mcp import BaseTool, ToolMetadata, register_tool


@register_tool
class TextGeneratorTool(BaseTool):
    """
    General-purpose text generation using LLM
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
            name="text_generator",
            description="Generate text using LLM (Groq + LLaMA)",
            category="llm",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt for text generation"},
                    "temperature": {"type": "number", "description": "Temperature for generation", "default": 0.7},
                },
                "required": ["prompt"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Generated text"}
                }
            }
        )

    def execute(self, prompt: str, temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """
        Execute text generation

        Args:
            prompt: The prompt to generate from
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        # Update temperature if different
        if abs(self.llm.temperature - temperature) > 0.01:
            self.llm.temperature = temperature

        response = self.llm.invoke([HumanMessage(content=prompt)])

        return {
            "text": response.content,
            "model": config.GROQ_MODEL
        }
