"""
Phase 3: Video Generation & Composition (MCP-Integrated Version)
Uses MCP tools for all operations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime
from typing import Optional

from .visual_context import VisualContextManager
from state_manager.schema import PipelineState
from mcp import ToolExecutor
import config


class VideoGeneratorMCP:
    """
    Orchestrates complete video generation pipeline using MCP tools
    """

    def __init__(self, use_mcp: bool = True):
        """
        Initialize video generator

        Args:
            use_mcp: If True, use MCP tools. If False, fall back to direct implementations
        """
        self.use_mcp = use_mcp
        self.executor = ToolExecutor() if use_mcp else None

        # Fallback to direct implementations if not using MCP
        if not use_mcp:
            from .image_generator import ImageGenerator
            from .animator import VideoAnimator
            from .compositor import VideoCompositor

            self.image_gen = ImageGenerator()
            self.animator = VideoAnimator(fps=config.DEFAULT_FPS)
            self.compositor = VideoCompositor()

    def generate(
        self,
        state: PipelineState,
        progress_callback: Optional[callable] = None
    ) -> PipelineState:
        """
        Generate complete video from story and audio

        Args:
            state: PipelineState with story, scenes, and audio
            progress_callback: Optional callback for progress updates

        Returns:
            Updated PipelineState with video file path
        """
        print("\n" + "=" * 80)
        print(f"🎨 PHASE 3: Video Generation & Composition ({'MCP Mode' if self.use_mcp else 'Direct Mode'})")
        print("=" * 80)

        if not state.scenes:
            raise ValueError("No scenes to generate video from")

        # Initialize visual context manager
        context_manager = VisualContextManager()

        if state.visual_context:
            print("  📋 Restoring visual context from state...")
        else:
            print("  🎬 Initializing visual context for continuity...")
            context_manager.initialize_from_characters(
                characters=state.characters,
                genre=state.user_params.get("genre", "Sci-Fi"),
                tone=state.user_params.get("tone", "Cinematic"),
                aspect=state.user_params.get("aspect", "16:9")
            )

        # Get aspect ratio dimensions
        aspect_ratio = state.user_params.get("aspect", "16:9")
        width, height = self._get_image_dimensions(aspect_ratio)

        total_scenes = len(state.scenes)

        # Step 1: Generate images for each scene
        print(f"\n📸 Generating images for {total_scenes} scenes...")

        for i, scene in enumerate(state.scenes):
            if progress_callback:
                progress = int((i / total_scenes) * 30)
                progress_callback({
                    "phase": "video",
                    "progress": progress,
                    "message": f"Generating image for scene {i + 1}/{total_scenes}..."
                })

            print(f"\nScene {i + 1}/{total_scenes}: {scene.id}")
            print(f"  Prompt: {scene.visual_prompt[:80]}...")

            # Skip if image already exists
            if scene.image_file and Path(scene.image_file).exists():
                print(f"  ✓ Using existing image: {Path(scene.image_file).name}")
                continue

            # Generate image using MCP or direct method
            if self.use_mcp:
                result = self.executor.execute(
                    "image_generator",
                    prompt=scene.visual_prompt,
                    run_id=state.run_id,
                    scene_id=scene.id,
                    width=width,
                    height=height
                )
                image_path = result.get("image_path")
            else:
                image_path = self.image_gen.generate_image(
                    prompt=scene.visual_prompt,
                    run_id=state.run_id,
                    scene_id=scene.id,
                    width=width,
                    height=height
                )

            if image_path:
                scene.image_file = image_path
                print(f"  ✓ Image generated")

                # Add to context
                characters_in_scene = list(set([d.character for d in scene.dialogue]))
                context_manager.add_to_history(
                    scene_id=scene.id,
                    description=scene.description,
                    visual_prompt=scene.visual_prompt,
                    characters_in_scene=characters_in_scene,
                    image_path=image_path
                )

        # Step 2: Animate images
        print(f"\n🎬 Animating {total_scenes} scenes...")

        for i, scene in enumerate(state.scenes):
            if progress_callback:
                progress = 30 + int((i / total_scenes) * 30)
                progress_callback({
                    "phase": "video",
                    "progress": progress,
                    "message": f"Animating scene {i + 1}/{total_scenes}..."
                })

            if not scene.image_file:
                continue

            print(f"\nScene {i + 1}/{total_scenes}: {scene.id}")
            duration = scene.duration_ms / 1000

            # Animate using direct method (MCP animator tool not critical)
            if not self.use_mcp:
                video_path = self.animator.create_scene_video(
                    image_path=scene.image_file,
                    duration=duration,
                    run_id=state.run_id,
                    scene_id=scene.id,
                    effect="random"
                )
            else:
                # For now, fall back to direct for animation
                from .animator import VideoAnimator
                animator = VideoAnimator(fps=config.DEFAULT_FPS)
                video_path = animator.create_scene_video(
                    image_path=scene.image_file,
                    duration=duration,
                    run_id=state.run_id,
                    scene_id=scene.id,
                    effect="random"
                )

            scene.video_file = video_path
            print(f"  ✓ Animated video: {Path(video_path).name}")

        # Step 3: Composite final video
        if progress_callback:
            progress_callback({
                "phase": "video",
                "progress": 70,
                "message": "Compositing final video..."
            })

        if self.use_mcp:
            result = self.executor.execute(
                "video_compositor",
                state=state
            )
            final_video_path = result.get("video_path")
        else:
            final_video_path = self.compositor.compose_final_video(state)

        state.final_video_path = final_video_path
        state.phase_status["video"] = "complete"
        state.timestamp = datetime.utcnow().isoformat()

        if progress_callback:
            progress_callback({
                "phase": "video",
                "progress": 100,
                "message": "Video generation complete!"
            })

        print("\n" + "=" * 80)
        print("✓ Video Generation Complete!")
        print(f"Final video: {final_video_path}")
        print("=" * 80)

        return state

    def _get_image_dimensions(self, aspect_ratio: str) -> tuple[int, int]:
        """Get image dimensions for aspect ratio"""
        dimensions = {
            "16:9": (1024, 576),
            "9:16": (576, 1024),
            "1:1": (1024, 1024),
            "4:3": (1024, 768),
        }
        return dimensions.get(aspect_ratio, (1024, 576))
