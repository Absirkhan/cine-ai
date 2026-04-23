// CineAI — shared primitives (icons, phase defs, small utils)

// Icons — inline SVG, single-color via currentColor
const Icon = ({ name, size = 16, stroke = 1.75 }) => {
  const s = size;
  const props = {
    width: s, height: s, viewBox: '0 0 24 24',
    fill: 'none', stroke: 'currentColor',
    strokeWidth: stroke, strokeLinecap: 'round', strokeLinejoin: 'round',
  };
  switch (name) {
    case 'sparkles':
      return (<svg {...props}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/></svg>);
    case 'script':
      return (<svg {...props}><path d="M4 4h13l3 3v13a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z"/><path d="M7 9h8M7 13h8M7 17h5"/></svg>);
    case 'audio':
      return (<svg {...props}><path d="M3 12v-1a9 9 0 0 1 18 0v1"/><rect x="3" y="12" width="5" height="8" rx="1.5"/><rect x="16" y="12" width="5" height="8" rx="1.5"/></svg>);
    case 'video':
      return (<svg {...props}><rect x="3" y="5" width="14" height="14" rx="2"/><path d="m17 10 4-2v8l-4-2z"/></svg>);
    case 'web':
      return (<svg {...props}><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M7 6.5h.01M10 6.5h.01"/></svg>);
    case 'wand':
      return (<svg {...props}><path d="m15 4 5 5-11 11H4v-5z"/><path d="m12 7 5 5"/></svg>);
    case 'play':
      return (<svg {...props} fill="currentColor" stroke="none"><path d="M8 5v14l11-7z"/></svg>);
    case 'pause':
      return (<svg {...props} fill="currentColor" stroke="none"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>);
    case 'download':
      return (<svg {...props}><path d="M12 3v12M7 10l5 5 5-5M5 21h14"/></svg>);
    case 'rerun':
      return (<svg {...props}><path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5"/></svg>);
    case 'undo':
      return (<svg {...props}><path d="M9 14 4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 6 6v0a6 6 0 0 1-6 6h-3"/></svg>);
    case 'check':
      return (<svg {...props}><path d="m5 12 5 5 9-11"/></svg>);
    case 'send':
      return (<svg {...props}><path d="M4 11 20 4l-7 16-2-7z"/></svg>);
    case 'chevron':
      return (<svg {...props}><path d="m9 6 6 6-6 6"/></svg>);
    case 'chevron-down':
      return (<svg {...props}><path d="m6 9 6 6 6-6"/></svg>);
    case 'dot':
      return (<svg {...props} fill="currentColor" stroke="none"><circle cx="12" cy="12" r="3"/></svg>);
    case 'clock':
      return (<svg {...props}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>);
    case 'layers':
      return (<svg {...props}><path d="m12 2 10 5-10 5L2 7z"/><path d="m2 12 10 5 10-5M2 17l10 5 10-5"/></svg>);
    case 'cpu':
      return (<svg {...props}><rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4"/></svg>);
    case 'eq':
      return (<svg {...props}><path d="M4 12h2M9 6v12M14 9v6M19 4v16"/></svg>);
    case 'palette':
      return (<svg {...props}><path d="M12 3a9 9 0 1 0 0 18 2 2 0 0 0 1.7-3c-.3-.5-.3-1.2 0-1.7a2 2 0 0 1 1.7-1H18a3 3 0 0 0 3-3 9 9 0 0 0-9-9z"/><circle cx="7.5" cy="10.5" r=".8" fill="currentColor"/><circle cx="11.5" cy="7.5" r=".8" fill="currentColor"/><circle cx="16" cy="10" r=".8" fill="currentColor"/></svg>);
    case 'settings':
      return (<svg {...props}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>);
    case 'volume':
      return (<svg {...props}><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></svg>);
    case 'mute':
      return (<svg {...props}><path d="M11 5 6 9H2v6h4l5 4z"/><path d="m23 9-6 6M17 9l6 6"/></svg>);
    case 'fullscreen':
      return (<svg {...props}><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>);
    case 'search':
      return (<svg {...props}><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>);
    case 'plus':
      return (<svg {...props}><path d="M12 5v14M5 12h14"/></svg>);
    case 'pin':
      return (<svg {...props}><path d="M12 17v5M9 3h6l-1 6 3 3H7l3-3z"/></svg>);
    case 'stop':
      return (<svg {...props} fill="currentColor" stroke="none"><rect x="6" y="6" width="12" height="12" rx="1.5"/></svg>);
    case 'code':
      return (<svg {...props}><path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/></svg>);
    default: return null;
  }
};

// Phase definitions
const PHASES = [
  { id: 'script', title: 'Story & Script', subtitle: 'LLM scene breakdown + dialogue',
    icon: 'script', color: 'blue' },
  { id: 'audio', title: 'Audio Generation', subtitle: 'TTS, SFX, music synthesis',
    icon: 'audio', color: 'cyan' },
  { id: 'video', title: 'Video Composition', subtitle: 'Frame generation + stitching',
    icon: 'video', color: 'violet' },
  { id: 'web', title: 'Web Interface', subtitle: 'Preview player + embeds',
    icon: 'web', color: 'blue' },
  { id: 'edit', title: 'Edit Agent', subtitle: 'Natural-language revisions',
    icon: 'wand', color: 'cyan' },
];

// Top nav used across all artboards
const TopNav = ({ active, onNav }) => {
  const items = [
    ['home', 'Compose'],
    ['pipeline', 'Pipeline'],
    ['progress', 'Live Progress'],
    ['preview', 'Preview'],
    ['edit', 'Edit Agent'],
  ];
  return (
    <div className="cai-nav">
      <div className="cai-logo">
        <div className="cai-logo-mark"></div>
        <span>CineAI</span>
        <span style={{ fontSize: 10, color: 'var(--text-mute)', fontWeight: 400, marginLeft: 4, letterSpacing: '0.05em' }}>v2.4</span>
      </div>
      <div className="cai-navlinks">
        {items.map(([id, label]) => (
          <div key={id}
               className={`cai-navlink ${active === id ? 'active' : ''}`}
               onClick={() => onNav && onNav(id)}>
            {label}
          </div>
        ))}
      </div>
      <div className="cai-nav-right">
        <div className="cai-credit">Credits <b>482</b> / 1000</div>
        <div className="cai-avatar">AN</div>
      </div>
    </div>
  );
};

// Small reusable status chip
const StatusChip = ({ status }) => {
  const map = {
    pending: { cls: 'pending', label: 'Pending' },
    queued: { cls: 'pending', label: 'Queued' },
    running: { cls: 'running', label: 'Running' },
    complete: { cls: 'complete', label: 'Complete' },
    error: { cls: 'error', label: 'Error' },
  };
  const v = map[status] || map.pending;
  return (
    <div className={`cai-chip ${v.cls}`}>
      <span className="dot"></span>{v.label}
    </div>
  );
};

Object.assign(window, { Icon, PHASES, TopNav, StatusChip });
