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

        # Primary model (FLUX.1-schnell - fast, high quality)
        self.primary_model = "black-forest-labs/FLUX.1-schnell"

        # Fallback model (Stable Diffusion XL - reliable on free tier)
        self.fallback_model = "stabilityai/stable-diffusion-xl-base-1.0"

        # Current active client (will be initialized on first use)
        self.client = None
        self.current_model = None

    def _get_client(self, model: str) -> InferenceClient:
        """
        Get or create InferenceClient for specified model

        Args:
            model: Model identifier (e.g., "black-forest-labs/FLUX.1-schnell")

        Returns:
            Configured InferenceClient instance
        """
        return InferenceClient(model=model, token=self.hf_token)

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

        # Try primary model first
        result = self._try_generate_with_model(
            model=self.primary_model,
            prompt=prompt,
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
            prompt=prompt,
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
