# Edit System Flow Diagrams

Visual representations of how the multi-intent edit system processes different types of queries.

---

## Flow 1: Simple Single-Intent Edit

```
┌─────────────────────────────────────────────────┐
│ User Query: "Make scene 2 darker"              │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ IntentDecomposer                                │
│ • Heuristic check: Simple command detected     │
│ • No decomposition needed                      │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Output: ["Make scene 2 darker"]
                    ▼
┌─────────────────────────────────────────────────┐
│ IntentParser (LLM)                              │
│ • Classify intent type: apply_filter           │
│ • Identify target: video_frame                 │
│ • Extract scope: scene:scene_002               │
│ • Extract parameters: {filter: darken, ...}    │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Output: EditIntent(...)
                    ▼
┌─────────────────────────────────────────────────┐
│ EditExecutor                                    │
│ • Create snapshot (before)                     │
│ • Apply darken filter to scene_002             │
│ • Update scene.image_file path                 │
│ • Set phase_status["video"] = needs_regen      │
│ • Create snapshot (after)                      │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Orchestrator                                    │
│ • Detect video regeneration needed             │
│ • Call VideoGenerator.generate()               │
│ • Recompose final video                        │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Result: Scene 2 is now darker ✓                │
└─────────────────────────────────────────────────┘
```

---

## Flow 2: Multi-Part Command (Same Intent Type)

```
┌─────────────────────────────────────────────────┐
│ User Query:                                     │
│ "Make scene 1 darker and scene 3 brighter"     │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ IntentDecomposer (LLM)                          │
│ • Detect multi-part command                    │
│ • Decompose using LLM                          │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Output: [
                    │   "Make scene 1 darker",
                    │   "Make scene 3 brighter"
                    │ ]
                    ▼
┌─────────────────────────────────────────────────┐
│ IntentParser (LLM) - Parallel Processing       │
├─────────────────┬───────────────────────────────┤
│ Parse cmd 1     │ Parse cmd 2                   │
│ ↓               │ ↓                             │
│ Intent 1:       │ Intent 2:                     │
│ apply_filter    │ apply_filter                  │
│ scope: scene_001│ scope: scene_003              │
│ filter: darken  │ filter: brighten              │
└─────────────────┴───────────────┬───────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────┐
│ EditExecutor - Sequential Execution             │
├─────────────────────────────────────────────────┤
│ [1/2] Execute Intent 1                          │
│   • Snapshot before                             │
│   • Apply darken to scene_001                   │
│   • Snapshot after                              │
├─────────────────────────────────────────────────┤
│ [2/2] Execute Intent 2                          │
│   • Snapshot before                             │
│   • Apply brighten to scene_003                 │
│   • Snapshot after                              │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Orchestrator                                    │
│ • Regenerate scene_001 and scene_003            │
│ • Recompose video                               │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Result: Scene 1 darker, Scene 3 brighter ✓      │
└─────────────────────────────────────────────────┘
```

---

## Flow 3: Complex Multi-Part Command (Different Intent Types)

```
┌─────────────────────────────────────────────────┐
│ User Query:                                     │
│ "Change narrator's voice to whispered and      │
│  make scene 2 darker"                          │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ IntentDecomposer (LLM)                          │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Output: [
                    │   "Change narrator's voice to whispered",
                    │   "Make scene 2 darker"
                    │ ]
                    ▼
┌─────────────────────────────────────────────────┐
│ IntentParser (LLM) - Parallel                   │
├─────────────────┬───────────────────────────────┤
│ Intent 1:       │ Intent 2:                     │
│ change_voice    │ apply_filter                  │
│ target: audio   │ target: video_frame           │
│ scope: Narrator │ scope: scene_002              │
└─────────────────┴───────────────┬───────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────┐
│ EditExecutor - Sequential                       │
├─────────────────────────────────────────────────┤
│ [1/2] Execute change_voice                      │
│   • Update Narrator.voice_params.tone           │
│   • Set phase_status["audio"] = needs_regen     │
├─────────────────────────────────────────────────┤
│ [2/2] Execute apply_filter                      │
│   • Apply darken to scene_002                   │
│   • Set phase_status["video"] = needs_regen     │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Orchestrator - Cascading Regeneration           │
├─────────────────────────────────────────────────┤
│ 1. Detect audio needs regeneration             │
│    → Rerun audio phase (TTS for Narrator)      │
│                                                 │
│ 2. Detect video needs regeneration             │
│    → Rerun video phase (scene_002 + compose)   │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ Result: Narrator whispered + Scene 2 darker ✓   │
└─────────────────────────────────────────────────┘
```

---

## Flow 4: Your Complex Example

