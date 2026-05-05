"""
Image Generation using Hugging Face InferenceClient
Generates still images for each scene using official HuggingFace SDK
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
import time
from typing import Optional
from PIL import Image
from huggingface_hub import InferenceClient

from shared.schema import Scene
from shared.utils import generate_asset_filename
import config


class ImageGenerator:
    """Generates images using Hugging Face InferenceClient with automatic fallback"""

    def __init__(self):
        """Initialize with primary and fallback models"""
        # Get HuggingFace token from environment
        self.hf_token = os.getenv("HUGGINGFACE_API_KEY") or config.HUGGINGFACE_API_KEY

        # Primary model (Z-Image-Turbo - 8-step fast generation)
        self.primary_model = "Tongyi-MAI/Z-Image-Turbo"

        # Fallback model (FLUX.1-schnell - fast, high quality)
        self.fallback_model = "black-forest-labs/FLUX.1-schnell"

        # Provider for Z-Image-Turbo
        self.provider = "wavespeed"  # GPU-backed provider for Z-Image-Turbo

        # Current active client (will be initialized on first use)
        self.client = None
        self.current_model = None

        # Free tier limits
        self.max_prompt_length = 500  # Conservative limit for free tier
        self.max_words = 77  # Token limit approximation (SDXL uses 77 tokens)

    def _get_client(self, model: str) -> InferenceClient:
        """
        Get or create InferenceClient for specified model

        Args:
            model: Model identifier (e.g., "Tongyi-MAI/Z-Image-Turbo")

        Returns:
            Configured InferenceClient instance
        """
        # Use wavespeed provider for Z-Image-Turbo
        if "Z-Image-Turbo" in model or "Tongyi-MAI" in model:
            return InferenceClient(provider=self.provider, api_key=self.hf_token)
        else:
            return InferenceClient(model=model, token=self.hf_token)

    def _truncate_prompt(self, prompt: str) -> str:
        """
        Intelligently truncate prompt to fit free-tier limits while preserving key information

        Priority order:
        1. Character descriptions (for continuity)
        2. Main scene action/subject
        3. Visual style and atmosphere
        4. Secondary details

        Args:
            prompt: Original prompt text

        Returns:
            Truncated prompt that fits within limits
        """
        # If already within limits, return as-is
        if len(prompt) <= self.max_prompt_length and len(prompt.split()) <= self.max_words:
            return prompt

        print(f"    [!] Prompt too long ({len(prompt)} chars, ~{len(prompt.split())} words). Truncating...")

        # Extract key components using heuristics
        lines = [line.strip() for line in prompt.split('\n') if line.strip()]

        # Categorize lines by priority
        character_lines = []
        continuity_lines = []
        scene_lines = []
        style_lines = []
        detail_lines = []

        for line in lines:
            line_lower = line.lower()
            # Check for continuity instructions first (highest priority with characters)
            if 'continuity' in line_lower or 'maintain exact' in line_lower or 'previous scene' in line_lower:
                continuity_lines.append(line)
            # Character descriptions
            elif any(keyword in line_lower for keyword in ['character:', 'characters (', 'boy', 'girl', 'man', 'woman', 'person wearing', 'person with']):
                character_lines.append(line)
            # Scene action/subject (high priority)
            elif any(keyword in line_lower for keyword in ['scene showing', 'scene depicts', 'depicts', 'showing', 'playing', 'running', 'celebrating', 'action:', 'doing']):
                scene_lines.append(line)
            # Visual style
            elif any(keyword in line_lower for keyword in ['style:', 'cinematic', 'photorealistic', 'animated', 'tone:', 'lighting']):
                style_lines.append(line)
            # Everything else is detail
            else:
                detail_lines.append(line)

        # Build truncated prompt with priority order
        truncated_parts = []
        current_word_count = 0

        # Priority 1: Character descriptions (critical for continuity)
        if character_lines:
            # Combine character lines and truncate if needed
            char_text = ' '.join(character_lines)
            char_words = char_text.split()
            if len(char_words) > 25:  # Max 25 words for character descriptions
                char_text = ' '.join(char_words[:25])
            truncated_parts.append(char_text)
            current_word_count += len(char_text.split())

        # Priority 2: Scene action/subject (what's happening)
        if scene_lines and current_word_count < self.max_words - 15:
            scene_text = ' '.join(scene_lines)
            scene_words = scene_text.split()
            available_words = self.max_words - current_word_count - 10  # Reserve 10 for style
            if len(scene_words) > available_words:
                scene_text = ' '.join(scene_words[:available_words])
            truncated_parts.append(scene_text)
            current_word_count += len(scene_text.split())

        # Priority 3: Style (important but can be shortened)
        if style_lines and current_word_count < self.max_words - 5:
            style_text = ' '.join(style_lines[:1])  # Just first style line
            style_words = style_text.split()
            available_words = self.max_words - current_word_count - 5
            if len(style_words) > available_words:
                style_text = ' '.join(style_words[:available_words])
            truncated_parts.append(style_text)
            current_word_count += len(style_text.split())

        # Priority 4: Continuity notes (if space permits)
        if continuity_lines and current_word_count < self.max_words - 5:
            cont_text = ' '.join(continuity_lines[:1])  # Just first continuity line
            cont_words = cont_text.split()
            available_words = self.max_words - current_word_count
            if len(cont_words) > available_words:
                cont_text = ' '.join(cont_words[:available_words])
            truncated_parts.append(cont_text)
            current_word_count += len(cont_text.split())

        # Priority 5: Details (only if space available)
        if detail_lines and current_word_count < self.max_words - 3:
            detail_text = ' '.join(detail_lines)
            detail_words = detail_text.split()
            available_words = self.max_words - current_word_count
            if len(detail_words) > available_words:
                detail_text = ' '.join(detail_words[:available_words])
            if detail_text:
                truncated_parts.append(detail_text)
                current_word_count += len(detail_text.split())

        # Join and final truncation
        truncated = ' '.join(truncated_parts)

        # Hard truncate if still too long
        if len(truncated) > self.max_prompt_length:
            truncated = truncated[:self.max_prompt_length].rsplit(' ', 1)[0]  # Cut at word boundary

        if len(truncated.split()) > self.max_words:
            words = truncated.split()[:self.max_words]
            truncated = ' '.join(words)

        print(f"    -> Truncated to {len(truncated)} chars, ~{len(truncated.split())} words")

        # Check what was preserved
        preserved = []
        if any(c in truncated for c in ['character', 'boy', 'girl', 'man', 'woman']):
            preserved.append("Characters")
        if any(s in truncated.lower() for s in ['showing', 'playing', 'depicting', 'scene']):
            preserved.append("Scene")
        if any(st in truncated.lower() for st in ['style', 'cinematic', 'lighting']):
            preserved.append("Style")
        if 'continuity' in truncated.lower() or 'maintain' in truncated.lower():
            preserved.append("Continuity")

        print(f"    -> Preserved: {', '.join(preserved) if preserved else 'Basic elements'}")

        return truncated

    def generate_image(
        self,
        prompt: str,
        run_id: str,
        scene_id: str,
        width: int = 1024,
        height: int = 576,
        retries: int = 3
    ) -> Optional[str]:
        """
        Generate image from text prompt using HuggingFace InferenceClient

        Attempts to use primary model (FLUX.1-schnell) first, with automatic
        fallback to stable-diffusion-xl-base-1.0 if primary fails.

        Args:
            prompt: Text description for image generation
            run_id: Pipeline run ID
            scene_id: Scene identifier
            width: Image width (default 1024 for 16:9)
            height: Image height (default 576 for 16:9)
            retries: Number of retry attempts per model

        Returns:
            Path to generated image file, or None on failure
        """

        # Truncate prompt to fit free-tier limits
        truncated_prompt = self._truncate_prompt(prompt)

        # Try primary model first
        result = self._try_generate_with_model(
            model=self.primary_model,
            prompt=truncated_prompt,
            run_id=run_id,
            scene_id=scene_id,
            retries=retries
        )

        if result:
            return result

        # Primary failed, try fallback
        print(f"  ⚠ Primary model failed, trying fallback: {self.fallback_model}")
        result = self._try_generate_with_model(
            model=self.fallback_model,
            prompt=truncated_prompt,
            run_id=run_id,
            scene_id=scene_id,
            retries=retries
        )

        return result

    def _try_generate_with_model(
        self,
        model: str,
        prompt: str,
        run_id: str,
        scene_id: str,
        retries: int = 3
    ) -> Optional[str]:
        """
        Attempt image generation with a specific model

        Args:
            model: HuggingFace model identifier
            prompt: Text description
            run_id: Pipeline run ID
            scene_id: Scene identifier
            retries: Number of retry attempts

        Returns:
            Path to generated image file, or None on failure
        """
        print(f"  🎨 Using model: {model}")

        for attempt in range(retries):
            try:
                print(f"  Generating image for {scene_id} (attempt {attempt + 1}/{retries})...")

                # Create client for this model
                client = self._get_client(model)

                # Generate image using official SDK
                # This returns a PIL.Image object directly
                # For Z-Image-Turbo, we need to pass the model parameter
                if "Z-Image-Turbo" in model or "Tongyi-MAI" in model:
                    image = client.text_to_image(prompt, model=model, width=832, height=512)
                else:
                    image = client.text_to_image(prompt)

                print(f"    ✓ Image generated successfully")

                # Save to designated output path
                image_file = generate_asset_filename(
                    run_id,
                    "image",
                    scene_id,
                    "png"
                )

                # Save PIL Image to file
                image.save(image_file, "PNG")
                print(f"    ✓ Image saved: {Path(image_file).name}")

                return str(image_file)

            except Exception as e:
                error_msg = str(e).lower()

                # Check if it's a model loading error (503)
                if "503" in error_msg or "loading" in error_msg:
                    print(f"    ⏳ Model loading...")

                    # Try to extract estimated time from error
                    try:
                        # Some errors include estimated_time in message
                        if "estimated_time" in error_msg:
                            import re
                            match = re.search(r'estimated_time["\s:]+(\d+)', error_msg)
                            if match:
                                wait_time = int(match.group(1))
                                print(f"    Waiting {wait_time} seconds for model to load...")
                                time.sleep(wait_time)
                                continue
                    except:
                        pass

                    # Default wait time
                    print(f"    Waiting 20 seconds for model to load...")
                    time.sleep(20)
                    continue

                # Check if it's a rate limit or quota error
                elif "rate limit" in error_msg or "quota" in error_msg:
                    print(f"    ⚠ Rate limit/quota exceeded")
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * 10  # Progressive backoff
                        print(f"    Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"    ✗ Rate limit persists, giving up on this model")
                        return None

                # Check if model is not available/accessible
                elif "404" in error_msg or "not found" in error_msg or "does not exist" in error_msg:
                    print(f"    ✗ Model not available on free tier: {e}")
                    return None  # Don't retry, model doesn't exist

                # Authentication/permission error
                elif "401" in error_msg or "403" in error_msg or "unauthorized" in error_msg:
                    print(f"    ✗ Authentication error: {e}")
                    return None  # Don't retry, token issue

                # Generic error - retry if attempts remaining
                else:
                    print(f"    ✗ Error: {e}")
                    if attempt < retries - 1:
                        print(f"    Retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                    else:
                        return None

        print(f"    ✗ Failed to generate image with {model} after {retries} attempts")
        return None

    def get_image_dimensions(self, aspect_ratio: str) -> tuple[int, int]:
        """Get width and height for given aspect ratio"""
        if aspect_ratio == "16:9":
            return (1024, 576)
        elif aspect_ratio == "9:16":
            return (576, 1024)
        elif aspect_ratio == "1:1":
            return (1024, 1024)
        else:
            return (1024, 576)  # Default to 16:9
