/* BodyOps · UI Kit — icons, primitives, device frames (grayscale wireframe)
   Exports to window. Load after React, before screen files. */

/* ───────────────────────── Icons (geometric line set) ───────────────────── */
const BO_ICONS = {
  home:    'M3 10.5 12 3l9 7.5M5.5 9.2V20a1 1 0 0 0 1 1H10v-5h4v5h3.5a1 1 0 0 0 1-1V9.2',
  meal:    'M5 3v8m0 0a2 2 0 0 0 2-2V3M3 3v6a2 2 0 0 0 2 2M19 3c-1.7 0-3 2-3 5s1 3 1 3v8M19 3c1.7 0 1 8-2 8',
  camera:  'M4 8.5A1.5 1.5 0 0 1 5.5 7H8l1.2-2h5.6L16 7h2.5A1.5 1.5 0 0 1 20 8.5v9A1.5 1.5 0 0 1 18.5 19h-13A1.5 1.5 0 0 1 4 17.5zM12 16.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z',
  workout: 'M6.5 9v6M17.5 9v6M3.5 10.5v3M20.5 10.5v3M6.5 12h11',
  progress:'M4 20V4M4 20h16M8 16l3.5-4 3 2.5L20 8',
  coach:   'M12 3l2.1 4.9L19 9l-4.9 2.1L12 16l-2.1-4.9L5 9l4.9-1.1zM18.5 16l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z',
  weight:  'M5 8h14l1.5 11a1 1 0 0 1-1 1.1H4.5a1 1 0 0 1-1-1.1zM9 8a3 3 0 1 1 6 0M12 12v2.5M12 12l-2.2 1',
  water:   'M12 3.5C12 3.5 6 10 6 14.5a6 6 0 0 0 12 0C18 10 12 3.5 12 3.5z',
  check:   'M5 12.5l4.5 4.5L19 6.5',
  chevR:   'M9 5l7 7-7 7',
  chevL:   'M15 5l-7 7 7 7',
  chevD:   'M5 9l7 7 7-7',
  chevU:   'M5 15l7-7 7 7',
  plus:    'M12 5v14M5 12h14',
  bell:    'M6 9a6 6 0 0 1 12 0c0 5 1.5 7 1.5 7h-15S6 14 6 9zM9.5 20a2.5 2.5 0 0 0 5 0',
  gear:    'M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM19.4 13a7.8 7.8 0 0 0 0-2l2-1.5-2-3.5-2.4 1a7.6 7.6 0 0 0-1.7-1L15 3H9l-.3 2.6a7.6 7.6 0 0 0-1.7 1l-2.4-1-2 3.5L2.6 11a7.8 7.8 0 0 0 0 2l-2 1.5 2 3.5 2.4-1c.5.4 1.1.7 1.7 1L9 21h6l.3-2.6c.6-.3 1.2-.6 1.7-1l2.4 1 2-3.5z',
  flame:   'M12 21c3.3 0 6-2.4 6-5.7 0-3.6-3-5.3-2.4-9.3-2 .6-5 3-5 6.2C8.7 11 8 9.5 8 8c-1.5 1.3-2 3.4-2 5.3C6 18 8.7 21 12 21z',
  arrowD:  'M12 5v14M6 13l6 6 6-6',
  arrowU:  'M12 19V5M6 11l6-6 6 6',
  x:       'M6 6l12 12M18 6L6 18',
  search:  'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4',
  cal:     'M4 7a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1zM4 10h16M8 4v4M16 4v4',
  clock:   'M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM12 8v4.5l3 2',
  moon:    'M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z',
  steps:   'M7 20c-1.5 0-2.5-1-2.5-3 0-1.6.6-3 .6-4.4 0-1-.4-1.6-.4-2.6 0-1.6 1-2.8 2.4-2.8s2.2 1.1 2.2 3c0 1.3-.4 2-.4 3.4 0 2.4.3 6.4-1.9 6.4zM17 16c1.5 0 2.5-1 2.5-3 0-1.6-.6-3-.6-4.4 0-1 .4-1.6.4-2.6 0-1.6-1-2.8-2.4-2.8s-2.2 1.1-2.2 3c0 1.3.4 2 .4 3.4 0 2.4-.3 6.4 1.9 6.4z',
  edit:    'M5 19h14M6 15l9-9 3 3-9 9H6z',
  trophy:  'M7 4h10v4a5 5 0 0 1-10 0zM7 6H4v1a3 3 0 0 0 3 3M17 6h3v1a3 3 0 0 1-3 3M9 19h6M12 13v6',
  share:   'M12 16V4M8 8l4-4 4 4M5 14v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5',
  dots:    'M5 12h.01M12 12h.01M19 12h.01',
  back:    'M19 12H5M11 18l-6-6 6-6',
  mic:     'M12 4a2.5 2.5 0 0 1 2.5 2.5v5a2.5 2.5 0 0 1-5 0v-5A2.5 2.5 0 0 1 12 4zM6 11a6 6 0 0 0 12 0M12 17v3',
  send:    'M5 12l15-7-7 15-2.5-5.5L5 12z',
  bolt:    'M13 3 4 14h6l-1 7 9-11h-6z',
  target:  'M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 11.5a.5.5 0 1 0 0 1 .5.5 0 0 0 0-1z',
  scale:   'M12 4v3M5 7h14l-2.5 6h-9zM7 20h10M9 13l-1 7M15 13l1 7',
  apple:   'M12 7c-1-2-3.5-2.5-5 0s-1 8 1 10c1 .8 2 .4 4 .4s3 .4 4-.4c2-2 2.5-7.5 1-10s-4-2-5 0zM12 7c0-1.5.5-3 2-3.5',
  list:    'M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01',
  filter:  'M4 6h16M7 12h10M10 18h4',
  info:    'M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16zM12 11v5M12 8h.01',
  link:    'M9 15l6-6M10 6l1-1a3.5 3.5 0 0 1 5 5l-1 1M14 18l-1 1a3.5 3.5 0 0 1-5-5l1-1',
  download:'M12 4v10M8 11l4 4 4-4M5 19h14',
  play:    'M8 5v14l11-7z',
  pause:   'M9 5v14M15 5v14',
  trend:   'M4 14l4-4 3 3 5-6M16 7h3v3',
  user:    'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM5 20c0-3.3 3-5.5 7-5.5s7 2.2 7 5.5',
};

