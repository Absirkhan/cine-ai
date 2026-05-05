# Edit Query Examples - Quick Reference

This document provides example queries for all supported edit operations.

---

## Voice & Audio

### Change Voice Tone
```
"Change voice tone to whispered"
"Make the narrator's voice energetic"
"Change all character voices to calm"
"Set narrator voice to dramatic with speed 1.5"
```

### Change Voice Speed
```
"Speed up narrator's speech"
"Slow down character voice to 0.8x"
"Make dialogue faster"
```

### Change Voice Pitch
```
"Increase narrator's pitch to 1.3"
"Make voice deeper (pitch 0.7)"
```

### Regenerate Script
```
"Regenerate the script"
"Rewrite the entire story"
"Generate a new script"
```

---

## Visual Filters

### Darken/Brighten
```
"Make scene 2 darker"
"Brighten scene 1"
"Darken all scenes"
"Make this scene 30% darker"
```

### Blur
```
"Apply blur to scene 3"
"Blur the background in scene 1"
```

### Color Adjustments
```
"Increase contrast in scene 2"
"Boost saturation"
"Make scene 1 grayscale"
"Apply sepia tone to scene 3"
```

### Temperature
```
"Make scene 1 warmer"
"Apply cool filter to scene 2"
"Add warm tones"
```

### Vignette
```
"Add vignette to scene 1"
"Apply vignette effect"
```

---

## Character Composition

### Change Characters in Scene
```
"In scene 1 change characters to male and female"
"Make scene 2 have one male and one female"
"Change scene 3 to show only one female"
"Add two male characters to scene 1"
```

### Change Character Design
```
"Change character design for narrator"
"Redesign the protagonist"
"Make narrator look older"
"Change character appearance to futuristic style"
```

### Regenerate Scene
```
"Regenerate scene 3"
"Recreate scene 1 visuals"
"Regenerate all scenes"
```

---

## Background Music (BGM)

### Add BGM
```
"Add background music"
"Add BGM to scene 2"
"Add background music to all scenes"
"Include ambient music"
```

### Change BGM
```
"Change background music to tense"
"Make BGM more upbeat"
"Switch to dramatic music in scene 3"
```

### Change Mood
```
"Change mood to mysterious"
"Make scene 1 more dramatic"
"Set mood to calm for all scenes"
```

### Remove BGM
```
"Remove background music from scene 2"
"Remove BGM"
"Take out the music from scene 3"
```

---

## Timing & Speed

### Adjust Duration
```
"Adjust scene duration to 5000ms"
"Make scene 2 last 8 seconds"
"Set duration to 3000ms"
```

### Speed Up
```
"Speed up scene 2"
"Make this scene faster"
"Speed up to 1.5x"
"Increase playback speed in scene 3"
```

### Slow Down
```
"Slow down scene 1"
"Make this scene slower"
"Reduce speed to 0.75x"
"Slow motion effect in scene 2"
```

---

## Subtitles

### Show/Hide Subtitles
```
"Remove the subtitle from scene 1"
"Hide subtitles in scene 2"
"Remove all subtitles"
"Show subtitles in scene 3"
"Add subtitles back to scene 1"
```

---

## Global Operations

### Change Script
```
"Change the dialogue"
"Modify the story"
"Update the script"
```

### Full Regenerate
```
"Regenerate the entire video"
"Start over from scratch"
"Recreate everything"
```

---

## Complex Multi-Part Queries

### Multiple Scenes
```
"Make scene 1 darker and scene 3 brighter"
"Add BGM to scene 1 and remove it from scene 3"
"Speed up scene 2 and slow down scene 4"
```

### Multiple Actions on Same Scene
```
"Make scene 2 darker and remove subtitles"
"Add BGM and speed up scene 1"
"Apply blur and darken scene 3"
```

### Character Composition Across Scenes
```
"In scene 1 change to male and female, in scene 3 also male and female"
"Make scene 1 have two males, scene 2 one female, scene 3 one male and one female"
"In first scene show male and female, keep second scene same, third scene only female"
```

### Mixed Edits
```
"Change narrator's voice to whispered and make scene 1 darker"
"Remove subtitles, add BGM, and speed up scene 2"
"Make scene 1 darker, scene 2 brighter, and add dramatic music to all scenes"
```

