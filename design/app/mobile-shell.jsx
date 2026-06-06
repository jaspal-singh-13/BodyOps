/* BodyOps · Mobile shell — top bar, bottom tab nav, screen router.
   Screens register into window.MSCREENS. Exports MobileApp + shared chrome. */

const MOBILE_TABS = [
  { id: 'home', label: 'Home', icon: 'home' },
  { id: 'meals', label: 'Meals', icon: 'meal' },
  { id: 'workout', label: 'Workout', icon: 'workout' },
  { id: 'progress', label: 'Progress', icon: 'progress' },
  { id: 'coach', label: 'Coach', icon: 'coach' },
];
// which screen belongs to which tab (for active highlight)
const SCREEN_TAB = {
  home: 'home', missions: 'home', weight: 'home', 'weight-entry': 'home',
  meals: 'meals', 'meal-camera': 'meals', 'meal-analyzing': 'meals', 'meal-analysis': 'meals', 'meal-detail': 'meals',
  workout: 'workout', 'workout-active': 'workout', 'exercise-detail': 'workout', 'workout-summary': 'workout',
  progress: 'progress',
  coach: 'coach', 'coach-chat': 'coach',
  reminders: 'home', settings: 'home',
};
// screens that hide the bottom nav (full-bleed flows)
const FULLBLEED = new Set(['meal-camera', 'meal-analyzing', 'onboarding', 'celebrate', 'workout-active', 'coach-chat']);

function MobileTopBar({ title, onBack, right, sub, sticky = true }) {
  return (
    <div style={{
      height: 52, display: 'flex', alignItems: 'center', gap: 10, padding: '0 12px',
      background: 'var(--paper)', borderBottom: '1px solid var(--line)',
      position: sticky ? 'sticky' : 'relative', top: 0, zIndex: 20, flexShrink: 0,
    }}>
      {onBack && (
        <button onClick={onBack} className="focusable" style={{ width: 38, height: 38, borderRadius: 'var(--r-md)',
          border: '1px solid var(--line-2)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
          <Icon name="back" size={18} />
        </button>
      )}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 16, fontWeight: 700, letterSpacing: -0.2, color: 'var(--ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{title}</div>
        {sub && <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 1 }}>{sub}</div>}
      </div>
      {right}
    </div>
  );
}

function MobileBottomNav({ active, onTab }) {
  return (
    <div style={{
      flexShrink: 0, background: 'var(--card)', borderTop: '1px solid var(--line)',
      paddingBottom: 18, position: 'relative', zIndex: 30,
    }}>
      <div style={{ display: 'flex', height: 58 }}>
        {MOBILE_TABS.map(t => {
          const on = active === t.id;
          return (
            <button key={t.id} onClick={() => onTab(t.id)} className="focusable" style={{
              flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 4,
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
            }}>
              <Icon name={t.icon} size={21} color={on ? 'var(--ink)' : 'var(--ink-4)'} stroke={on ? 2 : 1.6}
                fill={false} />
              <span style={{ fontFamily: 'var(--mono)', fontSize: 9.5, fontWeight: on ? 700 : 500,
                color: on ? 'var(--ink)' : 'var(--ink-4)', letterSpacing: 0.02 }}>{t.label}</span>
            </button>
          );
        })}
      </div>
      {/* home indicator */}
      <div style={{ position: 'absolute', bottom: 7, left: '50%', transform: 'translateX(-50%)',
        width: 134, height: 5, borderRadius: 999, background: 'var(--ink)', opacity: 0.22 }} />
    </div>
  );
}

/* Scrollable content area for a standard screen */
function ScreenBody({ children, pad = 16, gap = 14, style = {} }) {
  return (
    <div className="bo-scroll" style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden',
      display: 'flex', flexDirection: 'column', gap, padding: pad, ...style }}>
      {children}
    </div>
  );
}

/* The router. Manages a nav stack; passes nav helpers to screens. */
function MobileApp({ initial = 'home', initialParams = {}, onNavChange }) {
  const [stack, setStack] = React.useState([{ screen: initial, params: initialParams }]);
  const cur = stack[stack.length - 1];

  const nav = React.useMemo(() => ({
    go: (screen, params = {}) => setStack(s => [...s, { screen, params }]),
    replace: (screen, params = {}) => setStack(s => [...s.slice(0, -1), { screen, params }]),
    back: () => setStack(s => s.length > 1 ? s.slice(0, -1) : s),
    tab: (tabId) => setStack([{ screen: tabId, params: {} }]),
    reset: (screen, params = {}) => setStack([{ screen, params }]),
    depth: stack.length,
  }), [stack.length]);

  React.useEffect(() => { onNavChange && onNavChange(cur); }, [cur.screen]);

  const Screens = window.MSCREENS || {};
  const Comp = Screens[cur.screen] || (() => <div style={{ padding: 24, fontFamily: 'var(--mono)' }}>Missing screen: {cur.screen}</div>);
  const showNav = !FULLBLEED.has(cur.screen);
  const activeTab = SCREEN_TAB[cur.screen] || 'home';

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, background: 'var(--paper)' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <Comp nav={nav} params={cur.params} D={window.DATA} />
      </div>
      {showNav && <MobileBottomNav active={activeTab} onTab={nav.tab} />}
    </div>
  );
}

Object.assign(window, { MOBILE_TABS, SCREEN_TAB, FULLBLEED, MobileTopBar, MobileBottomNav, ScreenBody, MobileApp });
window.MSCREENS = window.MSCREENS || {};
