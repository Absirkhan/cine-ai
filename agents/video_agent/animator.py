"""
Video Animation using MoviePy
Applies Ken Burns effects (zoom/pan) to still images
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from moviepy.editor import ImageClip
import random
import numpy as np
import cv2

from shared.utils import generate_asset_filename


class VideoAnimator:
    """Applies animation effects to still images"""

    def __init__(self, fps: int = 24):
        self.fps = fps

    @staticmethod
    def ease_in_out_cubic(t):
        """
        Easing function for smooth acceleration and deceleration
        Args:
            t: Progress from 0 to 1
        Returns:
            Eased progress from 0 to 1
        """
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

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
        w, h = clip.size

        if effect == "random":
            effect = random.choice(["zoom_in", "zoom_out", "pan_right", "pan_left"])

        if effect == "zoom_in":
            # Zoom in from 1.0x to 1.3x with smooth easing and proper centering
            def zoom_in_effect(get_frame, t):
                frame = get_frame(t)

                # Calculate progress with easing (0 to 1)
                progress = self.ease_in_out_cubic(t / duration)

                # Scale factor from 1.0 to 1.3
                scale = 1.0 + 0.3 * progress

                # Get frame dimensions
                frame_h, frame_w = frame.shape[:2]

                # Calculate new dimensions after scaling
                new_h = int(frame_h * scale)
                new_w = int(frame_w * scale)

                # Resize frame using OpenCV (much faster than scipy)
                # INTER_LANCZOS4 provides high quality
                zoomed = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

                # Calculate center crop coordinates
                crop_y = (new_h - frame_h) // 2
                crop_x = (new_w - frame_w) // 2

                # Crop to original dimensions from center
                cropped = zoomed[crop_y:crop_y + frame_h, crop_x:crop_x + frame_w]

                return cropped

            clip = clip.fl(zoom_in_effect)

        elif effect == "zoom_out":
            # Zoom out from 1.3x to 1.0x with smooth easing and proper centering
            def zoom_out_effect(get_frame, t):
                frame = get_frame(t)

                # Calculate progress with easing (0 to 1)
                progress = self.ease_in_out_cubic(t / duration)

                # Scale factor from 1.3 to 1.0
                scale = 1.3 - 0.3 * progress

                # Get frame dimensions
                frame_h, frame_w = frame.shape[:2]

                # Calculate new dimensions after scaling
                new_h = int(frame_h * scale)
                new_w = int(frame_w * scale)

                # Resize frame using OpenCV (much faster than scipy)
                # INTER_LANCZOS4 provides high quality
                zoomed = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

                # Calculate center crop coordinates
                crop_y = (new_h - frame_h) // 2
                crop_x = (new_w - frame_w) // 2

                # Crop to original dimensions from center
                cropped = zoomed[crop_y:crop_y + frame_h, crop_x:crop_x + frame_w]

                return cropped

            clip = clip.fl(zoom_out_effect)

        elif effect == "pan_right":
            # Pan from left to right with smooth easing
            # Start with image scaled to 120% to allow panning
            clip = clip.resize(1.2)
            scaled_w = int(w * 1.2)

            # Apply dynamic crop using fl (frame lambda)
            def pan_right_effect(get_frame, t):
                frame = get_frame(t)
                # Calculate progress with easing
                progress = self.ease_in_out_cubic(t / duration)
                # Calculate x position based on eased progress
                x1 = int((scaled_w - w) * progress)
                x2 = x1 + w
                # Crop the frame
                return frame[:, x1:x2]

            clip = clip.fl(pan_right_effect)

        elif effect == "pan_left":
            # Pan from right to left with smooth easing
            # Start with image scaled to 120% to allow panning
            clip = clip.resize(1.2)
            scaled_w = int(w * 1.2)

            # Apply dynamic crop using fl (frame lambda)
            def pan_left_effect(get_frame, t):
                frame = get_frame(t)
                # Calculate progress with easing
                progress = self.ease_in_out_cubic(t / duration)
                # Calculate x position based on eased progress (reverse direction)
                x1 = int((scaled_w - w) * (1 - progress))
                x2 = x1 + w
                # Crop the frame
                return frame[:, x1:x2]

            clip = clip.fl(pan_left_effect)

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