### Complex Example (From Requirements)
```
"In the first scene, two males can be seen however the voice is of one girl and one boy, so change the first to male and female, keep second scene same, and third scene also as both male and female, only one female is seen in last scene"
```

**This will be decomposed into:**
1. "In scene 1 change characters to male and female"
2. "In scene 3 change characters to male and female"
3. "In scene 4 change characters to only one female"

---

## Intent Type Reference

| Query Pattern | Detected Intent | Target | Scope Example |
|--------------|----------------|--------|---------------|
| "Change voice to..." | `change_voice` | `audio` | `character:Narrator` |
| "Make scene X darker" | `apply_filter` | `video_frame` | `scene:scene_002` |
| "Add background music" | `add_bgm` | `bgm` | `all` |
| "Remove subtitle" | `toggle_subtitles` | `composition` | `scene:scene_001` |
| "Speed up scene X" | `speed_up` | `video` | `scene:scene_002` |
| "Change characters to..." | `change_scene_characters` | `video_frame` | `scene:scene_001` |
| "Regenerate script" | `regenerate_script` | `script` | `all` |

---

## Parameter Extraction Examples

### Voice Parameters
```
Query: "Change narrator's voice to whispered with speed 1.2 and pitch 0.9"

Parameters:
{
  "tone": "whispered",
  "speed": 1.2,
  "pitch": 0.9
}
```

### Filter Parameters
```
Query: "Make scene 2 darker by 50%"

Parameters:
{
  "filter": "darken",
  "amount": 0.5
}
```

### Character Parameters
```
Query: "In scene 1 change to one male and two females"

Parameters:
{
  "genders": ["male", "female", "female"],
  "character_count": 3
}
```

### Speed Parameters
```
Query: "Speed up scene 3 to 2x"

Parameters:
{
  "speed_multiplier": 2.0
}
```

### Mood Parameters
```
Query: "Change BGM to tense mood"

Parameters:
{
  "mood": "tense"
}
```

---

## Scope Targeting Examples

### Specific Scene
```
"Make scene 2 darker" → scope: "scene:scene_002"
"Speed up scene 1" → scope: "scene:scene_001"
"Remove subtitles from scene 3" → scope: "scene:scene_003"
```

### Specific Character
```
"Change narrator's voice to whispered" → scope: "character:Narrator"
"Make protagonist's voice energetic" → scope: "character:Protagonist"
```

### All Scenes/Characters
```
"Make all scenes darker" → scope: "all"
"Add background music" → scope: "all"
"Change voice tone to calm" → scope: "all"
```

---

## Advanced Usage

### Conditional Edits
```
"In scene 1 change to male and female, keep scene 2 same, in scene 3 change to one female"
```
The system will skip "keep scene 2 same" (no-op) and only execute edits for scenes 1 and 3.

### Sequential Multi-Step
```
"First make scene 1 darker, then add BGM, finally speed it up"
```
All three intents will be executed in sequence on scene 1.

### Bulk Operations
```
"Make scenes 1, 2, and 3 darker"
```
Will be decomposed into three separate `apply_filter` intents.

---

## Tips for Best Results

1. **Be Specific About Scenes**
   - ✅ "Make scene 2 darker"
   - ❌ "Make it darker" (ambiguous)

2. **Use Character Names**
   - ✅ "Change narrator's voice to whispered"
   - ❌ "Change the voice" (which character?)

3. **Specify Amounts When Needed**
   - ✅ "Speed up scene 1 to 1.5x"
   - ✅ "Make scene 2 30% darker"

4. **Use Conjunctions for Multi-Part**
   - "Make scene 1 darker **and** scene 3 brighter"
   - "Remove subtitles **and** add BGM"
   - "In scene 1... **then** in scene 2..."

5. **Natural Language Works**
   - "Make the scene way darker" → detects filter with high amount
   - "Add some chill background music" → detects calm mood
   - "Speed this up a lot" → detects high speed multiplier

---

## Summary

The edit system supports:
- ✅ 16 different intent types
- ✅ Scene-specific and global targeting
- ✅ Complex multi-part commands
- ✅ Natural language understanding
- ✅ Parameter extraction from context
- ✅ Intelligent decomposition

**Try any combination of the above patterns to create your desired edits!**
