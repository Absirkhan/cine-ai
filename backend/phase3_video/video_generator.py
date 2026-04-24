"""
Phase 3: Video Generation & Composition
Main orchestrator for video generation pipeline
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from typing import Optional

from .image_generator import ImageGenerator
from .animator import VideoAnimator
from .compositor import VideoCompositor
from shared.schema import PipelineState
import config


class VideoGenerator:
    """Orchestrates complete video generation pipeline"""

    def __init__(self):
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
        print("🎨 PHASE 3: Video Generation & Composition")
        print("=" * 80)

        if not state.scenes:
            raise ValueError("No scenes to generate video from")

        # Get aspect ratio dimensions
        aspect_ratio = state.user_params.get("aspect", "16:9")
        width, height = self.image_gen.get_image_dimensions(aspect_ratio)

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

            # Generate image
            image_path = self.image_gen.generate_image(
                prompt=scene.visual_prompt,
                run_id=state.run_id,
                scene_id=scene.id,
                width=width,
                height=height
            )

            if image_path:
                scene.image_file = image_path
            else:
                print(f"  ⚠ Failed to generate image for {scene.id}")

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
                print(f"\nScene {i + 1}: Skipping (no image)")
                continue

            print(f"\nScene {i + 1}/{total_scenes}: {scene.id}")
            duration = scene.duration_ms / 1000  # Convert to seconds

            # Apply animation
            video_path = self.animator.create_scene_video(
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
                "message": "Compositing final video with audio..."
            })

        final_video_path = self.compositor.compose_final_video(state)

        state.final_video_path = final_video_path

        # Update phase status
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
