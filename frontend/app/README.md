# CineAI Frontend Application

Production-ready Vite + React + TypeScript application for CineAI video generation system.

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start dev server with HMR
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

The dev server automatically proxies:
- `/api/*` → `http://localhost:8000`
- `/ws/*` → `ws://localhost:8000`

### Production Build

```bash
# Build for production
npm run build
```

Output goes to `../../dist/` (project root)

### Serve Built App

The built app is served by the FastAPI backend:

```bash
cd ../../backend
python main.py
```

Open [http://localhost:8000](http://localhost:8000)

## Project Structure

```
src/
├── components/
│   └── primitives.tsx       # Shared UI components (Icon, TopNav, StatusChip)
├── pages/
│   ├── Home.tsx             # / - Prompt input & generation
│   ├── Pipeline.tsx         # /pipeline/:jobId - Multi-phase dashboard
│   ├── Progress.tsx         # /progress/:jobId - Live logs
│   ├── Preview.tsx          # /preview/:jobId - Video player
│   └── EditAgent.tsx        # /edit/:jobId - Chat-based editor
├── App.tsx                  # Router configuration
├── main.tsx                 # App entry point
├── styles.css               # Global styles (Ember & Ash theme)
└── types.ts                 # TypeScript type definitions
```

## Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | Home | Prompt input and video generation |
| `/pipeline/:jobId` | Pipeline | 5-phase progress dashboard |
| `/progress/:jobId` | Progress | Vertical stepper + streaming logs |
| `/preview/:jobId` | Preview | Video player with scene markers |
| `/edit/:jobId` | EditAgent | Natural-language chat editor |

## API Integration

Currently uses mock data. Real API integration points are marked with `// TODO(api):` comments:

- **Home**: POST `/api/generate` to start pipeline
- **Pipeline**: GET `/api/runs/:id/status` for phase states
- **Progress**: WebSocket `/ws/progress/:id` for live logs
- **Preview**: GET `/api/runs/:id/output` for video/scenes
- **EditAgent**: WebSocket connection for chat

## Tech Stack

- **Vite 8.0.10** - Build tool & dev server
- **React 18.3.1** - UI framework
- **TypeScript 5.x** - Type safety
- **React Router 6** - Client-side routing

## Scripts

```bash
npm run dev      # Start dev server (port 5173)
npm run build    # Build for production
npm run preview  # Preview production build locally
```

## Design System

**Ember & Ash Color Palette:**
- Primary (orange): `#E8540A`
- Secondary (amber): `#F5A623`
- Background: `#0D0D0D`
- Text: `#F5EFE6`

All styles defined in `src/styles.css` using CSS custom properties.
