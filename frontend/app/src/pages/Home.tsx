// CineAI — Screen 1: Home / Compose

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon, TopNav } from '../components/primitives';
import { generateVideo } from '../services/api';

export const Home: React.FC = () => {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState("A lonely astronaut discovers a glowing crystal on Mars. As she picks it up, the rocks around her start to hum and pulse with light. She whispers: \"It's… alive.\"");
  const [genre, setGenre] = useState('Sci-Fi');
  const [tone, setTone] = useState('Cinematic');
  const [duration, setDuration] = useState('60s');
  const [aspect, setAspect] = useState('16:9');
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!prompt.trim() || generating) return;
    setGenerating(true);
    setError(null);

    try {
      // Call the backend API to start video generation
      const response = await generateVideo({ prompt, genre, tone, duration, aspect });

      // Navigate to progress screen with the returned run_id
      navigate(`/progress/${response.run_id}`);
    } catch (err) {
      console.error('Failed to generate video:', err);
      setError(err instanceof Error ? err.message : 'Failed to start generation');
      setGenerating(false);

      // Fallback to mock navigation for development
      setTimeout(() => {
        navigate('/progress/run_a7b3f1');
      }, 700);
    }
  };

  const genres = ['Sci-Fi', 'Documentary', 'Fantasy', 'Thriller', 'Comedy', 'Drama'];
  const tones = ['Cinematic', 'Playful', 'Dark', 'Warm', 'Suspense'];
  const durations = ['30s', '60s', '90s', '2 min'];
  const aspects = ['16:9', '9:16', '1:1'];

  const suggestions = [
    'A deep-sea documentary about bioluminescent jellyfish',
    'Time-lapse of a city from sunrise to midnight',
    'Robot learning to paint in a quiet studio',
    'Two strangers meeting on a Tokyo train at 3am',
  ];

  return (
    <>
      <TopNav active="home" onNav={(id) => navigate(`/${id === 'home' ? '' : id}`)} />
      <div className="bg-grid"></div>
      <div className="bg-glow" style={{ top: '-200px', left: '50%', transform: 'translateX(-50%)' }}></div>

      <div style={{
        position: 'relative', zIndex: 2,
        height: 'calc(100% - 57px)',
        overflow: 'auto',
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        padding: '48px 48px 64px',
      }}>
        {/* Kicker */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '6px 12px',
          background: 'rgba(245,166,35,0.08)',
          border: '1px solid rgba(245,166,35,0.28)',
          borderRadius: 999,
          fontSize: 11.5, color: 'var(--cyan)',
          letterSpacing: '0.02em',
          marginBottom: 24,
        }}>
          <Icon name="sparkles" size={12}/>
          <span>Pipeline 2.4 · Multi-agent rendering is live</span>
        </div>

        <h1 style={{
          fontSize: 52, fontWeight: 600, margin: 0,
          letterSpacing: '-0.035em', textAlign: 'center',
          lineHeight: 1.05,
        }}>
          From idea to finished film,
          <br/>
          <span style={{
            background: 'linear-gradient(92deg, #FF7A33, #F5A623 60%, #F08A4B)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>in a single prompt.</span>
        </h1>
        <p style={{
          color: 'var(--text-dim)', fontSize: 15, marginTop: 14, marginBottom: 36,
          textAlign: 'center', maxWidth: 560, lineHeight: 1.5,
        }}>
          Describe what you want to see. CineAI will script it, voice it, render it,
          and hand you a finished video with editable scenes.
        </p>

        {/* Prompt card */}
        <div className="cai-card" style={{
          width: '100%', maxWidth: 820,
          padding: 4,
          background: 'linear-gradient(180deg, rgba(245,166,35,0.1), rgba(232,84,10,0.05) 40%, rgba(30,26,22,0.6))',
          borderColor: 'rgba(232,84,10,0.3)',
          boxShadow: '0 20px 60px -20px rgba(0,0,0,0.7), 0 0 40px -10px rgba(232,84,10,0.22)',
        }}>
          <div style={{
            background: 'rgba(13,13,13,0.92)', borderRadius: 10,
            padding: '18px 20px 14px',
          }}>
            <textarea
              className="cai-textarea"
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="Describe your video idea…"
              style={{
                border: 'none', background: 'transparent',
                padding: 0, fontSize: 16, lineHeight: 1.55,
                minHeight: 110, resize: 'none',
                boxShadow: 'none',
              }}
              onFocus={e => (e.target as HTMLTextAreaElement).style.boxShadow = 'none'}
            />

            {/* Controls row */}
            <div style={{
              marginTop: 14, paddingTop: 14,
              borderTop: '1px solid var(--line)',
              display: 'flex', alignItems: 'center', gap: 14,
              flexWrap: 'wrap',
            }}>
              <PromptSelect label="Genre" value={genre} options={genres} onChange={setGenre} icon="layers"/>
              <PromptSelect label="Tone" value={tone} options={tones} onChange={setTone} icon="palette"/>
              <PromptSelect label="Duration" value={duration} options={durations} onChange={setDuration} icon="clock"/>
              <PromptSelect label="Aspect" value={aspect} options={aspects} onChange={setAspect} icon="fullscreen"/>

              <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ fontSize: 11.5, color: 'var(--text-mute)' }} className="mono">
                  ~{Math.round(prompt.length / 5)} tokens
                </div>
                <button
                  className="cai-btn primary"
                  onClick={handleGenerate}
                  disabled={generating || !prompt.trim()}
                  style={{
                    padding: '10px 20px', fontSize: 13, fontWeight: 600,
                    opacity: generating ? 0.8 : 1,
                  }}
                >
                  {generating ? (
                    <>
                      <svg width="14" height="14" viewBox="0 0 24 24" style={{ animation: 'cai-spin 0.8s linear infinite' }}>
                        <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="2.5" strokeDasharray="12 40" strokeLinecap="round"/>
                      </svg>
                      Initializing…
                    </>
                  ) : (
                    <>
                      <Icon name="sparkles" size={14}/>
                      Generate Film
                    </>
                  )}
                </button>
              </div>
            </div>
            {error && (
              <div style={{
                marginTop: 10, padding: '8px 12px', borderRadius: 8,
                background: 'rgba(242,106,63,0.1)', border: '1px solid rgba(242,106,63,0.3)',
                fontSize: 12, color: 'var(--red)',
              }}>
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Suggestions */}
        <div style={{ width: '100%', maxWidth: 820, marginTop: 28 }}>
          <div style={{
            fontSize: 11, color: 'var(--text-mute)',
            textTransform: 'uppercase', letterSpacing: '0.1em',
            marginBottom: 10,
          }}>Try a starting point</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {suggestions.map((s, i) => (
              <button key={i} className="cai-btn sm"
                onClick={() => setPrompt(s)}
                style={{ fontWeight: 400, color: 'var(--text-dim)' }}>
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Recent runs */}
        <div style={{ width: '100%', maxWidth: 820, marginTop: 40 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <div style={{ fontSize: 13, fontWeight: 500 }}>Recent renders</div>
            <div style={{ fontSize: 12, color: 'var(--text-dim)', cursor: 'pointer' }}>View all →</div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
            {[
              { t: 'Neon Tokyo at midnight', meta: '60s · 9:16 · Cinematic', status: 'complete', age: '2h ago' },
              { t: 'Bee colony micro-doc', meta: '90s · 16:9 · Documentary', status: 'complete', age: 'yesterday' },
              { t: 'Robot chef makes ramen', meta: '30s · 1:1 · Playful', status: 'complete', age: '3d ago' },
            ].map((r, i) => (
              <div key={i} className="cai-card" style={{ padding: 12, cursor: 'pointer' }}>
                <div className="cai-placeholder" style={{ height: 70, marginBottom: 10, fontSize: 9 }}>thumbnail</div>
                <div style={{ fontSize: 12.5, fontWeight: 500, marginBottom: 4, textWrap: 'pretty' }}>{r.t}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: 10.5, color: 'var(--text-mute)' }} className="mono">{r.meta}</div>
                  <div style={{ fontSize: 10.5, color: 'var(--text-mute)' }}>{r.age}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

interface PromptSelectProps {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
  icon: string;
}

const PromptSelect: React.FC<PromptSelectProps> = ({ label, value, options, onChange, icon }) => {
  const [open, setOpen] = useState(false);

  return (
    <div style={{ position: 'relative' }}>
      <button
        className="cai-btn sm"
        onClick={() => setOpen(o => !o)}
        onBlur={() => setTimeout(() => setOpen(false), 120)}
        style={{ gap: 6, padding: '6px 10px' }}
      >
        <Icon name={icon} size={12}/>
        <span style={{ color: 'var(--text-mute)' }}>{label}</span>
        <span style={{ color: 'var(--text)', fontWeight: 500 }}>{value}</span>
        <Icon name="chevron-down" size={11}/>
      </button>
      {open && (
        <div style={{
          position: 'absolute', top: 'calc(100% + 4px)', left: 0,
          background: '#1A1612', border: '1px solid var(--line-strong)',
          borderRadius: 8, padding: 4, zIndex: 20, minWidth: 140,
          boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
        }}>
          {options.map(o => (
            <div key={o}
              onMouseDown={() => { onChange(o); setOpen(false); }}
              style={{
                padding: '6px 10px', borderRadius: 5,
                fontSize: 12, cursor: 'pointer',
                background: o === value ? 'rgba(232,84,10,0.18)' : 'transparent',
                color: o === value ? 'var(--text)' : 'var(--text-dim)',
              }}>{o}</div>
          ))}
        </div>
      )}
    </div>
  );
};
