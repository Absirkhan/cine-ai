// CineAI — Screen 3: Real-time progress (vertical stepper + logs)

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Icon, TopNav, PHASES, StatusChip } from '../components/primitives';
import type { PhaseState, LogEntry } from '../types';
import { useProgressWebSocket } from '../hooks/useProgressWebSocket';

const Progress: React.FC = () => {
  const params = useParams<{ jobId: string }>();
  const jobId = params.jobId;
  const navigate = useNavigate();
  console.log('Job ID:', jobId);

  const [phaseStates, setPhaseStates] = useState<Record<string, PhaseState>>({
    script: { status: 'pending', progress: 0, start: '—', end: '—', lines: [] },
    audio: { status: 'pending', progress: 0, start: '—', end: '—', lines: [] },
    video: { status: 'pending', progress: 0, start: '—', end: '—', lines: [] },
    web: { status: 'pending', progress: 0, start: '—', end: '—', lines: [] },
    edit: { status: 'pending', progress: 0, start: '—', end: '—', lines: [] },
  });

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [autoscroll, setAutoscroll] = useState<boolean>(true);
  const logRef = useRef<HTMLDivElement>(null);

  // Connect to WebSocket for real-time logs and phase updates
  const { connected } = useProgressWebSocket({
    runId: jobId!,
    onLog: (log) => {
      setLogs((prev) => [...prev, log].slice(-60)); // Keep last 60 logs
    },
    onPhaseUpdate: (phaseId, status) => {
      setPhaseStates((prev) => ({
        ...prev,
        [phaseId]: status,
      }));

      // Auto-navigate to preview when pipeline completes
      if (phaseId === 'completed' || (phaseId === 'video' && status.status === 'complete')) {
        // Check if all phases are complete
        setTimeout(() => {
          const allComplete = Object.values(phaseStates).every(
            (phase) => phase.status === 'complete'
          );
          if (allComplete || phaseId === 'completed') {
            console.log('Pipeline completed! Navigating to preview...');
            navigate(`/preview/${jobId}`);
          }
        }, 2000); // Wait 2 seconds before navigating
      }
    },
    enabled: !!jobId,
  });

  // Fallback to mock logs if WebSocket is not connected
  useEffect(() => {
    if (connected || !jobId) return;

    // Use mock data if WebSocket fails to connect
    const initialLogs: LogEntry[] = [
      { t: '14:22:04.012', lvl: 'info', tag: 'script', msg: 'Pipeline started (demo mode - WebSocket not connected)' },
      { t: '14:22:04.118', lvl: 'info', tag: 'script', msg: 'Dispatching to story_agent (claude-sonnet-4.5)' },
      { t: '14:22:18.407', lvl: 'debug', tag: 'script', msg: 'Scene graph: [intro, discovery, awakening, outro]' },
    ];

    setLogs(initialLogs);
    setPhaseStates({
      script: { status: 'complete', progress: 100, start: '14:22:04', end: '14:22:46', lines: ['LLM call → claude-sonnet-4.5', 'Parsed 4 scenes, 12 beats', 'Dialogue generated (142 lines)', 'Shotlist written'] },
      audio: { status: 'complete', progress: 100, start: '14:22:46', end: '14:23:54', lines: ['Voice match: Iris (f, calm, warm)', 'Narration rendered in 11 takes', '4 SFX stems mixed', 'Score composed (60s, Am→C)'] },
      video: { status: 'running', progress: 64, start: '14:23:54', end: '…', lines: ['Storyboard → 24 keyframes', 'Keyframe gen: 18/24', 'Interpolation: 384/1440 frames', 'Compositing layer 2 of 5'] },
      web: { status: 'pending', progress: 0, start: '—', end: '—', lines: [] },
      edit: { status: 'pending', progress: 0, start: '—', end: '—', lines: [] },
    });

    // Mock log generation
    const messages: Omit<LogEntry, 't'>[] = [
      { lvl: 'debug', tag: 'video', msg: 'Frame 412 ✓ · 1.82s' },
      { lvl: 'info',  tag: 'video', msg: 'Interpolation engine: frame 445 / 1440' },
      { lvl: 'debug', tag: 'video', msg: 'GPU 0: 81% util · temp 72°C' },
    ];
    let i = 0;
    const t = setInterval(() => {
      const m = messages[i % messages.length];
      const stamp = `${String(14).padStart(2,'0')}:${String(25 + Math.floor(i/6)).padStart(2,'0')}:${String((i * 7) % 60).padStart(2,'0')}.${String((i * 113) % 1000).padStart(3,'0')}`;
      setLogs(prev => [...prev, { t: stamp, ...m }].slice(-60));
      i++;
    }, 900);
    return () => clearInterval(t);
  }, [connected, jobId]);

  useEffect(() => {
    if (autoscroll && logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs, autoscroll]);

  const filtered = filter === 'all' ? logs : logs.filter(l => l.tag === filter);

  return (
    <>
      <TopNav active="progress" onNav={(id) => {
        if (id === 'home') {
          navigate('/');
        } else if (jobId) {
          navigate(`/${id}/${jobId}`);
        } else {
          navigate(`/${id}`);
        }
      }} />
      <div className="bg-grid"></div>

      <div style={{
        position: 'relative', zIndex: 2,
        height: 'calc(100% - 57px)',
        display: 'grid',
        gridTemplateColumns: '1fr 480px',
      }}>
        {/* LEFT — vertical stepper */}
        <div style={{ overflow: 'auto', padding: '28px 32px 48px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 24 }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-mute)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 4 }}>Live run · <span className="mono">{jobId}</span></div>
              <h1 style={{ fontSize: 22, fontWeight: 600, margin: 0, letterSpacing: '-0.02em' }}>Rendering Video</h1>
              <div style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 6 }}>
                {connected ? 'Connected to backend' : 'Using demo mode'}
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              {/* Show "View Preview" button when video phase completes */}
              {phaseStates.video?.status === 'complete' && (
                <button className="cai-btn primary" onClick={() => navigate(`/preview/${jobId}`)}>
                  <Icon name="play" size={12}/> View Preview
                </button>
              )}
              <button className="cai-btn"><Icon name="pause" size={12}/> Pause</button>
              <button className="cai-btn"><Icon name="stop" size={12}/> Cancel</button>
            </div>
          </div>

          {/* Stepper */}
          <div style={{ position: 'relative' }}>
            {PHASES.map((phase, i) => {
              const state = phaseStates[phase.id];
              const isLast = i === PHASES.length - 1;
              return (
                <StepItem key={phase.id}
                  phase={phase} state={state}
                  isLast={isLast}
                  index={i}/>
              );
            })}
          </div>
        </div>

        {/* RIGHT — logs panel */}
        <div style={{
          borderLeft: '1px solid var(--line)',
          background: 'rgba(13,13,13,0.65)',
          display: 'flex', flexDirection: 'column',
          minHeight: 0,
        }}>
          <div style={{
            padding: '14px 18px', borderBottom: '1px solid var(--line)',
            display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Icon name="code" size={14}/>
              <div style={{ fontSize: 13, fontWeight: 500 }}>Live logs</div>
              <div className="cai-chip running" style={{ padding: '2px 8px', fontSize: 10 }}>
                <span className="dot"></span>Streaming
              </div>
            </div>
            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
              <button className="cai-btn sm ghost" style={{ padding: '5px 8px' }}>
                <Icon name="search" size={12}/>
              </button>
              <button className="cai-btn sm ghost" style={{ padding: '5px 8px' }}>
                <Icon name="pin" size={12}/>
              </button>
            </div>
          </div>

          <div style={{
            padding: '8px 12px', borderBottom: '1px solid var(--line)',
            display: 'flex', alignItems: 'center', gap: 6,
          }}>
            <div className="cai-seg" style={{ padding: 2 }}>
              {['all', ...PHASES.map(p => p.id)].map(k => (
                <button key={k}
                  className={filter === k ? 'active' : ''}
                  style={{ fontSize: 11, padding: '4px 8px' }}
                  onClick={() => setFilter(k)}>
                  {k}
                </button>
              ))}
            </div>
            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text-dim)' }}>
              <input type="checkbox" checked={autoscroll} onChange={e => setAutoscroll(e.target.checked)}
                style={{ accentColor: 'var(--blue)' }}/>
              Auto-scroll
            </div>
          </div>

          <div ref={logRef} style={{
            flex: 1, overflow: 'auto', padding: '10px 14px',
            fontFamily: 'JetBrains Mono, monospace', fontSize: 11.5,
            lineHeight: 1.6, minHeight: 0,
          }}>
            {filtered.map((l, i) => (
              <div key={i} style={{ display: 'flex', gap: 10, padding: '2px 0', wordBreak: 'break-word' }}>
                <span style={{ color: 'var(--text-mute)', flexShrink: 0 }}>{l.t}</span>
                <span style={{
                  flexShrink: 0, fontSize: 10, padding: '0 6px', borderRadius: 3,
                  lineHeight: '16px', marginTop: 1,
                  color: l.lvl === 'ok' ? 'var(--green)' :
                         l.lvl === 'warn' ? 'var(--amber)' :
                         l.lvl === 'error' ? 'var(--red)' :
                         l.lvl === 'debug' ? 'var(--text-mute)' : 'var(--blue-soft)',
                  background: 'rgba(245,239,230,0.05)',
                  textTransform: 'uppercase',
                }}>{l.lvl}</span>
                <span style={{ color: 'var(--violet)', flexShrink: 0 }}>[{l.tag}]</span>
                <span style={{ color: l.lvl === 'ok' ? 'var(--green)' : 'var(--text)' }}>{l.msg}</span>
              </div>
            ))}
            <div style={{ display: 'flex', gap: 10, padding: '2px 0', color: 'var(--cyan)' }}>
              <span style={{ color: 'var(--text-mute)' }}>{new Date().toTimeString().slice(0,8)}.{String(Date.now() % 1000).padStart(3,'0')}</span>
              <span style={{ marginLeft: 2 }}>▍</span>
            </div>
          </div>

          <div style={{
            padding: '10px 14px',
            borderTop: '1px solid var(--line)',
            display: 'flex', gap: 10,
            fontSize: 11, color: 'var(--text-dim)',
          }}>
            <span className="mono">{filtered.length} lines</span>
            <span>·</span>
            <span className="mono">0 errors</span>
            <span>·</span>
            <span className="mono" style={{ color: 'var(--amber)' }}>1 warning</span>
            <span style={{ marginLeft: 'auto' }} className="mono">stream: stable</span>
          </div>
        </div>
      </div>
    </>
  );
};

interface StepItemProps {
  phase: { id: string; title: string; subtitle: string; icon: string };
  state: PhaseState;
  isLast: boolean;
  index: number;
}

const StepItem: React.FC<StepItemProps> = ({ phase, state, isLast, index }) => {
  const running = state.status === 'running';
  const complete = state.status === 'complete';
  return (
    <div style={{ display: 'flex', gap: 16, position: 'relative' }}>
      {/* Rail */}
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        flexShrink: 0,
      }}>
        <div className={`cai-phase-icon ${state.status}`} style={{ width: 44, height: 44, zIndex: 2 }}>
          {complete ? <Icon name="check" size={20} stroke={2.5}/> : <Icon name={phase.icon} size={18}/>}
          {running && (
            <div style={{
              position: 'absolute', inset: -6, borderRadius: 14,
              border: '1.5px solid var(--cyan)',
              animation: 'cai-pulse 1.8s ease-in-out infinite',
              opacity: 0.6,
            }}></div>
          )}
        </div>
        {!isLast && (
          <div style={{
            width: 2, flex: 1, minHeight: 28,
            background: complete ? 'linear-gradient(180deg, var(--green), var(--cyan))' : 'var(--line-strong)',
            marginTop: 4, marginBottom: 4,
          }}></div>
        )}
      </div>

      {/* Body */}
      <div style={{ flex: 1, paddingBottom: isLast ? 0 : 28, minWidth: 0 }}>
        <div className="cai-card" style={{
          padding: 14,
          borderColor: running ? 'rgba(245,166,35,0.4)' : 'var(--line)',
          boxShadow: running ? '0 0 30px -10px rgba(245,166,35,0.3)' : 'none',
          background: running ? 'linear-gradient(180deg, rgba(245,166,35,0.05), rgba(23,20,18,0.6))' : undefined,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ fontSize: 10.5, color: 'var(--text-mute)', letterSpacing: '0.08em' }} className="mono">
              PHASE 0{index+1}
            </div>
            <div style={{ fontSize: 14, fontWeight: 600 }}>{phase.title}</div>
            <div style={{ marginLeft: 'auto' }}><StatusChip status={state.status}/></div>
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--text-mute)', marginTop: 4 }}>
            {phase.subtitle}
          </div>

          {state.status !== 'pending' && (
            <div style={{ marginTop: 12 }}>
              <div className="cai-progress">
                <div className={`cai-progress-fill ${running ? 'running' : ''}`}
                  style={{
                    width: `${state.progress}%`,
                    background: complete ? 'var(--green)' : undefined,
                  }}></div>
              </div>
              <div style={{ marginTop: 8, display: 'flex', gap: 16, fontSize: 10.5, color: 'var(--text-mute)' }} className="mono">
                <span>start {state.start}</span>
                <span>end {state.end}</span>
                <span style={{ marginLeft: 'auto' }}>{Math.round(state.progress)}%</span>
              </div>
            </div>
          )}

          {state.lines && state.lines.length > 0 && (
            <div style={{
              marginTop: 12, paddingTop: 12,
              borderTop: '1px solid var(--line)',
              display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '4px 16px',
            }}>
              {state.lines.map((line, i) => (
                <div key={i} style={{ display: 'flex', gap: 7, alignItems: 'center', fontSize: 11.5, color: 'var(--text-dim)' }}>
                  <div style={{
                    width: 4, height: 4, borderRadius: 50,
                    background: running && i === state.lines!.length - 1 ? 'var(--cyan)' : 'var(--text-mute)',
                    boxShadow: running && i === state.lines!.length - 1 ? '0 0 8px var(--cyan)' : 'none',
                  }}></div>
                  {line}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Progress;
