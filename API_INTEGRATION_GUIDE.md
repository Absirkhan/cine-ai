# CineAI API Integration Guide

Complete guide for integrating the frontend with your FastAPI backend.

## Overview

The frontend now has a **complete API service layer** with utility functions and React hooks ready to connect to your backend. The Home screen is fully integrated as a working example.

---

## API Service Layer

### 📁 **`src/services/api.ts`**

Centralized API functions for all backend calls:

```typescript
// Video generation
generateVideo(request: GenerateRequest): Promise<GenerateResponse>

// Job status
getJobStatus(runId: string): Promise<JobStatusResponse>

// Video output
getVideoOutput(runId: string): Promise<any>

// Version history
getVersionHistory(runId: string): Promise<any>

// Phase re-run
rerunPhase(runId: string, phaseId: string): Promise<any>

// Chat message
sendChatMessage(runId: string, message: string): Promise<any>
```

### 📁 **`src/hooks/useProgressWebSocket.ts`**

React hook for live progress updates:

```typescript
const { connected, error, disconnect } = useProgressWebSocket({
  runId: 'run_abc123',
  onLog: (log) => console.log(log),
  onPhaseUpdate: (phaseId, status) => console.log(phaseId, status),
  enabled: true,
});
```

### 📁 **`src/hooks/useChatWebSocket.ts`**

React hook for Edit Agent chat:

```typescript
const { connected, error, sending, sendMessage, disconnect } = useChatWebSocket({
  runId: 'run_abc123',
  onMessage: (message) => console.log(message),
  enabled: true,
});
```

---

## Integration Examples

### ✅ **Home Screen** (Already Integrated)

**File:** `src/pages/Home.tsx`

**What was done:**
1. Import `generateVideo` from `src/services/api`
2. Call API on form submit
3. Navigate to `/progress/:runId` with real run_id
4. Handle errors with fallback to mock navigation
5. Display error message to user

**Code:**
```typescript
import { generateVideo } from '../services/api';

const handleGenerate = async () => {
  setGenerating(true);
  setError(null);

  try {
    const response = await generateVideo({ prompt, genre, tone, duration, aspect });
    navigate(`/progress/${response.run_id}`);
  } catch (err) {
    setError(err.message);
    // Fallback for development
    navigate('/progress/run_a7b3f1');
  }
};
```

---

### 🔧 **Pipeline Screen** (Ready to Integrate)

**File:** `src/pages/Pipeline.tsx`

**Current state:** Uses mock `phaseStates`

**How to integrate:**

1. **Import API service:**
   ```typescript
   import { getJobStatus, rerunPhase } from '../services/api';
   ```

2. **Fetch real phase data on mount:**
   ```typescript
   useEffect(() => {
     if (!jobId) return;

     const fetchStatus = async () => {
       try {
         const data = await getJobStatus(jobId);
         setPhaseStates(data.phases);
       } catch (err) {
         console.error('Failed to fetch job status:', err);
       }
     };

     fetchStatus();
     const interval = setInterval(fetchStatus, 3000); // Poll every 3s
     return () => clearInterval(interval);
   }, [jobId]);
   ```

3. **Wire up re-run button:**
   ```typescript
   const handleRerun = async (phaseId: string) => {
     try {
       await rerunPhase(jobId!, phaseId);
       // Refresh status after re-run
       const data = await getJobStatus(jobId!);
       setPhaseStates(data.phases);
     } catch (err) {
       console.error('Failed to re-run phase:', err);
     }
   };
   ```

---

### 🔧 **Progress Screen** (Ready to Integrate)

**File:** `src/pages/Progress.tsx`

**Current state:** Uses mock logs with `setInterval`

**How to integrate:**

1. **Import WebSocket hook:**
   ```typescript
   import { useProgressWebSocket } from '../hooks/useProgressWebSocket';
   ```

2. **Replace mock logs with real WebSocket:**
   ```typescript
   const [logs, setLogs] = useState<LogEntry[]>([]);
   const [phaseStates, setPhaseStates] = useState<Record<string, PhaseState>>({});

   useProgressWebSocket({
     runId: jobId!,
     onLog: (log) => {
       setLogs((prev) => [...prev, log].slice(-60)); // Keep last 60 logs
     },
     onPhaseUpdate: (phaseId, status) => {
       setPhaseStates((prev) => ({
         ...prev,
         [phaseId]: status,
       }));
     },
     enabled: !!jobId,
   });
   ```

3. **Remove mock `setInterval`:** Delete the effect that generates fake logs

---

### 🔧 **Preview Screen** (Ready to Integrate)

**File:** `src/pages/Preview.tsx`

**Current state:** Uses mock `versions` and `scenes`

**How to integrate:**

1. **Import API service:**
   ```typescript
   import { getVideoOutput, getVersionHistory } from '../services/api';
   ```

2. **Fetch video data on mount:**
   ```typescript
   useEffect(() => {
     if (!jobId) return;

     const fetchData = async () => {
       try {
         const [output, versions] = await Promise.all([
           getVideoOutput(jobId),
           getVersionHistory(jobId),
         ]);

         setScenes(output.scenes || []);
         setVersions(versions || []);
         // Set active version
         const active = versions.find((v: any) => v.active);
         if (active) activateVersion(active.id);
       } catch (err) {
         console.error('Failed to fetch video data:', err);
       }
     };

     fetchData();
   }, [jobId]);
   ```

