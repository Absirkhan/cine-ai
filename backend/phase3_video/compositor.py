"""
Video Compositor
Combines scene videos with audio and BGM into final MP4
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, CompositeVideoClip, TextClip
)
from typing import List, Optional

from shared.schema import Scene, PipelineState
from shared.utils import generate_asset_filename
import config


class VideoCompositor:
    """Composes final video from scenes, dialogue, and BGM"""

    def __init__(self):
        pass

    def compose_final_video(
        self,
        state: PipelineState,
        output_path: Optional[str] = None
    ) -> str:
        """
        Compose final video from all scenes

        Args:
            state: Pipeline state with all scene data
            output_path: Optional custom output path

        Returns:
            Path to final video file
        """
        if not output_path:
            output_path = str(generate_asset_filename(
                state.run_id,
                "final",
                "output",
                "mp4"
            ))

        video_clips = []
        current_time = 0

        print("\n🎬 Compositing final video...")

        for i, scene in enumerate(state.scenes):
            print(f"\n  Scene {i + 1}/{len(state.scenes)}: {scene.id}")

            if not scene.video_file:
                print(f"    ⚠ No video file for scene, skipping")
                continue

            # Load scene video
            video_clip = VideoFileClip(scene.video_file)

            # Prepare audio tracks
            audio_tracks = []

            # Add dialogue audio
            dialogue_offset = 0
            for dialogue in scene.dialogue:
                if dialogue.audio_file:
                    try:
                        audio_clip = AudioFileClip(dialogue.audio_file)
                        audio_clip = audio_clip.set_start(dialogue_offset)
                        audio_tracks.append(audio_clip)
                        dialogue_offset += audio_clip.duration
                    except Exception as e:
                        print(f"    ⚠ Error loading dialogue audio: {e}")

            # Add BGM (background music)
            if scene.bgm_file:
                try:
                    bgm_clip = AudioFileClip(scene.bgm_file)
                    # Reduce BGM volume to 30% so dialogue is clear
                    bgm_clip = bgm_clip.volumex(0.3)
                    # Loop BGM if shorter than scene
                    if bgm_clip.duration < video_clip.duration:
                        bgm_clip = bgm_clip.audio_loop(duration=video_clip.duration)
                    else:
                        bgm_clip = bgm_clip.subclip(0, video_clip.duration)
                    audio_tracks.append(bgm_clip)
                except Exception as e:
                    print(f"    ⚠ Error loading BGM: {e}")

            # Composite audio
            if audio_tracks:
                composite_audio = CompositeAudioClip(audio_tracks)
                video_clip = video_clip.set_audio(composite_audio)

            video_clips.append(video_clip)

        if not video_clips:
            raise ValueError("No video clips to compose")

        # Concatenate all scenes
        print("\n  Concatenating scenes...")
        final_video = concatenate_videoclips(video_clips, method="compose")

        # Export final video
        print(f"\n  Exporting final video to: {Path(output_path).name}")
        print(f"  Duration: {final_video.duration:.1f}s")

        final_video.write_videofile(
            output_path,
            fps=config.DEFAULT_FPS,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )

        # Close clips
        for clip in video_clips:
            clip.close()
        final_video.close()

        print(f"\n  ✓ Final video saved: {output_path}")

        return output_path

    def add_subtitles(
        self,
        video_path: str,
        state: PipelineState,
        output_path: Optional[str] = None
    ) -> str:
        """
        Add subtitles to video (optional feature)

        Args:
            video_path: Path to input video
            state: Pipeline state with dialogue
            output_path: Optional custom output path

        Returns:
            Path to video with subtitles
        """
        if not output_path:
            output_path = video_path.replace(".mp4", "_subtitled.mp4")

        video = VideoFileClip(video_path)
        subtitle_clips = []

        current_time = 0
        for scene in state.scenes:
            for dialogue in scene.dialogue:
                if dialogue.duration_ms:
                    # Create subtitle text clip
                    txt_clip = TextClip(
                        dialogue.text,
                        fontsize=24,
                        color='white',
                        bg_color='black',
                        size=(video.w * 0.8, None),
                        method='caption'
                    )

                    # Position at bottom
                    txt_clip = txt_clip.set_position(('center', 'bottom'))

                    # Set timing
                    duration = dialogue.duration_ms / 1000
                    txt_clip = txt_clip.set_start(current_time).set_duration(duration)

                    subtitle_clips.append(txt_clip)
                    current_time += duration

        # Composite video with subtitles
        if subtitle_clips:
            final = CompositeVideoClip([video] + subtitle_clips)

            final.write_videofile(
                output_path,
                fps=config.DEFAULT_FPS,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )

            final.close()

        video.close()

        return output_path
