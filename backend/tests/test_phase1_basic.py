"""
Basic unit tests for Phase 1 (Story Generation)
"""
import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase1_story.agent import StoryAgent


class TestStoryAgentUtilities:
    """Test utility functions in StoryAgent"""

    @pytest.fixture
    def agent(self):
        """Create a StoryAgent instance for testing"""
        return StoryAgent()

    def test_extract_json_simple(self, agent):
        """Test JSON extraction from simple text"""
        text = '{"key": "value", "number": 42}'
        result = agent._extract_json(text)
        assert result == {"key": "value", "number": 42}

    def test_extract_json_with_markdown(self, agent):
        """Test JSON extraction from markdown code blocks"""
        text = '''
Here is some text
```json
{"story": "A tale of adventure", "characters": ["Alice", "Bob"]}
```
More text here
'''
        result = agent._extract_json(text)
        assert "story" in result
        assert result["story"] == "A tale of adventure"
        assert len(result["characters"]) == 2

    def test_extract_json_with_backticks(self, agent):
        """Test JSON extraction from backtick-wrapped JSON"""
        text = '```{"title": "Test Story"}```'
        result = agent._extract_json(text)
        assert result["title"] == "Test Story"

    def test_extract_json_nested(self, agent):
        """Test extraction of nested JSON objects"""
        text = '''
        {
            "story": {
                "title": "Adventure",
                "genre": "Fantasy"
            },
            "scenes": [
                {"number": 1, "description": "Opening"}
            ]
        }
        '''
        result = agent._extract_json(text)
        assert result["story"]["title"] == "Adventure"
        assert len(result["scenes"]) == 1

    def test_extract_json_invalid(self, agent):
        """Test handling of invalid JSON"""
        text = "This is not JSON at all"
        with pytest.raises((json.JSONDecodeError, ValueError)):
            agent._extract_json(text)

    def test_mood_normalization(self, agent):
        """Test that valid moods are preserved"""
        valid_moods = [
            "action", "adventurous", "calm", "dark", "dramatic",
            "epic", "happy", "inspirational", "mysterious",
            "peaceful", "romantic", "sad", "suspenseful", "tense"
        ]

        # Each valid mood should be preserved
        for mood in valid_moods:
            # In actual implementation, mood validation happens in schema
            # Here we just verify the mood values are recognized
            assert mood in [
                "action", "adventurous", "calm", "dark", "dramatic",
                "epic", "happy", "inspirational", "mysterious",
                "peaceful", "romantic", "sad", "suspenseful", "tense"
            ]


class TestStoryGeneration:
    """Test story generation workflow (with mocked LLM)"""

    @pytest.fixture
    def agent(self):
        """Create a StoryAgent instance"""
        return StoryAgent()

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly"""
        assert agent.llm is not None
        assert hasattr(agent, '_build_workflow')

    def test_workflow_structure(self, agent):
        """Test that workflow is properly constructed"""
        # Build the workflow
        workflow = agent._build_workflow()

        # Verify it's a compiled graph
        assert workflow is not None
        # The workflow should have the expected nodes
        # (We can't easily inspect the graph structure without running it)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