```
┌───────────────────────────────────────────────────────────┐
│ User Query:                                               │
│ "In the first scene, two males can be seen however       │
│  the voice is of one girl and one boy, so change the     │
│  first to male and female, keep second scene same,       │
│  and third scene also as both male and female,           │
│  only one female is seen in last scene."                 │
└──────────────────────┬────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────┐
│ IntentDecomposer (LLM)                                    │
│ • Detect multi-scene, multi-part command                 │
│ • Extract: scene 1, scene 2, scene 3, scene 4            │
│ • Filter out: "keep second scene same" (no-op)           │
└──────────────────────┬────────────────────────────────────┘
                       │
                       │ Output: [
                       │   "In scene 1 change to male and female",
                       │   "In scene 3 change to male and female",
                       │   "In scene 4 change to only one female"
                       │ ]
                       ▼
┌───────────────────────────────────────────────────────────┐
│ IntentParser (LLM) - 3 Parallel Calls                     │
├──────────────┬──────────────┬─────────────────────────────┤
│ Intent 1     │ Intent 2     │ Intent 3                    │
│              │              │                             │
│ Type:        │ Type:        │ Type:                       │
│ change_scene │ change_scene │ change_scene_characters     │
│ _characters  │ _characters  │                             │
│              │              │                             │
│ Scope:       │ Scope:       │ Scope:                      │
│ scene_001    │ scene_003    │ scene_004                   │
│              │              │                             │
│ Params:      │ Params:      │ Params:                     │
│ genders:     │ genders:     │ genders: ["female"]         │
│ ["male",     │ ["male",     │ character_count: 1          │
│  "female"]   │  "female"]   │                             │
│ count: 2     │ count: 2     │                             │
└──────────────┴──────────────┴──────────────┬──────────────┘
                                             │
                                             ▼
┌───────────────────────────────────────────────────────────┐
│ EditExecutor - Sequential (3 intents)                     │
├───────────────────────────────────────────────────────────┤
│ [1/3] Execute change_scene_characters for scene_001       │
│   • Create snapshot before                                │
│   • scene_001.character_visual_overrides = {              │
│       "Character1": {"gender": "male"},                   │
│       "Character2": {"gender": "female"}                  │
│     }                                                     │
│   • scene_001.characters_in_scene = [Char1, Char2]        │
│   • Create snapshot after                                 │
├───────────────────────────────────────────────────────────┤
│ [2/3] Execute change_scene_characters for scene_003       │
│   • scene_003.character_visual_overrides = {              │
│       "Character1": {"gender": "male"},                   │
│       "Character2": {"gender": "female"}                  │
│     }                                                     │
│   • scene_003.characters_in_scene = [Char1, Char2]        │
├───────────────────────────────────────────────────────────┤
│ [3/3] Execute change_scene_characters for scene_004       │
│   • scene_004.character_visual_overrides = {              │
│       "Character1": {"gender": "female"}                  │
│     }                                                     │
│   • scene_004.characters_in_scene = [Char1]               │
├───────────────────────────────────────────────────────────┤
│ • Set phase_status["video"] = "needs_regeneration"        │
└──────────────────────┬────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────┐
│ Orchestrator - Video Phase Regeneration                  │
├───────────────────────────────────────────────────────────┤
│ VideoGenerator.generate():                               │
│                                                           │
│ For scene_001:                                            │
│   • Read character_visual_overrides                       │
│   • Generate image with male + female characters          │
│   • Apply Ken Burns animation                            │
│                                                           │
│ For scene_002:                                            │
│   • No overrides → use original                          │
│                                                           │
│ For scene_003:                                            │
│   • Read character_visual_overrides                       │
│   • Generate image with male + female characters          │
│                                                           │
│ For scene_004:                                            │
│   • Read character_visual_overrides                       │
│   • Generate image with single female character           │
│                                                           │
│ Compositor:                                               │
│   • Stitch all scenes with audio + BGM                   │
│   • Apply subtitles                                       │
│   • Output final video                                    │
└──────────────────────┬────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────┐
│ ✓ Final Result:                                           │
│   Scene 1: Male + Female                                  │
│   Scene 2: Unchanged (original)                          │
│   Scene 3: Male + Female                                  │
│   Scene 4: Single Female                                  │
│                                                           │
│ All edits reversible via undo!                           │
└───────────────────────────────────────────────────────────┘
```

---

## Data Flow: EditIntent Structure

```
EditIntent
├── intent_type: str
│   └── One of 16 types (change_voice, apply_filter, etc.)
│
├── target: str
│   └── One of 6 targets (audio, video_frame, video, script, bgm, composition)
│
├── scope: Optional[str]
│   ├── "character:Name" → Target specific character
│   ├── "scene:ID" → Target specific scene
│   └── "all" → Target all
│
├── parameters: Dict[str, Any]
│   ├── For change_voice: {tone, speed, pitch}
│   ├── For apply_filter: {filter, amount}
│   ├── For change_scene_characters: {genders, character_count}
│   ├── For speed_up: {speed_multiplier}
│   └── ... (varies by intent_type)
│
├── original_query: str
│   └── The user's original command
│
└── priority: int
    └── Execution priority (0 = highest)
```

---

## State Transition Diagram

