"""
MCP Tools Registry Initialization
Imports and registers all tools automatically
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def initialize_all_tools():
    """
    Import all tool modules to trigger @register_tool decorators
    This registers all tools in the global registry
    """
    print("\n" + "=" * 60)
    print("Initializing MCP Tools Registry")
    print("=" * 60 + "\n")

    # Import LLM tools
    from mcp.tools.llm_tools.text_generator import TextGeneratorTool
    from mcp.tools.llm_tools.json_structurer import JSONStructurerTool

    # Import audio tools
    from mcp.tools.audio_tools.tts_tool import TTSTool
    from mcp.tools.audio_tools.bgm_tool import BGMTool
    from mcp.tools.audio_tools.audio_merger import AudioMergerTool

    # Import vision tools
    from mcp.tools.vision_tools.image_gen_tool import ImageGeneratorTool
    from mcp.tools.vision_tools.image_edit_tool import ImageEditTool
    from mcp.tools.vision_tools.style_transfer import StyleTransferTool

    # Import video tools
    from mcp.tools.video_tools.compositor_tool import VideoCompositorTool
    from mcp.tools.video_tools.ffmpeg_tool import FFmpegTool
    from mcp.tools.video_tools.subtitle_tool import SubtitleTool

    # Import system tools
    from mcp.tools.system_tools.state_tool import StateManagementTool
    from mcp.tools.system_tools.file_tool import FileTool
    from mcp.tools.system_tools.logger_tool import LoggerTool

    # Get registry and show registered tools
    from mcp import get_registry
    registry = get_registry()

    print(f"\n{registry}")
    print(f"\nRegistered Tools by Category:")

    for category in registry.list_categories():
        tools = registry.get_tools_by_category(category)
        print(f"\n  {category.upper()}:")
        for tool in tools:
            print(f"    - {tool.metadata.name}: {tool.metadata.description}")

    print("\n" + "=" * 60)
    print("MCP Tools Ready!")
    print("=" * 60 + "\n")

    return registry


if __name__ == "__main__":
    initialize_all_tools()