function Icon({ name, size = 18, stroke = 1.6, color = 'currentColor', fill = false, style = {} }) {
  const d = BO_ICONS[name] || BO_ICONS.info;
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={fill ? color : 'none'}
      stroke={fill ? 'none' : color} strokeWidth={stroke} strokeLinecap="round"
      strokeLinejoin="round" style={{ flexShrink: 0, display: 'block', ...style }}>
      <path d={d} />
    </svg>
  );
}

/* ───────────────────────── Layout primitives ─────────────────────────────── */
function Card({ children, pad = 16, className = '', style = {}, onClick, elevated = false, flat = false }) {
  return (
    <div onClick={onClick} className={className} style={{
      background: 'var(--card)',
      border: '1px solid var(--line)',
      borderRadius: 'var(--r-lg)',
      boxShadow: flat ? 'none' : (elevated ? 'var(--sh-2)' : 'var(--sh-1)'),
      padding: pad,
      cursor: onClick ? 'pointer' : 'default',
      ...style,
    }}>{children}</div>
  );
}

function Eyebrow({ children, style = {} }) {
  return <div className="eyebrow" style={style}>{children}</div>;
}

function Row({ children, gap = 10, align = 'center', justify = 'flex-start', wrap = false, style = {} }) {
  return <div style={{ display: 'flex', alignItems: align, justifyContent: justify, gap, flexWrap: wrap ? 'wrap' : 'nowrap', ...style }}>{children}</div>;
}
function Col({ children, gap = 10, style = {} }) {
  return <div style={{ display: 'flex', flexDirection: 'column', gap, ...style }}>{children}</div>;
}
function Divider({ style = {} }) {
  return <div style={{ height: 1, background: 'var(--line)', width: '100%', ...style }} />;
}
function Spacer({ h = 12 }) { return <div style={{ height: h }} />; }

