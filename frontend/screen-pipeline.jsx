// CineAI — Screen 2: Pipeline Dashboard

const PipelineScreen = () => {
  // Demo state: script complete, audio complete, video running, web pending, edit pending
  const [phaseStates, setPhaseStates] = React.useState({
    script: { status: 'complete', progress: 100, duration: '42s', substeps: ['Scene graph', 'Dialogue', 'Shotlist'] },
    audio: { status: 'complete', progress: 100, duration: '1m 08s', substeps: ['Voice casting', 'Narration', 'SFX', 'Score'] },
    video: { status: 'running', progress: 64, duration: '2m 14s · eta 1m 22s', substeps: ['Storyboard', 'Keyframes', 'Interpolation', 'Compositing'] },
    web: { status: 'pending', progress: 0, duration: '—', substeps: ['Player config', 'Captions', 'Share links'] },
    edit: { status: 'pending', progress: 0, duration: '—', substeps: ['Intent parser', 'Patch planner'] },
  });

  // Slowly tick the running phase
  React.useEffect(() => {
    const t = setInterval(() => {
      setPhaseStates(prev => {
        const next = { ...prev };
        if (next.video.status === 'running' && next.video.progress < 92) {
          next.video = { ...next.video, progress: next.video.progress + 0.5 };
        }
        return next;
      });
    }, 400);
    return () => clearInterval(t);
  }, []);

  const handleRerun = (id) => {
    setPhaseStates(prev => ({
      ...prev,
      [id]: { ...prev[id], status: 'running', progress: 5 },
    }));
  };

  const overall = Math.round(
    Object.values(phaseStates).reduce((s, p) => s + p.progress, 0) / PHASES.length
  );

  return (
    <>
      <TopNav active="pipeline" />
      <div className="bg-grid"></div>

      <div style={{
        position: 'relative', zIndex: 2,
        height: 'calc(100% - 57px)',
        overflow: 'auto',
        padding: '28px 32px 48px',
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, marginBottom: 24 }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6,
              fontSize: 11, color: 'var(--text-mute)', letterSpacing: '0.08em',
              textTransform: 'uppercase',
            }}>
              <span className="mono">run_a7b3f1</span>
              <span>·</span>
              <span>started 3 min ago</span>
              <span>·</span>
              <span style={{ color: 'var(--cyan)' }}>Claude Sonnet 4.5 · Veo 3</span>
            </div>
            <h1 style={{ fontSize: 24, fontWeight: 600, margin: 0, letterSpacing: '-0.02em' }}>
              "A lonely astronaut discovers a glowing crystal on Mars…"
            </h1>
            <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
              <div className="cai-chip">Sci-Fi</div>
              <div className="cai-chip">Cinematic</div>
              <div className="cai-chip">60s</div>
              <div className="cai-chip">16:9</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="cai-btn"><Icon name="stop" size={12}/> Stop</button>
            <button className="cai-btn"><Icon name="rerun" size={13}/> Re-run all</button>
            <button className="cai-btn primary"><Icon name="play" size={12}/> Continue</button>
          </div>
        </div>

        {/* Overall meter */}
        <div className="cai-card" style={{ padding: '14px 18px', marginBottom: 22, display: 'flex', alignItems: 'center', gap: 18 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <div style={{ fontSize: 12, fontWeight: 500 }}>Pipeline progress</div>
              <div style={{ fontSize: 12, color: 'var(--text-dim)' }} className="mono">
                {overall}% · 3 of 5 phases complete · ETA 2m 18s
              </div>
            </div>
            <div className="cai-progress" style={{ height: 5 }}>
              <div className="cai-progress-fill running" style={{ width: `${overall}%` }}></div>
            </div>
          </div>
        </div>

        {/* Phases — horizontal pipeline with connectors */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(5, 1fr)',
          gap: 0,
          marginBottom: 28,
        }}>
          {PHASES.map((phase, i) => {
            const state = phaseStates[phase.id];
            return (
              <React.Fragment key={phase.id}>
                <PhaseCard phase={phase} state={state} index={i} onRerun={handleRerun}/>
                {i < PHASES.length - 1 && (
                  <Connector
                    active={state.status === 'complete'}
                    running={phaseStates[PHASES[i+1].id].status === 'running'}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Artifacts output row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 16 }}>
          <div className="cai-card" style={{ padding: 18 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500 }}>Phase artifacts</div>
                <div style={{ fontSize: 11.5, color: 'var(--text-mute)', marginTop: 2 }}>
                  Outputs from completed phases. Click to inspect.
                </div>
              </div>
              <button className="cai-btn sm ghost"><Icon name="download" size={12}/> Export all</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {[
                { icon: 'script', name: 'script_v3.md', meta: '4 scenes · 142 lines', size: '8.2 KB' },
                { icon: 'audio', name: 'narration_en.wav', meta: 'Voice: Iris (calm)', size: '1.4 MB' },
                { icon: 'audio', name: 'score_main.mp3', meta: 'Ambient · 60s · 120 BPM', size: '982 KB' },
                { icon: 'video', name: 'comp_preview.mp4', meta: 'Rendering frame 384 / 1440', size: '—', running: true },
              ].map((a, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '9px 10px', borderRadius: 8,
                  background: 'rgba(245,239,230,0.02)',
                  border: '1px solid var(--line)',
                }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: 6,
                    background: 'rgba(232,84,10,0.12)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: a.running ? 'var(--cyan)' : 'var(--blue-soft)',
                  }}>
                    <Icon name={a.icon} size={14}/>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="mono" style={{ fontSize: 12, fontWeight: 500 }}>{a.name}</div>
                    <div style={{ fontSize: 10.5, color: 'var(--text-mute)' }}>{a.meta}</div>
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-dim)' }} className="mono">{a.size}</div>
                  {a.running ? (
                    <div className="cai-chip running" style={{ padding: '2px 8px', fontSize: 10 }}>
                      <span className="dot"></span>Writing
                    </div>
                  ) : (
                    <button className="cai-btn sm ghost" style={{ padding: 5 }}>
                      <Icon name="download" size={12}/>
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="cai-card" style={{ padding: 18 }}>
            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Resource usage</div>
            <div style={{ fontSize: 11.5, color: 'var(--text-mute)', marginBottom: 16 }}>Live telemetry across this run</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <Meter label="GPU utilization" value={78} unit="%" color="cyan"/>
              <Meter label="Tokens used" value={24900} max={100000} unit="" color="blue" format="k"/>
              <Meter label="Render queue" value={3} max={8} unit="jobs" color="violet"/>
              <Meter label="Storage" value={412} max={1024} unit="MB" color="cyan"/>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

const PhaseCard = ({ phase, state, index, onRerun }) => {
  const isRunning = state.status === 'running';
  return (
    <div className="cai-card" style={{
      padding: 16,
      borderColor: isRunning ? 'rgba(245,166,35,0.4)' : 'var(--line)',
      boxShadow: isRunning ? '0 0 40px -10px rgba(245,166,35,0.3)' : 'none',
      background: isRunning
        ? 'linear-gradient(180deg, rgba(245,166,35,0.06), rgba(23,20,18,0.6))'
        : undefined,
      position: 'relative',
    }}>
      <div style={{
        position: 'absolute', top: 10, right: 12,
        fontSize: 10, color: 'var(--text-mute)',
        letterSpacing: '0.1em',
      }} className="mono">
        0{index + 1}
      </div>

      <div className={`cai-phase-icon ${state.status}`} style={{ marginBottom: 12 }}>
        <Icon name={phase.icon} size={18}/>
      </div>

      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 3 }}>{phase.title}</div>
      <div style={{ fontSize: 11.5, color: 'var(--text-mute)', marginBottom: 12, lineHeight: 1.4 }}>
        {phase.subtitle}
      </div>

      <StatusChip status={state.status}/>

      <div style={{ marginTop: 14 }}>
        <div className="cai-progress">
          <div className={`cai-progress-fill ${isRunning ? 'running' : ''}`}
            style={{
              width: `${state.progress}%`,
              background: state.status === 'complete' ? 'var(--green)' : undefined,
            }}></div>
        </div>
        <div style={{
          marginTop: 7, display: 'flex', justifyContent: 'space-between',
          fontSize: 10.5, color: 'var(--text-mute)',
        }} className="mono">
          <span>{Math.round(state.progress)}%</span>
          <span>{state.duration}</span>
        </div>
      </div>

      {/* Substeps */}
      <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 4 }}>
        {state.substeps.map((s, i) => {
          const stepPct = (i + 1) / state.substeps.length;
          const doneAtThis = state.progress / 100 >= stepPct;
          const currentAtThis = !doneAtThis && state.status === 'running' && state.progress / 100 > i / state.substeps.length;
          return (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 7,
              fontSize: 11,
              color: doneAtThis ? 'var(--text-dim)' : currentAtThis ? 'var(--cyan)' : 'var(--text-mute)',
            }}>
              {doneAtThis ? (
                <div style={{ width: 11, height: 11, borderRadius: 3, background: 'var(--green)', opacity: 0.8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1A0F05' }}>
                  <Icon name="check" size={8} stroke={3}/>
                </div>
              ) : currentAtThis ? (
                <div style={{ width: 11, height: 11, borderRadius: 3, border: '1.5px solid var(--cyan)' }}>
                  <div style={{ width: '100%', height: '100%', borderRadius: 2, background: 'var(--cyan)', opacity: 0.4, animation: 'cai-pulse 1.4s ease-in-out infinite' }}></div>
                </div>
              ) : (
                <div style={{ width: 11, height: 11, borderRadius: 3, border: '1.5px solid var(--line-strong)' }}></div>
              )}
              {s}
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: 14, display: 'flex', gap: 6 }}>
        <button className="cai-btn sm" style={{ flex: 1, justifyContent: 'center' }} onClick={() => onRerun(phase.id)}>
          <Icon name="rerun" size={11}/> Re-run
        </button>
        <button className="cai-btn sm ghost" style={{ padding: '6px 9px' }}>
          <Icon name="settings" size={12}/>
        </button>
      </div>
    </div>
  );
};

const Connector = ({ active, running }) => (
  <div style={{
    alignSelf: 'center',
    height: 2, margin: '0 -4px',
    background: active ? 'linear-gradient(90deg, var(--green), var(--cyan))' : 'var(--line-strong)',
    position: 'relative',
    zIndex: 2,
  }}>
    {running && (
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(90deg, transparent, var(--cyan), transparent)',
        backgroundSize: '200% 100%',
        animation: 'cai-shimmer 1.4s linear infinite',
      }}></div>
    )}
  </div>
);

const Meter = ({ label, value, max = 100, unit, color = 'cyan', format }) => {
  const pct = (value / max) * 100;
  const display = format === 'k' ? `${(value / 1000).toFixed(1)}k` : value.toLocaleString();
  const colorVar = color === 'cyan' ? 'var(--cyan)' : color === 'blue' ? 'var(--blue-soft)' : 'var(--violet)';
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <div style={{ fontSize: 11.5, color: 'var(--text-dim)' }}>{label}</div>
        <div style={{ fontSize: 11.5, color: 'var(--text)' }} className="mono">
          {display}<span style={{ color: 'var(--text-mute)' }}> {unit}</span>
          {max !== 100 && format !== 'k' && <span style={{ color: 'var(--text-mute)' }}> / {max}</span>}
          {format === 'k' && <span style={{ color: 'var(--text-mute)' }}> / {(max/1000).toFixed(0)}k</span>}
        </div>
      </div>
      <div className="cai-progress">
        <div style={{
          height: '100%', width: `${Math.min(pct, 100)}%`,
          background: colorVar,
          borderRadius: 999,
          boxShadow: `0 0 12px ${colorVar}`,
          opacity: 0.85,
        }}></div>
      </div>
    </div>
  );
};

Object.assign(window, { PipelineScreen });