```
┌─────────────────┐
│ Initial State   │
│ • All scenes    │
│ • Characters    │
│ • Assets        │
└────────┬────────┘
         │
         │ User Edit Command
         ▼
┌─────────────────┐
│ Parse & Execute │
│ • Decompose     │
│ • Classify      │
│ • Execute       │
└────────┬────────┘
         │
         ├─── Snapshot (before)
         │
         │ Modify State
         ▼
┌─────────────────┐
│ Updated State   │
│ • Modified      │
│ • Regeneration  │
│   flags set     │
└────────┬────────┘
         │
         ├─── Snapshot (after)
         │
         │ Check phase_status
         ▼
┌─────────────────────────────────────┐
│ Cascading Regeneration              │
├─────────────────────────────────────┤
│ script needs_regeneration?          │
│   YES → Regenerate script, audio,   │
│         video                       │
│                                     │
│ audio needs_regeneration?           │
│   YES → Regenerate audio, video     │
│                                     │
│ video needs_regeneration?           │
│   YES → Regenerate video            │
│                                     │
│ video needs_recomposition?          │
│   YES → Recompose only              │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Final State     │
│ • New assets    │
│ • Updated video │
│ • History saved │
└─────────────────┘
         │
         │ User can:
         ├─── Execute more edits
         ├─── Undo this edit
         ├─── Redo undone edit
         └─── View edit history
```

---

## Undo/Redo Flow

```
Version Timeline:
─────────────────────────────────────────────────►

v1         v2         v3         v4         v5
│          │          │          │          │
Initial    Before     After      Before     After
State      Edit 1     Edit 1     Edit 2     Edit 2

          ┌─────────────────────────────────┐
          │ Current Version = 5             │
          └─────────────────────────────────┘

User calls: undo(steps=1)
          ↓

v1         v2         v3         v4         v5
│          │          │          │
Initial    Before     After      Before
State      Edit 1     Edit 1     Edit 2
                                 ▲
                                 │
                      ┌──────────┴──────────┐
                      │ Current Version = 4 │
                      └─────────────────────┘

User calls: redo(steps=1)
          ↓

v1         v2         v3         v4         v5
│          │          │          │          │
Initial    Before     After      Before     After
State      Edit 1     Edit 1     Edit 2     Edit 2
                                            ▲
                                            │
                                 ┌──────────┴──────────┐
                                 │ Current Version = 5 │
                                 └─────────────────────┘
```

---

## Intent Execution Order with Priority

```
Intents received:
┌──────────────────────────────────────┐
│ Intent 1: change_voice (priority: 2) │
│ Intent 2: regenerate_script (p: 0)  │
│ Intent 3: apply_filter (priority: 1) │
└──────────────────────────────────────┘
              │
              │ Sort by priority (0 = highest)
              ▼
┌──────────────────────────────────────┐
│ Execution order:                     │
│ 1. regenerate_script (priority: 0)  │
│ 2. apply_filter (priority: 1)       │
│ 3. change_voice (priority: 2)       │
└──────────────────────────────────────┘
              │
              │ Execute sequentially
              ▼
┌──────────────────────────────────────┐
│ Result: Script → Filter → Voice      │
└──────────────────────────────────────┘

Note: Currently all intents default to priority=0
      (sequential execution in parsed order)
      Future enhancement: smart priority assignment
```

---

## Error Handling Flow

```
┌──────────────────┐
│ User Command     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     LLM Fails?
│ Decomposer (LLM) │────────────►┌──────────────────┐
└────────┬─────────┘  YES        │ Fallback:        │
         │             ──────────►│ Treat as single  │
         │  NO                    │ command          │
         ▼                        └──────────────────┘
┌──────────────────┐     LLM Fails?
│ Parser (LLM)     │────────────►┌──────────────────┐
└────────┬─────────┘  YES        │ Fallback:        │
         │             ──────────►│ change_script    │
         │  NO                    │ intent           │
         ▼                        └──────────────────┘
┌──────────────────┐     Execution Fails?
│ Executor         │────────────►┌──────────────────┐
└────────┬─────────┘  YES        │ Log error,       │
         │             ──────────►│ continue to next │
         │  NO                    │ intent           │
         ▼                        └──────────────────┘
┌──────────────────┐     Regeneration Fails?
│ Orchestrator     │────────────►┌──────────────────┐
└────────┬─────────┘  YES        │ Keep old assets, │
         │             ──────────►│ notify user      │
         │  NO                    └──────────────────┘
         ▼
┌──────────────────┐
│ Success! ✓       │
└──────────────────┘
```

---

## Summary

These diagrams illustrate:

1. **Simple Edit Flow** - Fast path for single intents
2. **Multi-Part Flow** - Parallel parsing, sequential execution
3. **Mixed Intent Types** - Different targets, cascading regeneration
4. **Your Complex Example** - Complete end-to-end breakdown
5. **Data Structures** - Intent composition
6. **State Transitions** - Before/after snapshots
7. **Undo/Redo** - Version timeline management
8. **Priority** - Execution ordering (future enhancement)
9. **Error Handling** - Graceful degradation at each step

The system provides a robust, intelligent, and user-friendly editing experience!
