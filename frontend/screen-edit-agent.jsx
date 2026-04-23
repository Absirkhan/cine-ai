// CineAI — Screen 5: Edit Agent chat panel

const EditAgentScreen = () => {
  const [messages, setMessages] = React.useState([
    {
      role: 'system',
      content: 'Edit Agent is watching Mars Crystal v4. I can adjust script, audio, video frames, or pacing — just describe the change.',
      time: '14:28:02',
    },
    {
      role: 'user',
      content: 'Make scene 1 feel more tense — maybe darker lighting and slower pacing.',
      time: '14:28:14',
    },
    {
      role: 'assistant',
      time: '14:28:15',
      thinking: 'Parsing intent… target locked.',
      targets: [
        { type: 'Video Frame', detail: 'Scene 1 · color grade' },
        { type: 'Video Frame', detail: 'Scene 1 · timing' },
      ],
      plan: [
        { label: 'Lower key light, shift to cool blue-black', diff: '-15% exposure, -12 temp' },
        { label: 'Slow scene 1 playback', diff: '1.00x → 0.85x' },
      ],
      content: 'I\'ll re-grade scene 1 cooler and drop the exposure ~15%, then stretch playback to 0.85× to let the tension breathe. No audio changes needed.',
      confidence: 0.92,
      eta: '32s',
      applied: true,
      resultVersion: 'v4',
    },
    {
      role: 'user',
      content: 'Change the narrator\'s voice to something deeper and more serious.',
      time: '14:30:41',
    },
  ]);

  const [input, setInput] = React.useState('');
  const [detected, setDetected] = React.useState({ type: null, detail: null });
  const [pending, setPending] = React.useState(false);
  const listRef = React.useRef(null);

  // Live target detection from the draft
  React.useEffect(() => {
    setDetected(detectTarget(input));
  }, [input]);

  React.useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages]);

  const suggestions = [
    'Make scene 3 brighter and add soft rain',
    'Change voice tone to warmer',
    'Shorten the outro by 4 seconds',
    'Swap the score to something minor-key',
  ];

  const send = (text) => {
    const t = (text ?? input).trim();
    if (!t || pending) return;
    const now = new Date().toTimeString().slice(0,8);
    const userMsg = { role: 'user', content: t, time: now };
    const target = detectTarget(t);
    setMessages(m => [...m, userMsg]);
    setInput('');
    setPending(true);

    // Fake agent reply
    setTimeout(() => {
      const reply = buildReply(t, target);
      setMessages(m => [...m, { ...reply, time: new Date().toTimeString().slice(0,8) }]);
      setPending(false);
    }, 1100);
  };

  return (
    <>
      <TopNav active="edit" />
      <div className="bg-grid"></div>

      <div style={{
        position: 'relative', zIndex: 2,
        height: 'calc(100% - 57px)',
        display: 'grid',
        gridTemplateColumns: '320px 1fr',
      }}>
        {/* LEFT — context pane */}
        <div style={{
          borderRight: '1px solid var(--line)',
          background: 'rgba(13,13,13,0.65)',
          padding: 18, overflow: 'auto',
        }}>
          <div style={{ fontSize: 11, color: 'var(--text-mute)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 8 }}>Editing</div>

          {/* Current video card */}
          <div className="cai-card" style={{ padding: 10, marginBottom: 18 }}>
            <div style={{
              aspectRatio: '16/9', borderRadius: 7, marginBottom: 10,
              background:
                `radial-gradient(ellipse at 35% 45%, rgba(245,166,35,0.35), transparent 55%),
                 linear-gradient(180deg, #1a0f05 0%, #2d1608 100%)`,
              position: 'relative', overflow: 'hidden',
            }}>
              <div style={{
                position: 'absolute', left: '40%', top: '50%',
                width: 42, height: 42, borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(255,230,180,0.85), rgba(245,166,35,0.4) 50%, transparent 70%)',
                filter: 'blur(4px)', animation: 'cai-pulse 2.4s ease-in-out infinite',
              }}></div>
            </div>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>Mars Crystal</div>
            <div style={{ fontSize: 11, color: 'var(--text-mute)', marginBottom: 8 }} className="mono">v4 · 60s · 16:9</div>
            <div style={{ display: 'flex', gap: 6 }}>
              <button className="cai-btn sm" style={{ flex: 1, justifyContent: 'center' }}>
                <Icon name="play" size={11}/> Preview
              </button>
              <button className="cai-btn sm ghost" style={{ padding: '6px 8px' }}>
                <Icon name="layers" size={11}/>
              </button>
            </div>
          </div>

          {/* Targetable surfaces */}
          <div style={{ fontSize: 11, color: 'var(--text-mute)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 10 }}>
            Editable surfaces
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 20 }}>
            {[
              { type: 'Script',      icon: 'script', detail: '4 scenes · 142 lines' },
              { type: 'Audio',       icon: 'audio',  detail: 'narration + score + 4 SFX' },
              { type: 'Video Frame', icon: 'video',  detail: '1440 frames · 24fps' },
              { type: 'Pacing',      icon: 'clock',  detail: '60s runtime' },
            ].map(s => (
              <div key={s.type} style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '8px 10px', borderRadius: 7,
                border: '1px solid var(--line)',
                background: 'rgba(245,239,230,0.02)',
              }}>
                <div style={{
                  width: 26, height: 26, borderRadius: 6,
                  background: 'rgba(232,84,10,0.12)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--blue-soft)',
                }}>
                  <Icon name={s.icon} size={13}/>
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12, fontWeight: 500 }}>{s.type}</div>
                  <div style={{ fontSize: 10.5, color: 'var(--text-mute)' }}>{s.detail}</div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ fontSize: 11, color: 'var(--text-mute)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 10 }}>
            Recent edits
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5, fontSize: 11.5, color: 'var(--text-dim)' }}>
            <div style={{ padding: 6 }}>› Darker opening shot <span style={{ color: 'var(--text-mute)' }}>4m</span></div>
            <div style={{ padding: 6 }}>› Voice: Iris → Theo <span style={{ color: 'var(--text-mute)' }}>12m</span></div>
            <div style={{ padding: 6 }}>› Crystal glow +40% <span style={{ color: 'var(--text-mute)' }}>28m</span></div>
          </div>
        </div>

        {/* RIGHT — chat */}
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{
            padding: '14px 22px', borderBottom: '1px solid var(--line)',
            display: 'flex', alignItems: 'center', gap: 12,
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8,
              background: 'linear-gradient(135deg, rgba(240,138,75,0.3), rgba(245,166,35,0.18))',
              border: '1px solid rgba(240,138,75,0.4)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--violet)',
            }}>
              <Icon name="wand" size={16}/>
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>Edit Agent</div>
              <div style={{ fontSize: 11, color: 'var(--text-mute)' }}>Natural-language revisions · auto-routed</div>
            </div>
            <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
              <div className="cai-chip running" style={{ padding: '3px 9px' }}>
                <span className="dot"></span>Online
              </div>
              <button className="cai-btn sm ghost"><Icon name="settings" size={12}/></button>
            </div>
          </div>

          <div ref={listRef} style={{ flex: 1, overflow: 'auto', padding: '20px 22px', minHeight: 0 }}>
            {messages.map((m, i) => <Message key={i} m={m}/>)}
            {pending && (
              <div style={{ display: 'flex', gap: 10, marginBottom: 16, alignItems: 'flex-start' }}>
                <AgentAvatar/>
                <div className="cai-card" style={{ padding: '10px 14px', background: 'rgba(240,138,75,0.05)', borderColor: 'rgba(240,138,75,0.25)' }}>
                  <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
                    <div className="mono" style={{ fontSize: 11, color: 'var(--violet)' }}>Thinking</div>
                    <Dots/>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Suggestions row */}
          {messages.length < 6 && !pending && (
            <div style={{ padding: '0 22px 10px', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {suggestions.map((s, i) => (
                <button key={i} className="cai-btn sm" style={{ fontWeight: 400, color: 'var(--text-dim)' }}
                  onClick={() => setInput(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Composer */}
          <div style={{ padding: '12px 22px 18px', borderTop: '1px solid var(--line)', background: 'rgba(13,13,13,0.55)' }}>
            <div style={{
              border: '1px solid var(--line-strong)',
              borderRadius: 12,
              padding: 10,
              background: 'rgba(245,239,230,0.02)',
              transition: 'border-color 0.15s',
            }}>
              <textarea
                className="cai-textarea"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
                placeholder="Describe an edit — e.g. make the scene darker, change voice tone…"
                style={{
                  border: 'none', background: 'transparent', padding: '4px 6px',
                  fontSize: 13.5, minHeight: 44, resize: 'none', boxShadow: 'none',
                }}
              />

              <div style={{ display: 'flex', alignItems: 'center', gap: 10, paddingTop: 6 }}>
                {detected.type ? (
                  <DetectedTargetChip target={detected}/>
                ) : (
                  <div style={{ fontSize: 11, color: 'var(--text-mute)' }}>
                    Target will be detected as you type
                  </div>
                )}
                <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ fontSize: 10.5, color: 'var(--text-mute)' }} className="mono">↵ send · ⇧↵ newline</div>
                  <button className="cai-btn primary" onClick={() => send()}
                    disabled={!input.trim() || pending}
                    style={{ padding: '7px 12px', opacity: (!input.trim() || pending) ? 0.5 : 1 }}>
                    <Icon name="send" size={12}/> Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

// --- helpers ---
function detectTarget(text) {
  const t = text.toLowerCase();
  if (!t.trim()) return { type: null };
  const hits = [];
  if (/voice|narrat|tone|tts|speak|accent|louder|quieter|music|score|sound|sfx|audio|quiet|noise/.test(t)) hits.push({ type: 'Audio', detail: inferAudioDetail(t) });
  if (/script|line|dialogue|word|say|caption|subtitle|text/.test(t)) hits.push({ type: 'Script', detail: 'dialogue' });
  if (/dark|bright|color|light|scene|shot|camera|frame|visual|render|rain|snow|fog|grade|contrast/.test(t)) hits.push({ type: 'Video Frame', detail: inferSceneDetail(t) });
  if (/pace|speed|slow|fast|shorten|lengthen|cut|extend|duration|second/.test(t)) hits.push({ type: 'Pacing', detail: 'runtime' });
  if (hits.length === 0) return { type: 'Script', detail: 'general' };
  return hits[0]; // primary
}
function inferSceneDetail(t) {
  const m = t.match(/scene\s*(\d+)/);
  if (m) return `Scene ${m[1]} · visuals`;
  return 'visuals';
}
function inferAudioDetail(t) {
  if (/voice|narrat|tone|speak/.test(t)) return 'narration voice';
  if (/music|score/.test(t)) return 'score';
  if (/sfx|sound/.test(t)) return 'sfx';
  return 'audio';
}
function buildReply(userText, target) {
  const t = userText.toLowerCase();
  const plan = [];
  if (target.type === 'Audio') {
    if (/deep|serious|low/.test(t)) plan.push({ label: 'Swap narrator to "Atlas" (baritone, grounded)', diff: 'Iris → Atlas' });
    else if (/warm/.test(t))         plan.push({ label: 'Apply warm-EQ preset on narration', diff: '+2dB low-mids' });
    else                              plan.push({ label: 'Adjust audio parameters', diff: '—' });
  } else if (target.type === 'Video Frame') {
    plan.push({ label: 'Re-grade target scene', diff: '-12% exposure, cooler cast' });
  } else if (target.type === 'Pacing') {
    plan.push({ label: 'Retime scene', diff: '1.00x → 0.90x' });
  } else {
    plan.push({ label: 'Rewrite dialogue line', diff: 'pending approval' });
  }
  return {
    role: 'assistant',
    targets: [target],
    plan,
    content: `I'll route this as a ${target.type.toLowerCase()} edit and re-render only what changed.`,
    confidence: 0.88,
    eta: '26s',
    applied: false,
    pendingApproval: true,
  };
}

// --- message components ---
const AgentAvatar = () => (
  <div style={{
    width: 28, height: 28, borderRadius: 8, flexShrink: 0,
    background: 'linear-gradient(135deg, rgba(240,138,75,0.35), rgba(245,166,35,0.18))',
    border: '1px solid rgba(240,138,75,0.4)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: 'var(--violet)',
  }}>
    <Icon name="wand" size={14}/>
  </div>
);

const Dots = () => (
  <div style={{ display: 'inline-flex', gap: 3, marginLeft: 4 }}>
    {[0,1,2].map(i => (
      <div key={i} style={{
        width: 4, height: 4, borderRadius: '50%', background: 'var(--violet)',
        animation: `cai-pulse 1.2s ease-in-out ${i * 0.15}s infinite`,
      }}></div>
    ))}
  </div>
);

const DetectedTargetChip = ({ target }) => {
  const colorMap = {
    'Audio':       { bg: 'rgba(245,166,35,0.12)', bd: 'rgba(245,166,35,0.4)', fg: 'var(--cyan)' },
    'Video Frame': { bg: 'rgba(240,138,75,0.12)', bd: 'rgba(240,138,75,0.4)', fg: 'var(--violet)' },
    'Script':      { bg: 'rgba(255,122,51,0.12)', bd: 'rgba(255,122,51,0.4)', fg: 'var(--blue-soft)' },
    'Pacing':      { bg: 'rgba(217,164,65,0.12)', bd: 'rgba(217,164,65,0.4)', fg: 'var(--amber)' },
  };
  const c = colorMap[target.type] || colorMap.Script;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ fontSize: 11, color: 'var(--text-mute)', letterSpacing: '0.05em' }}>Detected target</div>
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        fontSize: 11.5, padding: '4px 10px',
        borderRadius: 999,
        background: c.bg, border: `1px solid ${c.bd}`, color: c.fg,
      }}>
        <span style={{ width: 6, height: 6, borderRadius: 50, background: 'currentColor', boxShadow: '0 0 6px currentColor' }}></span>
        <span style={{ fontWeight: 600 }}>{target.type}</span>
        {target.detail && <span style={{ color: 'var(--text-dim)' }}>· {target.detail}</span>}
      </div>
    </div>
  );
};

const Message = ({ m }) => {
  if (m.role === 'system') {
    return (
      <div style={{
        fontSize: 11.5, color: 'var(--text-mute)',
        textAlign: 'center', margin: '0 auto 20px', maxWidth: 480,
        padding: '6px 12px', background: 'rgba(245,239,230,0.02)',
        border: '1px solid var(--line)', borderRadius: 999,
      }}>{m.content}</div>
    );
  }
  if (m.role === 'user') {
    return (
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
        <div style={{
          maxWidth: '72%',
          background: 'linear-gradient(180deg, rgba(232,84,10,0.22), rgba(232,84,10,0.1))',
          border: '1px solid rgba(232,84,10,0.35)',
          borderRadius: '12px 12px 3px 12px',
          padding: '9px 13px',
          fontSize: 13.5, lineHeight: 1.5,
        }}>
          {m.content}
          <div style={{ fontSize: 10, color: 'var(--text-mute)', marginTop: 4, textAlign: 'right' }} className="mono">{m.time}</div>
        </div>
      </div>
    );
  }
  // assistant
  return (
    <div style={{ display: 'flex', gap: 10, marginBottom: 18, alignItems: 'flex-start' }}>
      <AgentAvatar/>
      <div style={{ maxWidth: '80%', minWidth: 0 }}>
        {m.targets && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
            {m.targets.map((t, i) => <DetectedTargetChip key={i} target={t}/>)}
          </div>
        )}
        <div className="cai-card" style={{
          padding: '10px 14px',
          background: 'rgba(240,138,75,0.05)',
          borderColor: 'rgba(240,138,75,0.25)',
          borderRadius: '12px 12px 12px 3px',
        }}>
          <div style={{ fontSize: 13.5, lineHeight: 1.5, textWrap: 'pretty' }}>{m.content}</div>

          {m.plan && (
            <div style={{
              marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--line)',
              display: 'flex', flexDirection: 'column', gap: 5,
            }}>
              {m.plan.map((p, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  fontSize: 11.5, color: 'var(--text-dim)',
                }}>
                  <Icon name="check" size={11}/>
                  <span style={{ color: 'var(--text)' }}>{p.label}</span>
                  <span className="mono" style={{ marginLeft: 'auto', color: 'var(--cyan)', fontSize: 10.5 }}>{p.diff}</span>
                </div>
              ))}
            </div>
          )}

          <div style={{
            marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--line)',
            display: 'flex', alignItems: 'center', gap: 10,
          }}>
            <div style={{ fontSize: 10.5, color: 'var(--text-mute)' }} className="mono">
              confidence {Math.round((m.confidence || 0) * 100)}% · eta {m.eta || '—'}
            </div>
            <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
              {m.applied ? (
                <div className="cai-chip complete" style={{ padding: '3px 8px', fontSize: 10 }}>
                  <span className="dot"></span>Applied → {m.resultVersion}
                </div>
              ) : m.pendingApproval ? (
                <>
                  <button className="cai-btn sm ghost">Reject</button>
                  <button className="cai-btn sm primary" style={{ padding: '6px 11px' }}>Apply edit</button>
                </>
              ) : null}
            </div>
          </div>
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-mute)', marginTop: 4, paddingLeft: 4 }} className="mono">{m.time}</div>
      </div>
    </div>
  );
};

Object.assign(window, { EditAgentScreen });