/* ───────────────────────── Buttons / chips / tags ────────────────────────── */
function Btn({ children, variant = 'primary', size = 'md', icon, iconRight, full = false, onClick, style = {}, disabled = false }) {
  const sizes = {
    sm: { h: 34, fs: 13, px: 12, gap: 6 },
    md: { h: 44, fs: 14.5, px: 16, gap: 8 },
    lg: { h: 52, fs: 16, px: 20, gap: 9 },
  }[size];
  const variants = {
    primary: { background: 'var(--fill-ink)', color: '#fff', border: '1px solid var(--fill-ink)' },
    secondary: { background: 'var(--card)', color: 'var(--ink)', border: '1px solid var(--line-3)' },
    ghost: { background: 'transparent', color: 'var(--ink-2)', border: '1px solid transparent' },
    soft: { background: 'var(--paper-2)', color: 'var(--ink)', border: '1px solid transparent' },
  }[variant];
  return (
    <button className="focusable" onClick={onClick} disabled={disabled} style={{
      height: sizes.h, padding: `0 ${sizes.px}px`, fontSize: sizes.fs,
      fontFamily: 'var(--sans)', fontWeight: 600, letterSpacing: 0.1,
      borderRadius: 'var(--r-md)', display: 'inline-flex', alignItems: 'center',
      justifyContent: 'center', gap: sizes.gap, cursor: disabled ? 'not-allowed' : 'pointer',
      width: full ? '100%' : 'auto', opacity: disabled ? 0.4 : 1, ...variants, ...style,
    }}>
      {icon && <Icon name={icon} size={sizes.fs + 3} stroke={1.8} />}
      {children}
      {iconRight && <Icon name={iconRight} size={sizes.fs + 3} stroke={1.8} />}
    </button>
  );
}

function Chip({ children, active = false, icon, onClick, style = {} }) {
  return (
    <button onClick={onClick} className="focusable" style={{
      height: 32, padding: '0 12px', borderRadius: 'var(--r-pill)',
      fontFamily: 'var(--mono)', fontSize: 11.5, fontWeight: 600, letterSpacing: 0.02,
      display: 'inline-flex', alignItems: 'center', gap: 6, cursor: 'pointer',
      background: active ? 'var(--fill-ink)' : 'var(--card)',
      color: active ? '#fff' : 'var(--ink-2)',
      border: `1px solid ${active ? 'var(--fill-ink)' : 'var(--line-2)'}`,
      ...style,
    }}>
      {icon && <Icon name={icon} size={13} stroke={1.8} />}
      {children}
    </button>
  );
}

function Tag({ children, style = {} }) {
  return <span style={{
    fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 600, letterSpacing: 0.04,
    textTransform: 'uppercase', padding: '3px 7px', borderRadius: 'var(--r-xs)',
    background: 'var(--paper-2)', color: 'var(--ink-2)', whiteSpace: 'nowrap',
    display: 'inline-flex', alignItems: 'center', gap: 4, ...style,
  }}>{children}</span>;
}

/* ───────────────────────── Bars, rings, confidence ───────────────────────── */
function Bar({ value = 0, track = 'var(--fill)', fill = 'var(--ink)', h = 8, radius = 999, style = {} }) {
  return (
    <div style={{ width: '100%', height: h, background: track, borderRadius: radius, overflow: 'hidden', ...style }}>
      <div style={{ width: `${Math.max(0, Math.min(100, value))}%`, height: '100%', background: fill, borderRadius: radius }} />
    </div>
  );
}

function Ring({ value = 0, size = 64, stroke = 7, track = 'var(--fill)', fill = 'var(--ink)', children }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const off = c * (1 - Math.max(0, Math.min(100, value)) / 100);
  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={track} strokeWidth={stroke} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={fill} strokeWidth={stroke}
          strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round" />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
        {children}
      </div>
    </div>
  );
}

