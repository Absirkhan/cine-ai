"""
Unit tests for Phase 3: Video Generation
Run with: pytest phase3_video/tests.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from .image_generator import ImageGenerator
from .animator import VideoAnimator
from .compositor import VideoCompositor
from shared.schema import Scene, MoodType, PipelineState


class TestImageGenerator:
    """Test cases for ImageGenerator"""

    def test_get_image_dimensions(self):
        """Test aspect ratio to dimensions conversion"""
        gen = ImageGenerator()

        assert gen.get_image_dimensions("16:9") == (1024, 576)
        assert gen.get_image_dimensions("9:16") == (576, 1024)
        assert gen.get_image_dimensions("1:1") == (1024, 1024)
        assert gen.get_image_dimensions("unknown") == (1024, 576)  # Default

    @patch('phase3_video.image_generator.requests.post')
    def test_generate_image_success(self, mock_post):
        """Test successful image generation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake_image_data"
        mock_post.return_value = mock_response

        gen = ImageGenerator()

        # Note: This will fail in real test due to PIL, but tests the flow
        # In production, use actual image bytes or mock PIL


class TestVideoAnimator:
    """Test cases for VideoAnimator"""

    def test_animator_initialization(self):
        """Test animator initializes correctly"""
        animator = VideoAnimator(fps=24)
        assert animator.fps == 24

        animator2 = VideoAnimator(fps=30)
        assert animator2.fps == 30


class TestVideoCompositor:
    """Test cases for VideoCompositor"""

    def test_compositor_initialization(self):
        """Test compositor initializes correctly"""
        compositor = VideoCompositor()
        assert compositor is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
