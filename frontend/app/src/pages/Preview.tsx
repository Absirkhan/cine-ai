// CineAI — Screen 4: Video Preview + Version History

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Icon, TopNav } from '../components/primitives';
import type { Scene, Version } from '../types';
import { getVideoOutput, getVersionHistory } from '../services/api';

const Preview: React.FC = () => {
  const params = useParams<{ jobId: string }>();
  const jobId = params.jobId;
  const navigate = useNavigate();
  console.log('Job ID:', jobId);

  const [versions, setVersions] = useState<Version[]>([]);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [outputData, setOutputData] = useState<any>(null);
  const [showDownloadMenu, setShowDownloadMenu] = useState<boolean>(false);
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const activeId = versions.find(v => v.active)?.id;
  const [playing, setPlaying] = useState<boolean>(false);
  const [time, setTime] = useState<number>(0);
  const [muted, setMuted] = useState<boolean>(false);
  const [duration, setDuration] = useState<number>(60);

  // Fetch video data and version history on mount
  useEffect(() => {
    if (!jobId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const [output, versionsData] = await Promise.all([
          getVideoOutput(jobId),
          getVersionHistory(jobId),
        ]);

        // Store output data for metadata
        setOutputData(output);

        // Set scenes from output
        if (output.scenes) {
          setScenes(output.scenes);
        }

        // Always set video URL - it will be available after phase 3
        // The video element will show error if file doesn't exist
        setVideoUrl(`/api/runs/${jobId}/assets/final_output.mp4`);

        // Set versions from history
        if (versionsData.versions) {
          setVersions(versionsData.versions);
          // Set active version
          const active = versionsData.versions.find((v: Version) => v.active);
          if (active) {
            // Version is already set to active in the data
          }
        }

        console.log('Video data loaded:', { videoUrl: `/api/runs/${jobId}/assets/final_output.mp4`, output });
      } catch (err) {
        console.error('Failed to fetch video data:', err);

        // Fallback to mock data
        setVersions([
          { id: 'v4', label: 'v4', note: 'Current · Darker opening shot', time: '4 min ago', author: 'Edit Agent', active: true,
            changes: ['Lower key lighting', 'Scene 1 color grade -15%'] },
          { id: 'v3', label: 'v3', note: 'Swapped narrator voice', time: '12 min ago', author: 'Edit Agent',
            changes: ['Voice: Iris → Theo'] },
          { id: 'v2', label: 'v2', note: 'Re-rendered scene 3', time: '28 min ago', author: 'You',
            changes: ['Crystal glow intensity +40%', 'Added subtle camera dolly'] },
          { id: 'v1', label: 'v1', note: 'Initial render', time: '38 min ago', author: 'Pipeline',
            changes: ['Full generation from prompt'] },
        ]);

        setScenes([
          { id: 1, label: 'Opening · Mars plain',    start: 0,  end: 14, color: 'rgba(232,84,10,0.5)' },
          { id: 2, label: 'Discovery · The crystal', start: 14, end: 30, color: 'rgba(245,166,35,0.5)' },
          { id: 3, label: 'Awakening · Light hum',   start: 30, end: 48, color: 'rgba(240,138,75,0.5)' },
          { id: 4, label: 'Outro · Whisper',         start: 48, end: 60, color: 'rgba(217,164,65,0.5)' },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [jobId]);

  // Sync playing state with video element
  useEffect(() => {
    if (!videoRef.current) return;
    if (playing) {
      videoRef.current.play();
    } else {
      videoRef.current.pause();
    }
  }, [playing]);

  // Update time from video element
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => setTime(video.currentTime);
    const handleDurationChange = () => setDuration(video.duration || 60);
    const handlePlay = () => setPlaying(true);
    const handlePause = () => setPlaying(false);
    const handleEnded = () => setPlaying(false);

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('ended', handleEnded);
    };
  }, [videoRef.current]);

  const activateVersion = (id: string) => {
    // In a real app, you might want to call an API to activate the version
    // For now, just update the local state
    setVersions(vs => vs.map(v => ({ ...v, active: v.id === id })));
  };

  const undoTo = (id: string) => {
    // Undo = roll the "current" flag back to this version, remove nothing from history
    activateVersion(id);
  };

  const fmt = (s: number) => {
    const m = Math.floor(s / 60); const sec = Math.floor(s % 60);
    return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
  };

  // Ensure scenes have default mock data if empty
  const displayScenes: Scene[] = scenes.length > 0 ? scenes : [
    { id: 1, label: 'Scene 1',    start: 0,  end: duration / 4, color: 'rgba(232,84,10,0.5)' },
    { id: 2, label: 'Scene 2', start: duration / 4, end: duration / 2, color: 'rgba(245,166,35,0.5)' },
    { id: 3, label: 'Scene 3',   start: duration / 2, end: 3 * duration / 4, color: 'rgba(240,138,75,0.5)' },
    { id: 4, label: 'Scene 4',         start: 3 * duration / 4, end: duration, color: 'rgba(217,164,65,0.5)' },
  ];
  const currentScene = displayScenes.find(s => time >= s.start && time < s.end) || displayScenes[0];

  const handleSeek = (newTime: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
      setTime(newTime);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !muted;
      setMuted(!muted);
    }
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        videoRef.current.requestFullscreen();
      }
    }
  };

  const downloadFile = (url: string, filename: string) => {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleDownloadFinal = () => {
    downloadFile(`/api/runs/${jobId}/assets/final_output.mp4`, `${jobId}_final.mp4`);
    setShowDownloadMenu(false);
  };

  const handleDownloadAll = async () => {
    // Download final output
    downloadFile(`/api/runs/${jobId}/assets/final_output.mp4`, `${jobId}_final.mp4`);

    // Download individual scenes
    if (outputData?.scenes) {
      outputData.scenes.forEach((_: any, index: number) => {
        const sceneVideoName = `scene_video_scene_${String(index).padStart(3, '0')}.mp4`;
        setTimeout(() => {
          downloadFile(`/api/runs/${jobId}/assets/${sceneVideoName}`, `${jobId}_scene_${index + 1}.mp4`);
        }, index * 500); // Stagger downloads
      });
    }
    setShowDownloadMenu(false);
  };

  const handleDownloadScene = (sceneIndex: number) => {
    const sceneVideoName = `scene_video_scene_${String(sceneIndex).padStart(3, '0')}.mp4`;
    downloadFile(`/api/runs/${jobId}/assets/${sceneVideoName}`, `${jobId}_scene_${sceneIndex + 1}.mp4`);
  };

  // Get title from output data or fallback
  const videoTitle = outputData?.story?.title || outputData?.user_prompt?.substring(0, 50) || 'Generated Video';
  const videoParams = outputData?.user_params || {};
  const aspectRatio = videoParams.aspect_ratio || '16:9';
  const runDuration = Math.round(duration) || outputData?.user_params?.duration || 60;

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (showDownloadMenu && !(e.target as Element).closest('.download-menu-container')) {
        setShowDownloadMenu(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showDownloadMenu]);

  return (
    <>
      <TopNav active="preview" onNav={(id) => {
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
        gridTemplateColumns: '1fr 360px',
      }}>
        {/* LEFT — player */}
        <div style={{ overflow: 'auto', padding: '24px 28px 32px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-mute)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 4 }}>
                Final output · <span className="mono">{jobId?.substring(0, 16)}...</span>
              </div>
              <h1 style={{ fontSize: 22, fontWeight: 600, margin: 0, letterSpacing: '-0.02em' }}>
                {videoTitle} · {activeId || 'v1'}
              </h1>
              <div style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 6 }}>
                {runDuration}s · {aspectRatio} · 1920×1080 · H.264
              </div>
            </div>
            <div style={{ position: 'relative' }} className="download-menu-container">
              <button
                className="cai-btn primary"
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                style={{ display: 'flex', alignItems: 'center', gap: 6 }}
              >
                <Icon name="download" size={12}/> Download MP4
                <span style={{ fontSize: 10, marginLeft: 2 }}>▼</span>
              </button>

              {showDownloadMenu && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  marginTop: 8,
                  background: 'var(--bg-1)',
                  border: '1px solid var(--line-strong)',
                  borderRadius: 8,
                  boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
                  minWidth: 220,
                  zIndex: 100,
                  overflow: 'hidden',
                }}>
                  <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--line)', fontSize: 11, color: 'var(--text-mute)' }}>
                    Download Options
                  </div>
                  <div style={{ padding: 4 }}>
                    <button
                      className="cai-btn sm"
                      onClick={handleDownloadFinal}
                      style={{ width: '100%', justifyContent: 'flex-start', marginBottom: 4 }}
                    >
                      <Icon name="download" size={11}/> Final Output Only
                    </button>
                    <button
                      className="cai-btn sm"
                      onClick={handleDownloadAll}
                      style={{ width: '100%', justifyContent: 'flex-start' }}
                    >
                      <Icon name="download" size={11}/> All Scenes + Final
                    </button>
                  </div>
                  <div style={{ padding: '8px 12px', borderTop: '1px solid var(--line)', fontSize: 10, color: 'var(--text-mute)' }}>
                    Individual Scenes
                  </div>
                  <div style={{ padding: 4, maxHeight: 200, overflowY: 'auto' }}>
                    {displayScenes.map((scene, index) => (
                      <button
                        key={scene.id}
                        className="cai-btn sm ghost"
                        onClick={() => handleDownloadScene(index)}
                        style={{ width: '100%', justifyContent: 'flex-start', marginBottom: 2, fontSize: 11 }}
                      >
                        <Icon name="play" size={10}/> Scene {index + 1}: {scene.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
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
            {/* Actual Video Element */}
            {videoUrl ? (
              <video
                ref={videoRef}
                src={videoUrl}
                style={{
                  position: 'absolute',
                  inset: 0,
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                }}
                muted={muted}
                onError={(e) => {
                  console.error('Video load error:', e);
                }}
              />
            ) : loading ? (
              <div style={{
                position: 'absolute', inset: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'rgba(0,0,0,0.8)',
                color: 'var(--text-mute)',
                fontSize: 14,
              }}>
                Loading video...
              </div>
            ) : (
              <>
                {/* Fallback faux frame if no video */}
                <div style={{
                  position: 'absolute', inset: 0,
                  background:
                    `radial-gradient(ellipse at 30% 40%, rgba(245,166,35,0.4), transparent 50%),
                     radial-gradient(ellipse at 70% 70%, rgba(232,84,10,0.3), transparent 55%),
                     linear-gradient(180deg, #1a0f05 0%, #2d1608 50%, #0d0705 100%)`,
                }}></div>
                <div style={{
                  position: 'absolute', left: '38%', top: '48%',
                  width: 120, height: 120, borderRadius: '50%',
                  background: 'radial-gradient(circle, rgba(255,230,180,0.95), rgba(245,166,35,0.5) 40%, transparent 70%)',
                  filter: 'blur(8px)',
                  animation: 'cai-pulse 2.4s ease-in-out infinite',
                }}></div>
                <div style={{
                  position: 'absolute', inset: 0,
                  backgroundImage: 'repeating-radial-gradient(circle at 50% 50%, rgba(245,239,230,0.03) 0 1px, transparent 1px 3px)',
                  mixBlendMode: 'overlay',
                }}></div>
              </>
            )}

            {/* Removed scene label overlay */}

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
                  const newTime = ((e.clientX - rect.left) / rect.width) * duration;
                  handleSeek(newTime);
                }}>
                <div style={{ position: 'absolute', left: 0, right: 0, top: 4, height: 2, background: 'rgba(255,255,255,0.2)', borderRadius: 2 }}></div>
                {displayScenes.map(s => (
                  <div key={s.id} style={{
                    position: 'absolute', top: 2,
                    left: `${(s.start / duration) * 100}%`,
                    width: `${((s.end - s.start) / duration) * 100}%`,
                    height: 6, background: s.color, borderRadius: 2,
                    borderRight: '1px solid rgba(0,0,0,0.5)',
                  }}></div>
                ))}
                <div style={{
                  position: 'absolute', left: 0, top: 4,
                  width: `${(time / duration) * 100}%`, height: 2,
                  background: 'linear-gradient(90deg, var(--blue), var(--cyan))',
                  borderRadius: 2,
                }}></div>
                <div style={{
                  position: 'absolute', left: `${(time / duration) * 100}%`, top: -1,
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
                  {fmt(time)} / {fmt(duration)}
                </div>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
                  <button className="cai-btn icon" onClick={toggleMute}
                    style={{ background: 'rgba(255,255,255,0.06)', border: 'none' }}>
                    <Icon name={muted ? 'mute' : 'volume'} size={14}/>
                  </button>
                  <button className="cai-btn icon" onClick={toggleFullscreen}
                    style={{ background: 'rgba(255,255,255,0.06)', border: 'none' }}>
                    <Icon name="fullscreen" size={14}/>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Scene strip with Final Output */}
          <div style={{
            marginTop: 20,
            display: 'grid',
            gridTemplateColumns: `repeat(auto-fit, minmax(180px, 1fr))`,
            gap: 12,
          }}>
            {/* Individual Scenes */}
            {displayScenes.map((s, index) => {
              const active = currentScene.id === s.id;
              const sceneImageName = `image_scene_${String(index).padStart(3, '0')}.png`;
              const sceneVideoName = `scene_video_scene_${String(index).padStart(3, '0')}.mp4`;
              const sceneImageUrl = `/api/runs/${jobId}/assets/${sceneImageName}`;
              const sceneVideoUrl = `/api/runs/${jobId}/assets/${sceneVideoName}`;
              const hasValidTimes = !isNaN(s.start) && !isNaN(s.end) && isFinite(s.start) && isFinite(s.end);

              return (
                <div key={s.id} className="cai-card" style={{
                  padding: 10,
                  borderColor: active ? 'rgba(245,166,35,0.45)' : 'var(--line)',
                  background: active ? 'rgba(245,166,35,0.08)' : undefined,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onClick={(e) => {
                  e.preventDefault();
                  console.log('Scene clicked:', { index, scene: s, hasValidTimes, start: s.start });
                  if (hasValidTimes) {
                    handleSeek(s.start + 0.5);
                  } else {
                    // Fallback: seek based on index
                    const estimatedStart = (index / displayScenes.length) * duration;
                    handleSeek(estimatedStart);
                  }
                }}>
                  <div style={{
                    height: 100,
                    borderRadius: 6,
                    marginBottom: 8,
                    background: s.color,
                    position: 'relative',
                    overflow: 'hidden',
                  }}>
                    {/* Try video first, fallback to image */}
                    <video
                      src={sceneVideoUrl}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                      }}
                      muted
                      preload="metadata"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                    <img
                      src={sceneImageUrl}
                      alt={`Scene ${s.id}`}
                      style={{
                        position: 'absolute',
                        inset: 0,
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                      }}
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                    <div style={{
                      position: 'absolute', top: 5, left: 6, fontSize: 10,
                      color: '#fff',
                      textShadow: '0 1px 4px rgba(0,0,0,0.9)',
                      background: 'rgba(0,0,0,0.5)',
                      padding: '3px 6px',
                      borderRadius: 4,
                      fontWeight: 600,
                    }} className="mono">
                      SC {String(index + 1).padStart(2, '0')}
                    </div>
                  </div>
                  <div style={{ fontSize: 11.5, color: active ? 'var(--text)' : 'var(--text-dim)', marginBottom: 4, textWrap: 'pretty', fontWeight: 500 }}>
                    {s.label}
                  </div>
                  {hasValidTimes ? (
                    <div style={{ fontSize: 10, color: 'var(--text-mute)' }} className="mono">
                      {fmt(s.start)} – {fmt(s.end)}
                    </div>
                  ) : (
                    <div style={{ fontSize: 10, color: 'var(--text-mute)', fontStyle: 'italic' }}>
                      Click to preview
                    </div>
                  )}
                </div>
              );
            })}

            {/* Final Output Thumbnail */}
            <div className="cai-card" style={{
              padding: 10,
              borderColor: 'rgba(245,166,35,0.6)',
              background: 'rgba(245,166,35,0.1)',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }} onClick={() => handleSeek(0)}>
              <div style={{
                height: 100,
                borderRadius: 6,
                marginBottom: 8,
                background: 'linear-gradient(135deg, rgba(232,84,10,0.3), rgba(245,166,35,0.3))',
                position: 'relative',
                overflow: 'hidden',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <video
                  src={videoUrl || ''}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                  muted
                  preload="metadata"
                />
                <div style={{
                  position: 'absolute', top: 5, left: 6, fontSize: 10,
                  color: '#fff',
                  textShadow: '0 1px 4px rgba(0,0,0,0.9)',
                  background: 'rgba(232,84,10,0.8)',
                  padding: '3px 6px',
                  borderRadius: 4,
                  fontWeight: 600,
                }} className="mono">
                  FINAL
                </div>
              </div>
              <div style={{ fontSize: 11.5, color: 'var(--text)', marginBottom: 4, fontWeight: 600 }}>
                Final Output
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-mute)' }} className="mono">
                {fmt(0)} – {fmt(duration)}
              </div>
            </div>
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

export default Preview;