function Confidence({ level = 'high', showLabel = true }) {
  const map = { high: { n: 3, t: 'High' }, med: { n: 2, t: 'Medium' }, low: { n: 1, t: 'Low' } };
  const { n, t } = map[level] || map.high;
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
      <span style={{ display: 'inline-flex', gap: 2, alignItems: 'flex-end' }}>
        {[5, 8, 11].map((h, i) => (
          <span key={i} style={{ width: 3, height: h, borderRadius: 1,
            background: i < n ? 'var(--ink)' : 'var(--fill-2)' }} />
        ))}
      </span>
      {showLabel && <span className="mono" style={{ fontSize: 10.5, color: 'var(--ink-3)', fontWeight: 600 }}>{t}</span>}
    </span>
  );
}

/* ───────────────────────── Field / input look ────────────────────────────── */
function Field({ label, value, placeholder, suffix, icon, big = false, hint, onClick, active = false }) {
  return (
    <label style={{ display: 'block' }} onClick={onClick}>
      {label && <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, fontWeight: 600, letterSpacing: 0.08, textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 7 }}>{label}</div>}
      <div className="focusable" tabIndex={0} style={{
        minHeight: big ? 64 : 48, display: 'flex', alignItems: 'center', gap: 10,
        padding: big ? '0 18px' : '0 14px', borderRadius: 'var(--r-md)',
        background: 'var(--card)', border: `1.5px solid ${active ? 'var(--ink)' : 'var(--line-2)'}`,
        cursor: onClick ? 'pointer' : 'text',
      }}>
        {icon && <Icon name={icon} size={18} color="var(--ink-3)" />}
        <span style={{ flex: 1, fontFamily: big ? 'var(--mono)' : 'var(--sans)',
          fontSize: big ? 26 : 15, fontWeight: big ? 700 : 500,
          color: value ? 'var(--ink)' : 'var(--ink-4)' }}>
          {value || placeholder}
        </span>
        {suffix && <span style={{ fontFamily: 'var(--mono)', fontSize: big ? 15 : 13, color: 'var(--ink-3)', fontWeight: 600 }}>{suffix}</span>}
      </div>
      {hint && <div style={{ fontSize: 11.5, color: 'var(--ink-3)', marginTop: 6 }}>{hint}</div>}
    </label>
  );
}

/* ───────────────────────── Image placeholder ─────────────────────────────── */
function ImageSlot({ label = 'Image', h = 120, w = '100%', radius = 'var(--r-md)', icon, style = {} }) {
  return (
    <div className="hatch" style={{ width: w, height: h, borderRadius: radius, ...style }}>
      <span className="hatch-label">
        {icon && <Icon name={icon} size={11} style={{ display: 'inline', verticalAlign: '-1px', marginRight: 4 }} />}
        {label}
      </span>
    </div>
  );
}

/* ───────────────────────── Avatar ────────────────────────────────────────── */
function Avatar({ initials = 'AC', size = 38, ring = false }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: 'var(--r-pill)',
      background: 'var(--paper-2)', border: ring ? '1.5px solid var(--ink)' : '1px solid var(--line-2)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'var(--mono)', fontWeight: 700, fontSize: size * 0.34, color: 'var(--ink-2)',
      flexShrink: 0,
    }}>{initials}</div>
  );
}

/* ───────────────────────── Coach bubble mark ─────────────────────────────── */
function CoachMark({ size = 38 }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: 'var(--r-md)',
      background: 'var(--fill-ink)', display: 'flex', alignItems: 'center', justifyContent: 'center',
      flexShrink: 0,
    }}>
      <Icon name="coach" size={size * 0.5} color="#fff" stroke={1.6} />
    </div>
  );
}

/* ═════════════════════════ DEVICE FRAMES ═════════════════════════════════ */

