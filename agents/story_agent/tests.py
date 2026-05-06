"""
Unit tests for Phase 1: Story & Script Generation
Run with: pytest phase1_story/tests.py
"""

import pytest
import json
from unittest.mock import Mock, patch
from .agent import StoryAgent
from shared.schema import Story, Scene, Character


class TestStoryAgent:
    """Test cases for StoryAgent"""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM responses for testing"""
        return {
            "story": '''```json
{
  "title": "Mars Crystal Discovery",
  "summary": "An astronaut discovers a mysterious glowing crystal on Mars that awakens ancient technology.",
  "scenes": [
    {
      "description": "Lonely astronaut walks across barren Martian landscape at sunset",
      "mood": "calm",
      "duration_s": 15
    },
    {
      "description": "Astronaut discovers glowing crystal embedded in rocks",
      "mood": "mysterious",
      "duration_s": 20
    },
    {
      "description": "Crystal activates, rocks begin to pulse with light",
      "mood": "tense",
      "duration_s": 25
    }
  ]
}
```''',
            "characters": '''```json
{
  "characters": [
    {
      "name": "Dr. Iris Chen",
      "role": "protagonist",
      "voice_gender": "female",
      "voice_tone": "calm",
      "voice_accent": "american",
      "visual_description": "Asian woman in orange spacesuit, determined expression"
    },
    {
      "name": "Narrator",
      "role": "narrator",
      "voice_gender": "male",
      "voice_tone": "authoritative",
      "voice_accent": "british",
      "visual_description": "N/A - voice only"
    }
  ]
}
```''',
            "dialogue": '''```json
{
  "dialogue": [
    {
      "character": "Narrator",
      "text": "The Martian sunset painted the horizon in shades of rust and amber."
    },
    {
      "character": "Dr. Iris Chen",
      "text": "Mission log, day 247. Still searching for signs of water."
    }
  ]
}
```''',
            "visual_prompt": "Cinematic wide shot of a lone astronaut in an orange spacesuit walking across a vast red Martian desert at golden hour. The sun sets behind distant rocky mountains, casting long shadows. Photorealistic, 8K, dramatic lighting, sense of isolation and wonder. Reddish-orange sky with wispy clouds. Rocky terrain with small pebbles and dust. No visible faces.",
        }

    def test_extract_json(self, mock_llm_response):
        """Test JSON extraction from various response formats"""
        agent = StoryAgent.__new__(StoryAgent)  # Create without __init__

        # Test with markdown code blocks
        result = agent._extract_json(mock_llm_response["story"])
        assert "title" in result
        assert "scenes" in result

        # Test with raw JSON
        raw_json = '{"test": "value"}'
        result = agent._extract_json(raw_json)
        assert result["test"] == "value"

    @patch('phase1_story.agent.ChatGroq')
    def test_generate_story_structure(self, mock_groq, mock_llm_response):
        """Test story structure generation"""
        # Setup mock
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = mock_llm_response["story"]
        mock_groq.return_value = mock_llm

        agent = StoryAgent()
        state = {
            "user_input": "A lonely astronaut discovers a glowing crystal on Mars",
            "params": {"genre": "Sci-Fi", "tone": "Cinematic", "duration": "60s", "aspect": "16:9"}
        }

        result = agent._generate_story(state)

        assert "story" in result
        assert "scenes" in result
        assert len(result["scenes"]) == 3
        assert result["story"].title == "Mars Crystal Discovery"

    @patch('phase1_story.agent.ChatGroq')
    def test_generate_characters(self, mock_groq, mock_llm_response):
        """Test character generation"""
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = mock_llm_response["characters"]
        mock_groq.return_value = mock_llm

        agent = StoryAgent()
        state = {
            "story": Story(
                title="Test",
                summary="Test summary",
                genre="Sci-Fi",
                tone="Cinematic",
                total_duration_ms=60000
            ),
            "scenes": [],
            "params": {}
        }

        result = agent._generate_characters(state)

        assert "characters" in result
        assert len(result["characters"]) == 2
        assert result["characters"][0].name == "Dr. Iris Chen"

    @patch('phase1_story.agent.ChatGroq')
    def test_mood_types(self, mock_groq):
        """Test that mood types are correctly assigned"""
        from shared.schema import MoodType

        valid_moods = ["calm", "tense", "upbeat", "mysterious", "dramatic", "sad", "ambient"]

        for mood in valid_moods:
            mood_enum = MoodType(mood)
            assert mood_enum.value == mood

    def test_scene_validation(self):
        """Test scene validation logic"""
        # Valid scene
        scene = Scene(
            id="scene_001",
            description="Test scene",
            visual_prompt="Test prompt",
            mood="calm",
            duration_ms=15000,
            dialogue=[]
        )

        assert scene.id == "scene_001"
        assert scene.mood == "calm"

    @patch('phase1_story.agent.ChatGroq')
    def test_full_pipeline(self, mock_groq, mock_llm_response):
        """Test complete story generation pipeline"""
        # Setup comprehensive mock
        mock_llm = Mock()

        def mock_invoke(messages):
            content = messages[0].content.lower()
            if "story title" in content or "scenes" in content and "json" in content:
                return Mock(content=mock_llm_response["story"])
            elif "character" in content:
                return Mock(content=mock_llm_response["characters"])
            elif "dialogue" in content:
                return Mock(content=mock_llm_response["dialogue"])
            else:
                return Mock(content=mock_llm_response["visual_prompt"])

        mock_llm.invoke.side_effect = mock_invoke
        mock_groq.return_value = mock_llm

        agent = StoryAgent()

        # Run full generation
        result = agent.generate(
            user_prompt="A lonely astronaut discovers a glowing crystal on Mars",
            params={"genre": "Sci-Fi", "tone": "Cinematic", "duration": "60s", "aspect": "16:9"}
        )

        # Validate output
        assert result.story is not None
        assert len(result.scenes) > 0
        assert len(result.characters) > 0
        assert result.phase_status["script"] == "complete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
