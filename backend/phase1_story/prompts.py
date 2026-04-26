"""
Prompt templates for Phase 1: Story & Script Generation
Engineered for structured output with Groq/LLaMA
"""

STORY_GENERATION_PROMPT = """You are a professional screenplay writer and creative director. Your task is to transform the user's idea into a complete, scene-by-scene story structure.

USER INPUT:
{user_prompt}

PARAMETERS:
- Genre: {genre}
- Tone: {tone}
- Target Duration: {duration}
- Aspect Ratio: {aspect_ratio}

INSTRUCTIONS:
1. Create a compelling story title and summary
2. Break the story into 3-5 distinct scenes
3. Each scene should have:
   - Clear visual description for AI image generation
   - Specific mood for background music selection
   - Estimated duration that adds up to target duration
4. Ensure visual variety and narrative arc (setup → conflict → resolution)

Respond with ONLY a JSON object in this exact format:
```json
{{
  "title": "Story Title",
  "summary": "Brief 2-3 sentence summary",
  "scenes": [
    {{
      "description": "Detailed scene description",
      "mood": "calm|tense|upbeat|mysterious|dramatic|sad",
      "duration_s": 15
    }}
  ]
}}
```

Do not include any other text. Only output the JSON."""

CHARACTER_GENERATION_PROMPT = """You are a character designer for animated films. Based on the story, create detailed character profiles.

STORY:
{story_summary}

SCENES:
{scenes_summary}

INSTRUCTIONS:
1. Identify all characters needed (typically 1-3 for short films)
2. For each character, define:
   - Name and role
   - Voice characteristics (gender, tone, accent if relevant)
   - Visual appearance for AI image generation
3. Ensure character voices are distinct and appropriate for their role

Respond with ONLY a JSON object in this exact format:
```json
{{
  "characters": [
    {{
      "name": "Character Name",
      "role": "protagonist|narrator|antagonist|supporting",
      "voice_gender": "male|female|neutral",
      "voice_tone": "calm|energetic|whispered|authoritative",
      "voice_accent": "american|british|neutral",
      "visual_description": "Detailed physical appearance"
    }}
  ]
}}
```

Do not include any other text. Only output the JSON."""

DIALOGUE_GENERATION_PROMPT = """You are a dialogue writer for animated short films. Create natural, engaging dialogue for this scene.

SCENE:
{scene_description}

AVAILABLE CHARACTERS:
{characters_list}

SCENE MOOD: {mood}
SCENE DURATION: {duration_s} seconds

INSTRUCTIONS:
1. Write 2-6 dialogue lines total for this scene
2. Match the tone and mood of the scene
3. Keep dialogue concise - this is for voiceover narration
4. If appropriate, include a narrator for scene-setting
5. Dialogue should fit within the scene duration (estimate ~3 seconds per line)

Respond with ONLY a JSON object in this exact format:
```json
{{
  "dialogue": [
    {{
      "character": "Character Name or Narrator",
      "text": "The dialogue text"
    }}
  ]
}}
```

Do not include any other text. Only output the JSON."""

VISUAL_PROMPT_GENERATION = """You are a prompt engineer for AI image generation. Create a detailed visual prompt for this scene.

SCENE DESCRIPTION:
{scene_description}

STORY CONTEXT:
Genre: {genre}
Tone: {tone}
Aspect Ratio: {aspect_ratio}

INSTRUCTIONS:
1. Create a highly detailed prompt for FLUX.1-schnell image generation
2. Include:
   - Visual style matching the tone (cinematic, painterly, etc.)
   - Lighting and atmosphere matching the mood
   - Composition details for the aspect ratio
   - Specific visual elements from the scene description
3. Keep prompt under 200 words
4. Do NOT include characters with faces (AI struggles with faces in group shots)
5. Focus on environment, atmosphere, and setting

Respond with ONLY the prompt text, no JSON, no additional formatting."""

MOOD_CLASSIFICATION_PROMPT = """Based on this scene description, classify the dominant mood for background music selection.

SCENE: {scene_description}

Available moods: calm, tense, upbeat, mysterious, dramatic, sad

Respond with ONLY one word - the mood classification."""
