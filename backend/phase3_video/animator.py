"""
Video Animation using MoviePy
Applies Ken Burns effects (zoom/pan) to still images
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from moviepy.editor import ImageClip
import random

from shared.utils import generate_asset_filename


class VideoAnimator:
    """Applies animation effects to still images"""

    def __init__(self, fps: int = 24):
        self.fps = fps

    def apply_ken_burns(
        self,
        image_path: str,
        duration: float,
        effect: str = "random"
    ) -> ImageClip:
        """
        Apply Ken Burns effect (zoom/pan) to image

        Args:
            image_path: Path to input image
            duration: Duration in seconds
            effect: Type of effect (zoom_in, zoom_out, pan_left, pan_right, random)

        Returns:
            MoviePy ImageClip with animation
        """
        clip = ImageClip(image_path, duration=duration)

        if effect == "random":
            effect = random.choice(["zoom_in", "zoom_out", "pan_right", "pan_left"])

        if effect == "zoom_in":
            # Zoom in slowly
            clip = clip.resize(lambda t: 1 + 0.3 * (t / duration))

        elif effect == "zoom_out":
            # Zoom out slowly
            clip = clip.resize(lambda t: 1.3 - 0.3 * (t / duration))

        elif effect == "pan_right":
            # Pan from left to right
            w, h = clip.size
            clip = clip.crop(
                x1=lambda t: int(w * 0.2 * (t / duration)),
                width=w,
                height=h
            )

        elif effect == "pan_left":
            # Pan from right to left
            w, h = clip.size
            clip = clip.crop(
                x1=lambda t: int(w * 0.2 * (1 - t / duration)),
                width=w,
                height=h
            )

        return clip.set_fps(self.fps)

    def create_scene_video(
        self,
        image_path: str,
        duration: float,
        run_id: str,
        scene_id: str,
        effect: str = "random"
    ) -> str:
        """
        Create animated video clip for a scene

        Args:
            image_path: Path to scene image
            duration: Duration in seconds
            run_id: Pipeline run ID
            scene_id: Scene identifier
            effect: Animation effect to apply

        Returns:
            Path to generated video file
        """
        # Apply animation
        clip = self.apply_ken_burns(image_path, duration, effect)

        # Generate output path
        video_file = generate_asset_filename(
            run_id,
            "scene_video",
            scene_id,
            "mp4"
        )

        # Export video
        clip.write_videofile(
            str(video_file),
            fps=self.fps,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None
        )

        clip.close()

        return str(video_file)
