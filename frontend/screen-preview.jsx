// CineAI — Screen 4: Video Preview + Version History

const PreviewScreen = () => {
  const [versions, setVersions] = React.useState([
    { id: 'v4', label: 'v4', note: 'Current · Darker opening shot', time: '4 min ago', author: 'Edit Agent', active: true,
      changes: ['Lower key lighting', 'Scene 1 color grade -15%'] },
    { id: 'v3', label: 'v3', note: 'Swapped narrator voice', time: '12 min ago', author: 'Edit Agent',
      changes: ['Voice: Iris → Theo'] },
    { id: 'v2', label: 'v2', note: 'Re-rendered scene 3', time: '28 min ago', author: 'You',
      changes: ['Crystal glow intensity +40%', 'Added subtle camera dolly'] },
    { id: 'v1', label: 'v1', note: 'Initial render', time: '38 min ago', author: 'Pipeline',
      changes: ['Full generation from prompt'] },
  ]);
  const activeId = versions.find(v => v.active)?.id;
  const [playing, setPlaying] = React.useState(false);
  const [time, setTime] = React.useState(18);
  const [muted, setMuted] = React.useState(false);
  const total = 60;

  React.useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => {
      setTime(x => (x + 0.1 >= total ? (setPlaying(false), total) : x + 0.1));
    }, 100);
    return () => clearInterval(t);
  }, [playing]);

  const activateVersion = (id) => {
    setVersions(vs => vs.map(v => ({ ...v, active: v.id === id })));
  };

  const undoTo = (id) => {
    // Undo = roll the "current" flag back to this version, remove nothing from history
    activateVersion(id);
  };

  const fmt = (s) => {
    const m = Math.floor(s / 60); const sec = Math.floor(s % 60);
    return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
  };

  // Scenes on the timeline
  const scenes = [
    { id: 1, label: 'Opening · Mars plain',    start: 0,  end: 14, color: 'rgba(232,84,10,0.5)' },
    { id: 2, label: 'Discovery · The crystal', start: 14, end: 30, color: 'rgba(245,166,35,0.5)' },
    { id: 3, label: 'Awakening · Light hum',   start: 30, end: 48, color: 'rgba(240,138,75,0.5)' },
    { id: 4, label: 'Outro · Whisper',         start: 48, end: 60, color: 'rgba(217,164,65,0.5)' },
  ];
  const currentScene = scenes.find(s => time >= s.start && time < s.end) || scenes[scenes.length - 1];

  return (
    <>
      <TopNav active="preview" />
      <div className="bg-grid"></div>

      <div style={{
        position: 'relative', zIndex: 2,
        height: 'calc(100% - 57px)',
        display: 'grid',
        gridTemplateColumns: '1fr 360px',
      }}>
        {/* LEFT — player */}
        <div style={{ overflow: 'auto', padding: '24px 28px 32px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-mute)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 4 }}>Final output · <span className="mono">run_a7b3f1</span></div>
              <h1 style={{ fontSize: 22, fontWeight: 600, margin: 0, letterSpacing: '-0.02em' }}>Mars Crystal · {activeId}</h1>
              <div style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 6 }}>
                60s · 16:9 · 1920×1080 · H.264 · 38.2 MB
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="cai-btn"><Icon name="rerun" size={12}/> Re-render</button>
              <button className="cai-btn"><Icon name="wand" size={12}/> Open edit agent</button>
              <button className="cai-btn primary"><Icon name="download" size={12}/> Download MP4</button>
            </div>
          </div>

          {/* Player */}
          <div style={{
            position: 'relative',
            background: '#000',
            borderRadius: 14,
            overflow: 'hidden',
            border: '1px solid var(--line-strong)',
            aspectRatio: '16 / 9',
            maxHeight: 'calc(100% - 240px)',
            boxShadow: '0 20px 60px -20px rgba(0,0,0,0.8)',
          }}>
            {/* Faux frame — gradient + grain */}
            <div style={{
              position: 'absolute', inset: 0,
              background:
                `radial-gradient(ellipse at 30% 40%, rgba(245,166,35,0.4), transparent 50%),
                 radial-gradient(ellipse at 70% 70%, rgba(232,84,10,0.3), transparent 55%),
                 linear-gradient(180deg, #1a0f05 0%, #2d1608 50%, #0d0705 100%)`,
            }}></div>
            {/* Crystal glow */}
            <div style={{
              position: 'absolute', left: '38%', top: '48%',
              width: 120, height: 120, borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(255,230,180,0.95), rgba(245,166,35,0.5) 40%, transparent 70%)',
              filter: 'blur(8px)',
              animation: 'cai-pulse 2.4s ease-in-out infinite',
            }}></div>
            {/* Film grain */}
            <div style={{
              position: 'absolute', inset: 0,
              backgroundImage: 'repeating-radial-gradient(circle at 50% 50%, rgba(245,239,230,0.03) 0 1px, transparent 1px 3px)',
              mixBlendMode: 'overlay',
            }}></div>

            {/* Scene label */}
            <div style={{
              position: 'absolute', top: 14, left: 14,
              padding: '4px 10px',
              background: 'rgba(0,0,0,0.5)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 6,
              fontSize: 11, color: 'var(--text)',
            }} className="mono">
              Scene {currentScene.id} — {currentScene.label}
            </div>

            <div style={{
              position: 'absolute', top: 14, right: 14,
              padding: '4px 10px',
              background: 'rgba(0,0,0,0.5)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 6,
              fontSize: 11, color: 'var(--text-dim)',
            }} className="mono">
              1920×1080 · 24fps
            </div>

            {/* Center play overlay when paused */}
            {!playing && (
              <button
                onClick={() => setPlaying(true)}
                style={{
                  position: 'absolute', inset: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: 'rgba(0,0,0,0.2)',
                  border: 'none', cursor: 'pointer',
                }}>
                <div style={{
                  width: 72, height: 72, borderRadius: '50%',
                  background: 'rgba(255,255,255,0.95)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#000',
                  boxShadow: '0 0 40px rgba(245,166,35,0.5)',
                }}>
                  <Icon name="play" size={28}/>
                </div>
              </button>
            )}

            {/* Bottom controls */}
            <div style={{
              position: 'absolute', left: 0, right: 0, bottom: 0,
              padding: '24px 16px 12px',
              background: 'linear-gradient(180deg, transparent, rgba(0,0,0,0.75))',
            }}>
              {/* Scrubber with scene markers */}
              <div style={{ position: 'relative', height: 10, marginBottom: 8, cursor: 'pointer' }}
                onClick={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  setTime(((e.clientX - rect.left) / rect.width) * total);
                }}>
                <div style={{ position: 'absolute', left: 0, right: 0, top: 4, height: 2, background: 'rgba(255,255,255,0.2)', borderRadius: 2 }}></div>
                {scenes.map(s => (
                  <div key={s.id} style={{
                    position: 'absolute', top: 2,
                    left: `${(s.start / total) * 100}%`,
                    width: `${((s.end - s.start) / total) * 100}%`,
                    height: 6, background: s.color, borderRadius: 2,
                    borderRight: '1px solid rgba(0,0,0,0.5)',
                  }}></div>
                ))}
                <div style={{
                  position: 'absolute', left: 0, top: 4,
                  width: `${(time / total) * 100}%`, height: 2,
                  background: 'linear-gradient(90deg, var(--blue), var(--cyan))',
                  borderRadius: 2,
                }}></div>
                <div style={{
                  position: 'absolute', left: `${(time / total) * 100}%`, top: -1,
                  width: 12, height: 12, borderRadius: '50%',
                  background: '#fff',
                  transform: 'translateX(-50%)',
                  boxShadow: '0 0 12px rgba(245,166,35,0.9)',
                }}></div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <button className="cai-btn icon" onClick={() => setPlaying(p => !p)}
                  style={{ background: 'rgba(255,255,255,0.1)', border: 'none' }}>
                  <Icon name={playing ? 'pause' : 'play'} size={14}/>
                </button>
                <div className="mono" style={{ fontSize: 11.5, color: 'var(--text)' }}>
                  {fmt(time)} / {fmt(total)}
                </div>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
                  <button className="cai-btn icon" onClick={() => setMuted(m => !m)}
                    style={{ background: 'rgba(255,255,255,0.06)', border: 'none' }}>
                    <Icon name={muted ? 'mute' : 'volume'} size={14}/>
                  </button>
                  <button className="cai-btn icon" style={{ background: 'rgba(255,255,255,0.06)', border: 'none' }}>
                    <Icon name="fullscreen" size={14}/>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Scene strip */}
          <div style={{
            marginTop: 14,
            display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8,
          }}>
            {scenes.map(s => {
              const active = currentScene.id === s.id;
              return (
                <div key={s.id} className="cai-card" style={{
                  padding: 8,
                  borderColor: active ? 'rgba(245,166,35,0.45)' : 'var(--line)',
                  background: active ? 'rgba(245,166,35,0.08)' : undefined,
                  cursor: 'pointer',
                }} onClick={() => setTime(s.start + 0.5)}>
                  <div style={{
                    height: 48, borderRadius: 5, marginBottom: 6,
                    background: s.color, position: 'relative',
                  }}>
                    <div style={{ position: 'absolute', top: 3, left: 5, fontSize: 9, color: 'rgba(0,0,0,0.6)' }} className="mono">
                      SC 0{s.id}
                    </div>
                  </div>
                  <div style={{ fontSize: 10.5, color: active ? 'var(--text)' : 'var(--text-dim)', marginBottom: 2, textWrap: 'pretty' }}>
                    {s.label}
                  </div>
                  <div style={{ fontSize: 9.5, color: 'var(--text-mute)' }} className="mono">
                    {fmt(s.start)} – {fmt(s.end)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* RIGHT — version history */}
        <div style={{
          borderLeft: '1px solid var(--line)',
          background: 'rgba(13,13,13,0.65)',
          display: 'flex', flexDirection: 'column', minHeight: 0,
        }}>
          <div style={{
            padding: '14px 18px', borderBottom: '1px solid var(--line)',
            display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <Icon name="layers" size={14}/>
            <div style={{ fontSize: 13, fontWeight: 500 }}>Version history</div>
            <div className="cai-chip" style={{ padding: '2px 8px', fontSize: 10, marginLeft: 'auto' }}>
              {versions.length} versions
            </div>
          </div>

          <div style={{ flex: 1, overflow: 'auto', padding: '4px 0' }}>
            {versions.map((v, i) => (
              <div key={v.id} style={{
                position: 'relative',
                padding: '14px 18px 14px 38px',
                borderLeft: v.active ? '2px solid var(--cyan)' : '2px solid transparent',
                background: v.active ? 'rgba(245,166,35,0.05)' : 'transparent',
              }}>
                {/* Timeline rail */}
                <div style={{
                  position: 'absolute', left: 18, top: 18, bottom: -14,
                  width: 1, background: 'var(--line-strong)',
                  display: i === versions.length - 1 ? 'none' : 'block',
                }}></div>
                <div style={{
                  position: 'absolute', left: 13, top: 18,
                  width: 11, height: 11, borderRadius: '50%',
                  background: v.active ? 'var(--cyan)' : v.author === 'Edit Agent' ? 'var(--violet)' : 'var(--blue-soft)',
                  boxShadow: v.active ? '0 0 12px var(--cyan)' : 'none',
                  border: '2px solid var(--bg-0)',
                  zIndex: 1,
                }}></div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <div className="mono" style={{ fontSize: 12, fontWeight: 600, color: v.active ? 'var(--cyan)' : 'var(--text)' }}>{v.label}</div>
                  {v.active && <div className="cai-chip running" style={{ padding: '1px 7px', fontSize: 9.5 }}>Current</div>}
                  <div style={{ marginLeft: 'auto', fontSize: 10.5, color: 'var(--text-mute)' }}>{v.time}</div>
                </div>
                <div style={{ fontSize: 12.5, color: 'var(--text)', marginBottom: 4, textWrap: 'pretty' }}>{v.note}</div>
                <div style={{ fontSize: 10.5, color: 'var(--text-mute)', marginBottom: 8 }}>
                  by <span style={{ color: v.author === 'Edit Agent' ? 'var(--violet)' : 'var(--text-dim)' }}>{v.author}</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 3, marginBottom: 10 }}>
                  {v.changes.map((c, j) => (
                    <div key={j} style={{ display: 'flex', gap: 6, alignItems: 'center', fontSize: 11, color: 'var(--text-dim)' }}>
                      <div style={{ width: 3, height: 3, borderRadius: 50, background: 'var(--text-mute)' }}></div>
                      {c}
                    </div>
                  ))}
                </div>
                <div style={{ display: 'flex', gap: 6 }}>
                  {!v.active && (
                    <button className="cai-btn sm" onClick={() => undoTo(v.id)}>
                      <Icon name="undo" size={11}/> Undo to here
                    </button>
                  )}
                  {v.active && (
                    <button className="cai-btn sm ghost" disabled style={{ opacity: 0.5, cursor: 'default' }}>
                      <Icon name="dot" size={11}/> You are here
                    </button>
                  )}
                  <button className="cai-btn sm ghost" style={{ padding: '6px 8px' }}>
                    <Icon name="play" size={11}/>
                  </button>
                  <button className="cai-btn sm ghost" style={{ padding: '6px 8px' }}>
                    <Icon name="download" size={11}/>
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div style={{ padding: 14, borderTop: '1px solid var(--line)' }}>
            <button className="cai-btn" style={{ width: '100%', justifyContent: 'center' }}>
              <Icon name="plus" size={12}/> Create branch from {activeId}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

Object.assign(window, { PreviewScreen });
