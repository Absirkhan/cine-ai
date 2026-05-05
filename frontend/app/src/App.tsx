// CineAI — Main Application with Routing

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import Pipeline from './pages/Pipeline';
import Progress from './pages/Progress';
import Preview from './pages/Preview';
import EditAgent from './pages/EditAgent';
import './styles.css';

function App() {
  return (
    <BrowserRouter>
      <div className="cai" style={{ width: '100vw', height: '100vh', overflow: 'hidden' }}>
        <Routes>
          {/* Phase 0: Compose - Prompt input screen */}
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Navigate to="/" replace />} />

          {/* Phase 1: Pipeline Dashboard - Multi-phase progress overview */}
          <Route path="/pipeline/:jobId" element={<Pipeline />} />
          <Route path="/pipeline" element={<Navigate to="/pipeline/run_a7b3f1" replace />} />

          {/* Phase 2: Live Progress - Vertical stepper + streaming logs */}
          <Route path="/progress/:jobId" element={<Progress />} />
          <Route path="/progress" element={<Navigate to="/progress/run_a7b3f1" replace />} />

          {/* Phase 3: Video Preview - Player with scene markers and version history */}
          <Route path="/preview/:jobId" element={<Preview />} />
          <Route path="/preview" element={<Navigate to="/preview/run_a7b3f1" replace />} />

          {/* Phase 4: Edit Agent - Natural-language chat editor */}
          <Route path="/edit/:jobId" element={<EditAgent />} />
          <Route path="/edit" element={<Navigate to="/edit/run_a7b3f1" replace />} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
