"""
Unit tests for Phase 5: Edit Agent
Run with: pytest phase5_edit/tests.py
"""

import pytest
from unittest.mock import Mock, patch

from .intent_parser import IntentParser
from .filters import ImageFilters
from .edit_agent import EditAgent
from shared.schema import EditIntent


class TestIntentParser:
    """Test cases for IntentParser"""

    @patch('phase5_edit.intent_parser.ChatGroq')
    def test_parse_change_voice(self, mock_groq):
        """Test parsing voice change command"""
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = '''
        {
            "intent_type": "change_voice",
            "target": "audio",
            "scope": "character:Narrator",
            "parameters": {"tone": "whispered"}
        }
        '''
        mock_groq.return_value = mock_llm

        parser = IntentParser()
        intent = parser.parse("Change voice tone to whispered for narrator")

        assert intent.intent_type == "change_voice"
        assert intent.target == "audio"
        assert "whispered" in str(intent.parameters.get("tone", "")).lower()

    @patch('phase5_edit.intent_parser.ChatGroq')
    def test_parse_apply_filter(self, mock_groq):
        """Test parsing filter command"""
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = '''
        {
            "intent_type": "apply_filter",
            "target": "video_frame",
            "scope": "scene:scene_001",
            "parameters": {"filter": "darken", "amount": 0.3}
        }
        '''
        mock_groq.return_value = mock_llm

        parser = IntentParser()
        intent = parser.parse("Make scene 1 darker")

        assert intent.intent_type == "apply_filter"
        assert intent.target == "video_frame"


class TestImageFilters:
    """Test cases for ImageFilters"""

    def test_filter_functions_exist(self):
        """Test that all filter functions exist"""
        filters = ImageFilters()

        assert hasattr(filters, 'darken')
        assert hasattr(filters, 'brighten')
        assert hasattr(filters, 'adjust_contrast')
        assert hasattr(filters, 'adjust_saturation')
        assert hasattr(filters, 'apply_blur')
        assert hasattr(filters, 'to_grayscale')
        assert hasattr(filters, 'apply_sepia')


class TestEditAgent:
    """Test cases for EditAgent"""

    def test_edit_agent_initialization(self):
        """Test edit agent initializes correctly"""
        agent = EditAgent()

        assert agent.parser is not None
        assert agent.executor is not None

    def test_supports_edit_type(self):
        """Test edit type support checking"""
        agent = EditAgent()

        assert agent.supports_edit_type("change_voice")
        assert agent.supports_edit_type("apply_filter")
        assert agent.supports_edit_type("change_bgm")
        assert not agent.supports_edit_type("invalid_type")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