3. **Update version activation to call backend:**
   ```typescript
   const activateVersion = async (versionId: string) => {
     try {
       // If you have an endpoint to activate versions:
       // await fetch(`/api/runs/${jobId}/versions/${versionId}/activate`, { method: 'POST' });

       setVersions(vs => vs.map(v => ({ ...v, active: v.id === versionId })));
     } catch (err) {
       console.error('Failed to activate version:', err);
     }
   };
   ```

---

### 🔧 **EditAgent Screen** (Ready to Integrate)

**File:** `src/pages/EditAgent.tsx`

**Current state:** Uses mock chat with `buildReply` function

**How to integrate:**

1. **Import WebSocket hook:**
   ```typescript
   import { useChatWebSocket } from '../hooks/useChatWebSocket';
   ```

2. **Replace mock chat with real WebSocket:**
   ```typescript
   const [messages, setMessages] = useState<ChatMessage[]>([
     {
       role: 'system',
       content: `Edit Agent is watching ${jobId}. I can adjust script, audio, video frames, or pacing.`,
       time: new Date().toTimeString().slice(0, 8),
     },
   ]);

   const { connected, sending, sendMessage: wsSendMessage } = useChatWebSocket({
     runId: jobId!,
     onMessage: (message) => {
       setMessages((prev) => [...prev, message]);
       setPending(false);
     },
     enabled: !!jobId,
   });
   ```

3. **Update send function:**
   ```typescript
   const send = (text?: string) => {
     const content = (text ?? input).trim();
     if (!content || pending) return;

     const userMsg: ChatMessage = {
       role: 'user',
       content,
       time: new Date().toTimeString().slice(0, 8),
     };

     setMessages((m) => [...m, userMsg]);
     setInput('');
     setPending(true);

     // Send via WebSocket
     wsSendMessage(content);
   };
   ```

4. **Remove mock reply logic:** Delete `buildReply` function and `setTimeout` logic

---

## Backend API Endpoints Required

Your FastAPI backend needs to implement these endpoints:

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate` | Start video generation |
| GET | `/api/runs/:runId/status` | Get job status and phases |
| GET | `/api/runs/:runId/output` | Get video output and scenes |
| GET | `/api/runs/:runId/versions` | Get version history |
| POST | `/api/runs/:runId/phases/:phaseId/rerun` | Re-run a specific phase |
| POST | `/api/runs/:runId/chat` | Send chat message (optional if using WS) |

### **WebSocket Endpoints**

| Protocol | Endpoint | Description |
|----------|----------|-------------|
| WS | `/ws/progress/:runId` | Stream logs and phase updates |
| WS | `/ws/chat/:runId` | Bi-directional chat for Edit Agent |

---

## WebSocket Message Formats

### **Progress WebSocket** (`/ws/progress/:runId`)

**Log message:**
```json
{
  "type": "log",
  "payload": {
    "t": "14:22:04.012",
    "lvl": "info",
    "tag": "script",
    "msg": "Pipeline started for run_a7b3f1"
  }
}
```

**Phase update:**
```json
{
  "type": "phase_update",
  "phase_id": "video",
  "status": {
    "status": "running",
    "progress": 64,
    "duration": "2m 14s · eta 1m 22s"
  }
}
```

### **Chat WebSocket** (`/ws/chat/:runId`)

**Client → Server (User message):**
```json
{
  "role": "user",
  "content": "Make scene 1 darker",
  "time": "14:28:14"
}
```

**Server → Client (Agent response):**
```json
{
  "role": "assistant",
  "content": "I'll re-grade scene 1 cooler and drop the exposure ~15%",
  "time": "14:28:15",
  "targets": [{ "type": "Video Frame", "detail": "Scene 1 · color grade" }],
  "plan": [{ "label": "Lower key light", "diff": "-15% exposure" }],
  "confidence": 0.92,
  "eta": "32s",
  "applied": true,
  "resultVersion": "v4"
}
```

---

## Environment Variables

Create `.env` file in `frontend/app/`:

```bash
# API base URL (empty = same origin)
VITE_API_BASE=

# WebSocket base URL
VITE_WS_BASE=ws://localhost:8000
```

For production:
```bash
VITE_API_BASE=https://your-domain.com
VITE_WS_BASE=wss://your-domain.com
```

---

## Testing Without Backend

All screens have **fallback behavior** when backend is unavailable:

- **Home**: Falls back to mock navigation after showing error
- **Pipeline**: Shows mock phase states (already in place)
- **Progress**: Shows mock logs (already in place)
- **Preview**: Shows mock scenes/versions (already in place)
- **EditAgent**: Shows mock chat responses (already in place)

This lets you develop and test the UI independently.

---

## Next Steps

1. ✅ **Home screen is done** — working example to reference
2. **Implement backend endpoints** as documented above
3. **Integrate remaining screens** using the examples above
4. **Test WebSocket connections** with real backend
5. **Remove mock data** once backend is fully integrated

All the infrastructure is in place. Just follow the integration examples for each screen!

---

## Quick Reference

**Files created:**
- `src/services/api.ts` — API service layer
- `src/hooks/useProgressWebSocket.ts` — Progress WebSocket hook
- `src/hooks/useChatWebSocket.ts` — Chat WebSocket hook

**Files updated:**
- `src/pages/Home.tsx` — ✅ Fully integrated with API

**Files ready to integrate:**
- `src/pages/Pipeline.tsx`
- `src/pages/Progress.tsx`
- `src/pages/Preview.tsx`
- `src/pages/EditAgent.tsx`

Each file has clear integration points. The Home screen shows the pattern to follow.