function PhoneStatusBar({ dark = false }) {
  const c = dark ? '#fff' : 'var(--ink)';
  return (
    <div style={{ height: 44, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 26px 0 30px', position: 'relative', zIndex: 5, flexShrink: 0 }}>
      <span style={{ fontFamily: 'var(--mono)', fontSize: 13, fontWeight: 700, color: c, letterSpacing: 0.02 }}>9:41</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <svg width="17" height="11" viewBox="0 0 17 11"><rect x="0" y="6.5" width="3" height="4.5" rx="0.6" fill={c}/><rect x="4.5" y="4" width="3" height="7" rx="0.6" fill={c}/><rect x="9" y="1.5" width="3" height="9.5" rx="0.6" fill={c}/><rect x="13.5" y="0" width="3" height="11" rx="0.6" fill={c} opacity="0.4"/></svg>
        <svg width="24" height="12" viewBox="0 0 24 12"><rect x="0.5" y="0.5" width="20" height="11" rx="3" stroke={c} strokeOpacity="0.4" fill="none"/><rect x="2" y="2" width="15" height="8" rx="1.6" fill={c}/><rect x="22" y="3.5" width="1.5" height="5" rx="0.75" fill={c} fillOpacity="0.5"/></svg>
      </div>
    </div>
  );
}

function PhoneFrame({ children, label, sublabel, dark = false, width = 390, height = 844, noChrome = false, style = {} }) {
  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'flex-start', gap: 12, ...style }}>
      {label && (
        <div style={{ paddingLeft: 4 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, color: 'var(--ink)', letterSpacing: 0.02 }}>{label}</div>
          {sublabel && <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>{sublabel}</div>}
        </div>
      )}
      <div style={{
        width: width + 16, height: height + 16, borderRadius: 54, padding: 8,
        background: '#1d1c1a', boxShadow: 'var(--sh-3)', position: 'relative', flexShrink: 0,
      }}>
        <div style={{
          width, height, borderRadius: 46, overflow: 'hidden', position: 'relative',
          background: dark ? '#1d1c1a' : 'var(--paper)', display: 'flex', flexDirection: 'column',
        }}>
          {/* notch */}
          <div style={{ position: 'absolute', top: 9, left: '50%', transform: 'translateX(-50%)',
            width: 118, height: 30, borderRadius: 18, background: '#1d1c1a', zIndex: 40 }} />
          {!noChrome && <PhoneStatusBar dark={dark} />}
          {children}
        </div>
      </div>
    </div>
  );
}

function BrowserFrame({ children, label, sublabel, url = 'app.bodyops.io', width = 1280, height = 820, style = {} }) {
  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', gap: 12, ...style }}>
      {label && (
        <div style={{ paddingLeft: 4 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, color: 'var(--ink)' }}>{label}</div>
          {sublabel && <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>{sublabel}</div>}
        </div>
      )}
      <div style={{ width, borderRadius: 'var(--r-lg)', overflow: 'hidden', background: 'var(--card)',
        border: '1px solid var(--line-2)', boxShadow: 'var(--sh-3)' }}>
        <div style={{ height: 44, background: 'var(--card-2)', borderBottom: '1px solid var(--line)',
          display: 'flex', alignItems: 'center', gap: 14, padding: '0 16px' }}>
          <div style={{ display: 'flex', gap: 7 }}>
            {[0,1,2].map(i => <div key={i} style={{ width: 11, height: 11, borderRadius: 999, background: 'var(--fill-2)', border: '1px solid var(--line-2)' }} />)}
          </div>
          <div style={{ flex: 1, maxWidth: 420, height: 26, borderRadius: 'var(--r-pill)', background: 'var(--paper)',
            border: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: 7, padding: '0 12px' }}>
            <Icon name="link" size={12} color="var(--ink-4)" />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--ink-3)' }}>{url}</span>
          </div>
        </div>
        <div style={{ height, overflow: 'hidden', position: 'relative', background: 'var(--paper)' }}>{children}</div>
      </div>
    </div>
  );
}

/* ───────────────────────── Annotation callout ────────────────────────────── */
function Anno({ n, children, style = {} }) {
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start', ...style }}>
      {n != null && <span style={{ flexShrink: 0, width: 18, height: 18, borderRadius: 999, border: '1.5px solid var(--ink)',
        fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--ink)' }}>{n}</span>}
      <span className="anno">{children}</span>
    </div>
  );
}

Object.assign(window, {
  Icon, BO_ICONS, Card, Eyebrow, Row, Col, Divider, Spacer,
  Btn, Chip, Tag, Bar, Ring, Confidence, Field, ImageSlot, Avatar, CoachMark,
  PhoneFrame, PhoneStatusBar, BrowserFrame, Anno,
});
