/* BodyOps · Desktop shell — sidebar nav + topbar + router (window.DSCREENS) */

const DESKTOP_NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: 'home' },
  { id: 'd-meals', label: 'Meals', icon: 'meal' },
  { id: 'd-weight', label: 'Weight', icon: 'weight' },
  { id: 'd-workouts', label: 'Workouts', icon: 'workout' },
  { id: 'd-progress', label: 'Progress', icon: 'progress' },
  { id: 'd-coach', label: 'Coach', icon: 'coach' },
];

function DesktopSidebar({ active, onNav, D }) {
  return (
    <div style={{ width: 234, flexShrink: 0, background: 'var(--card)', borderRight: '1px solid var(--line)', display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* logo */}
      <div style={{ padding: '20px 18px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 32, height: 32, borderRadius: 9, background: 'var(--fill-ink)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="bolt" size={18} color="#fff" /></div>
        <div style={{ fontSize: 17, fontWeight: 800, letterSpacing: -0.4 }}>BodyOps</div>
      </div>
      {/* quick log */}
      <div style={{ padding: '0 14px 8px' }}>
        <Btn full size="sm" icon="camera" onClick={() => onNav('d-meals')}>Log a meal</Btn>
      </div>
      {/* nav */}
      <div style={{ flex: 1, padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: 2 }}>
        <div className="eyebrow" style={{ padding: '8px 10px 6px' }}>Menu</div>
        {DESKTOP_NAV.map(n => {
          const on = active === n.id;
          return (
            <button key={n.id} onClick={() => onNav(n.id)} style={{ display: 'flex', alignItems: 'center', gap: 11, height: 40, padding: '0 12px', borderRadius: 'var(--r-md)', border: 'none', cursor: 'pointer',
              background: on ? 'var(--paper-2)' : 'transparent', textAlign: 'left' }}>
              <Icon name={n.icon} size={18} color={on ? 'var(--ink)' : 'var(--ink-3)'} stroke={on ? 2 : 1.6} />
              <span style={{ fontSize: 13.5, fontWeight: on ? 700 : 500, color: on ? 'var(--ink)' : 'var(--ink-2)' }}>{n.label}</span>
              {n.id === 'd-coach' && <span style={{ marginLeft: 'auto', width: 7, height: 7, borderRadius: 999, background: 'var(--ink)' }} />}
            </button>
          );
        })}
      </div>
      {/* settings + user */}
      <div style={{ padding: 12, borderTop: '1px solid var(--line)' }}>
        <button onClick={() => onNav('d-settings')} style={{ display: 'flex', alignItems: 'center', gap: 11, height: 40, padding: '0 12px', width: '100%', borderRadius: 'var(--r-md)', border: 'none', cursor: 'pointer', background: active === 'd-settings' ? 'var(--paper-2)' : 'transparent', textAlign: 'left' }}>
          <Icon name="gear" size={18} color="var(--ink-3)" />
          <span style={{ fontSize: 13.5, fontWeight: 500, color: 'var(--ink-2)' }}>Settings</span>
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 8px 2px' }}>
          <Avatar initials={D.user.initials} size={34} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 12.5, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{D.user.name}</div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)' }}>Day {D.user.dayN} · {D.goal.current} kg</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function DesktopTopBar({ title, sub, right }) {
  return (
    <div style={{ height: 64, flexShrink: 0, borderBottom: '1px solid var(--line)', background: 'var(--paper)', display: 'flex', alignItems: 'center', padding: '0 26px', gap: 16 }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 19, fontWeight: 800, letterSpacing: -0.3 }}>{title}</div>
        {sub && <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 1 }}>{sub}</div>}
      </div>
      {right}
    </div>
  );
}

function DesktopApp({ initial = 'dashboard' }) {
  const [active, setActive] = React.useState(initial);
  const Screens = window.DSCREENS || {};
  const Comp = Screens[active] || (() => <div style={{ padding: 30, fontFamily: 'var(--mono)' }}>Missing: {active}</div>);
  const nav = { go: setActive, tab: setActive };
  return (
    <div style={{ display: 'flex', height: '100%', background: 'var(--paper)' }}>
      <DesktopSidebar active={active} onNav={setActive} D={window.DATA} />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Comp nav={nav} D={window.DATA} />
      </div>
    </div>
  );
}

/* shared desktop content scroller */
function DeskBody({ children, style = {} }) {
  return <div className="bo-scroll" style={{ flex: 1, overflowY: 'auto', padding: 26, ...style }}>{children}</div>;
}

Object.assign(window, { DESKTOP_NAV, DesktopSidebar, DesktopTopBar, DesktopApp, DeskBody });
window.DSCREENS = window.DSCREENS || {};
