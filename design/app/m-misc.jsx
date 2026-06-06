/* BodyOps · Mobile — Onboarding, Reminders, Settings, Empty + Success states */

/* ═══════════════ ONBOARDING (self-contained multi-step) ═══════════════ */
function OnboardingScreen({ nav, D }) {
  const [step, setStep] = React.useState(0);
  const [data, setData] = React.useState({ goalW: 77, curW: 107, activity: 'Moderate', freq: 5, reminders: ['Weigh-in', 'Workout', 'Protein'] });
  const steps = ['welcome', 'goal', 'current', 'target', 'activity', 'frequency', 'reminders'];
  const next = () => step < steps.length - 1 ? setStep(step + 1) : nav.reset('home');
  const back = () => step > 0 ? setStep(step - 1) : nav.reset('home');
  const cur = steps[step];

  const set = (k, v) => setData(d => ({ ...d, [k]: v }));
  const toggleRem = (r) => set('reminders', data.reminders.includes(r) ? data.reminders.filter(x => x !== r) : [...data.reminders, r]);

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--paper)', minHeight: 0 }}>
      {/* progress header */}
      <div style={{ flexShrink: 0, padding: '14px 16px 0' }}>
        <Row justify="space-between" align="center">
          <button onClick={back} style={{ width: 36, height: 36, borderRadius: 'var(--r-md)', border: '1px solid var(--line-2)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="back" size={17} /></button>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', fontWeight: 600 }}>{step === 0 ? 'WELCOME' : `STEP ${step} OF ${steps.length - 1}`}</span>
          <button onClick={() => nav.reset('home')} style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', background: 'none', border: 'none', cursor: 'pointer' }}>Skip</button>
        </Row>
        {step > 0 && <div style={{ display: 'flex', gap: 4, marginTop: 14 }}>
          {steps.slice(1).map((_, i) => <div key={i} style={{ flex: 1, height: 4, borderRadius: 999, background: i < step ? 'var(--ink)' : 'var(--fill-2)' }} />)}
        </div>}
      </div>

      <div className="bo-scroll" style={{ flex: 1, overflowY: 'auto', padding: '24px 20px', display: 'flex', flexDirection: 'column' }}>
        {cur === 'welcome' && (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', textAlign: 'center', gap: 22 }}>
            <div style={{ width: 72, height: 72, borderRadius: 20, background: 'var(--fill-ink)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto' }}>
              <Icon name="bolt" size={36} color="#fff" /></div>
            <div>
              <div style={{ fontSize: 30, fontWeight: 800, letterSpacing: -0.8 }}>BodyOps</div>
              <div style={{ fontSize: 15, color: 'var(--ink-2)', lineHeight: 1.5, marginTop: 12, maxWidth: 280, margin: '12px auto 0' }}>Your AI accountability system for reaching a target weight — without the manual data entry.</div>
            </div>
            <Col gap={10} style={{ marginTop: 8 }}>
              {[['camera', 'Snap meals, AI does the macros'], ['trend', 'Progressive overload that adapts'], ['coach', 'A coach that keeps you honest']].map(([ic, t]) => (
                <Row key={t} gap={11} style={{ textAlign: 'left' }}>
                  <div style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', background: 'var(--card)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}><Icon name={ic} size={18} /></div>
                  <span style={{ fontSize: 13.5, fontWeight: 500 }}>{t}</span>
                </Row>
              ))}
            </Col>
          </div>
        )}

        {cur === 'goal' && <OnbStep eyebrow="Your goal" title="What are you here to do?" sub="We'll tailor the whole system around it.">
          <Col gap={10}>
            {[['Lose fat', 'Reach a lower target weight', true], ['Build muscle', 'Gain lean mass', false], ['Maintain', 'Stay where I am, get healthier', false]].map(([t, s, on]) => (
              <SelectCard key={t} title={t} sub={s} active={on} icon={t === 'Lose fat' ? 'arrowD' : t === 'Build muscle' ? 'arrowU' : 'target'} />
            ))}
          </Col>
        </OnbStep>}

        {cur === 'current' && <OnbStep eyebrow="Starting point" title="What's your current weight?" sub="Be honest — this is your baseline, not a judgment.">
          <BigNumberPicker value={data.curW} unit="kg" onChange={v => set('curW', v)} min={50} max={180} />
          <Row gap={10} style={{ marginTop: 18 }}>
            <Field label="Height" value="182" suffix="cm" />
            <Field label="Age" value="30" suffix="yrs" />
          </Row>
        </OnbStep>}

        {cur === 'target' && <OnbStep eyebrow="Destination" title="What's your goal weight?" sub="We'll build a realistic 6-month path to get there.">
          <BigNumberPicker value={data.goalW} unit="kg" onChange={v => set('goalW', v)} min={50} max={180} />
          <Card pad={14} style={{ marginTop: 18, background: 'var(--card-2)' }}>
            <Row justify="space-between"><span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}>TO LOSE</span><span style={{ fontFamily: 'var(--mono)', fontSize: 15, fontWeight: 700 }}>{data.curW - data.goalW} kg</span></Row>
            <Divider style={{ margin: '11px 0' }} />
            <Row justify="space-between"><span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}>EST. TIMELINE</span><span style={{ fontFamily: 'var(--mono)', fontSize: 15, fontWeight: 700 }}>~{Math.round((data.curW - data.goalW) / 1.2)} weeks</span></Row>
          </Card>
        </OnbStep>}

        {cur === 'activity' && <OnbStep eyebrow="Daily activity" title="How active is your day?" sub="Outside of training — this sets your calorie baseline.">
          <Col gap={10}>
            {[['Sedentary', 'Desk job, little movement'], ['Light', 'Some walking daily'], ['Moderate', 'On my feet often'], ['Very active', 'Physical job']].map(([t, s]) => (
              <SelectCard key={t} title={t} sub={s} active={data.activity === t} onClick={() => set('activity', t)} />
            ))}
          </Col>
        </OnbStep>}

        {cur === 'frequency' && <OnbStep eyebrow="Training" title="How often do you train?" sub="We'll build your split around this.">
          <div style={{ textAlign: 'center', margin: '10px 0 18px' }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 56, fontWeight: 700 }}>{data.freq}</div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ink-3)' }}>days per week</div>
          </div>
          <div style={{ display: 'flex', gap: 7, justifyContent: 'center' }}>
            {[2,3,4,5,6,7].map(n => (
              <button key={n} onClick={() => set('freq', n)} style={{ width: 44, height: 44, borderRadius: 'var(--r-md)', border: '1.5px solid ' + (data.freq === n ? 'var(--ink)' : 'var(--line-2)'), background: data.freq === n ? 'var(--fill-ink)' : 'var(--card)', color: data.freq === n ? '#fff' : 'var(--ink)', fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 700, cursor: 'pointer' }}>{n}</button>
            ))}
          </div>
          <Card pad={13} style={{ marginTop: 18, background: 'var(--card-2)' }}>
            <Row gap={9}><Icon name="info" size={15} /><span style={{ fontSize: 12.5, color: 'var(--ink-2)' }}>At {data.freq} days we'll set up a <b>Push / Pull / Legs</b> split.</span></Row>
          </Card>
        </OnbStep>}

        {cur === 'reminders' && <OnbStep eyebrow="Stay accountable" title="When should we nudge you?" sub="Turn on the reminders that'll keep you consistent.">
          <Col gap={10}>
            {[['Weigh-in', '07:00 daily', 'weight'], ['Protein', '15:00 daily', 'meal'], ['Workout', '18:00 Mon–Sat', 'workout'], ['Wind down', '23:00 daily', 'moon']].map(([t, time, ic]) => {
              const on = data.reminders.includes(t);
              return (
                <Card key={t} pad={13} flat onClick={() => toggleRem(t)} style={{ borderColor: on ? 'var(--line-3)' : 'var(--line)' }}>
                  <Row gap={12}>
                    <div style={{ width: 36, height: 36, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name={ic} size={18} color="var(--ink-2)" /></div>
                    <div style={{ flex: 1 }}><div style={{ fontSize: 14, fontWeight: 600 }}>{t}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>{time}</div></div>
                    <Toggle on={on} />
                  </Row>
                </Card>
              );
            })}
          </Col>
        </OnbStep>}
      </div>

      {/* footer */}
      <div style={{ flexShrink: 0, padding: '12px 20px 24px', borderTop: step === 0 ? 'none' : '1px solid var(--line)' }}>
        <Btn full size="lg" iconRight={step === steps.length - 1 ? 'check' : 'chevR'} onClick={next}>
          {step === 0 ? 'Get started' : step === steps.length - 1 ? 'Finish setup' : 'Continue'}
        </Btn>
      </div>
    </div>
  );
}

function OnbStep({ eyebrow, title, sub, children }) {
  return (
    <div>
      <Eyebrow>{eyebrow}</Eyebrow>
      <div style={{ fontSize: 25, fontWeight: 800, letterSpacing: -0.5, marginTop: 8, lineHeight: 1.15 }}>{title}</div>
      {sub && <div style={{ fontSize: 13.5, color: 'var(--ink-2)', marginTop: 8, lineHeight: 1.5 }}>{sub}</div>}
      <div style={{ marginTop: 22 }}>{children}</div>
    </div>
  );
}
function SelectCard({ title, sub, active, icon, onClick }) {
  return (
    <Card pad={14} flat onClick={onClick} style={{ borderColor: active ? 'var(--ink)' : 'var(--line-2)', borderWidth: active ? 1.5 : 1 }}>
      <Row gap={12}>
        {icon && <div style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', background: active ? 'var(--fill-ink)' : 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}><Icon name={icon} size={18} color={active ? '#fff' : 'var(--ink-2)'} /></div>}
        <div style={{ flex: 1 }}><div style={{ fontSize: 14.5, fontWeight: 700 }}>{title}</div><div style={{ fontSize: 12, color: 'var(--ink-3)', marginTop: 1 }}>{sub}</div></div>
        <div style={{ width: 22, height: 22, borderRadius: 999, border: '1.5px solid ' + (active ? 'var(--ink)' : 'var(--line-3)'), background: active ? 'var(--ink)' : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{active && <Icon name="check" size={13} color="#fff" stroke={2.6} />}</div>
      </Row>
    </Card>
  );
}
function BigNumberPicker({ value, unit, onChange, min, max }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 18 }}>
        <button onClick={() => onChange(Math.max(min, value - 1))} style={{ width: 46, height: 46, borderRadius: 999, border: '1px solid var(--line-2)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="chevD" size={20} style={{ transform: 'rotate(90deg)' }} /></button>
        <div style={{ textAlign: 'center', minWidth: 130 }}>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 56, fontWeight: 700, letterSpacing: -1 }}>{value}</span>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 18, color: 'var(--ink-3)', marginLeft: 4 }}>{unit}</span>
        </div>
        <button onClick={() => onChange(Math.min(max, value + 1))} style={{ width: 46, height: 46, borderRadius: 999, border: '1px solid var(--line-2)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="chevD" size={20} style={{ transform: 'rotate(-90deg)' }} /></button>
      </div>
      {/* ruler */}
      <div style={{ marginTop: 18, height: 40, position: 'relative', overflow: 'hidden', maskImage: 'linear-gradient(90deg, transparent, #000 20%, #000 80%, transparent)' }}>
        <div style={{ display: 'flex', gap: 0, alignItems: 'flex-end', justifyContent: 'center', height: '100%' }}>
          {Array.from({ length: 31 }).map((_, i) => {
            const major = (i % 5) === 0;
            return <div key={i} style={{ width: 9, height: major ? 26 : 14, borderLeft: '1.5px solid ' + (i === 15 ? 'var(--ink)' : 'var(--line-2)') }} />;
          })}
        </div>
        <div style={{ position: 'absolute', bottom: 0, left: '50%', transform: 'translateX(-50%)', width: 2, height: 32, background: 'var(--ink)' }} />
      </div>
    </div>
  );
}

/* ═══════════════ REMINDERS ═══════════════ */
function RemindersScreen({ nav, D }) {
  const [items, setItems] = React.useState(D.reminders);
  const toggle = (id) => setItems(items.map(r => r.id === id ? { ...r, on: !r.on } : r));
  return (
    <>
      <MobileTopBar title="Reminders" onBack={() => nav.back()} sub={`${items.filter(r => r.on).length} active`} />
      <ScreenBody pad={14} gap={13}>
        <Card pad={14} style={{ background: 'var(--card-2)' }}>
          <Row gap={10}><Icon name="bell" size={17} /><span style={{ fontSize: 12.5, color: 'var(--ink-2)', lineHeight: 1.45, flex: 1 }}>Smart reminders fire only when you haven't logged. We'll never spam you.</span></Row>
        </Card>
        <Col gap={9}>
          {items.map(r => (
            <Card key={r.id} pad={14} flat>
              <Row gap={12}>
                <div style={{ width: 40, height: 40, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}><Icon name={r.icon} size={19} color="var(--ink-2)" /></div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 700 }}>{r.label}</div>
                  <Row gap={6} style={{ marginTop: 3 }}>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 600, color: 'var(--ink)' }}>{r.time}</span>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}>· {r.days}</span>
                  </Row>
                </div>
                <Toggle on={r.on} onClick={() => toggle(r.id)} />
              </Row>
              {r.on && <Row gap={8} style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--line)' }}>
                <button style={{ flex: 1, height: 34, borderRadius: 'var(--r-sm)', border: '1px solid var(--line-2)', background: 'var(--card)', fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}><Icon name="clock" size={13} /> Edit time</button>
                <button style={{ flex: 1, height: 34, borderRadius: 'var(--r-sm)', border: '1px solid var(--line-2)', background: 'var(--card)', fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}><Icon name="cal" size={13} /> Days</button>
              </Row>}
            </Card>
          ))}
        </Col>
        <button style={{ height: 48, borderRadius: 'var(--r-md)', border: '1.5px dashed var(--line-3)', background: 'transparent', fontFamily: 'var(--sans)', fontSize: 13.5, fontWeight: 600, color: 'var(--ink-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7, cursor: 'pointer' }}><Icon name="plus" size={16} /> Add reminder</button>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}
function Toggle({ on, onClick }) {
  return (
    <button onClick={onClick} style={{ width: 46, height: 28, borderRadius: 999, border: 'none', cursor: 'pointer', padding: 3, background: on ? 'var(--fill-ink)' : 'var(--fill-2)', display: 'flex', justifyContent: on ? 'flex-end' : 'flex-start', transition: 'all .15s', flexShrink: 0 }}>
      <div style={{ width: 22, height: 22, borderRadius: 999, background: '#fff', boxShadow: 'var(--sh-1)' }} />
    </button>
  );
}

/* ═══════════════ SETTINGS ═══════════════ */
function SettingsScreen({ nav, D }) {
  const groups = [
    { h: 'Account', rows: [['user', 'Profile', 'Alex Chen'], ['target', 'Goals & targets', '77 kg'], ['scale', 'Units', 'Metric · kg']] },
    { h: 'Coaching', rows: [['bell', 'Reminders', '4 active', 'reminders'], ['coach', 'Coach style', 'Direct'], ['workout', 'Training split', 'PPL · 6 day']] },
    { h: 'Data', rows: [['link', 'Connected services', 'Apple Health'], ['download', 'Export my data', 'CSV · PDF'], ['info', 'Privacy', '']] },
  ];
  return (
    <>
      <MobileTopBar title="Settings" onBack={() => nav.back()} />
      <ScreenBody pad={14} gap={16}>
        {/* profile */}
        <Card pad={16}>
          <Row gap={13}>
            <Avatar initials={D.user.initials} size={52} ring />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 17, fontWeight: 800 }}>{D.user.name}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', marginTop: 2 }}>{D.user.job} · {D.user.age} yrs</div>
            </div>
            <Tag><Icon name="bolt" size={10} fill color="var(--ink)" /> Day {D.user.dayN}</Tag>
          </Row>
        </Card>
        {groups.map(g => (
          <div key={g.h}>
            <Eyebrow style={{ paddingLeft: 4, marginBottom: 8 }}>{g.h}</Eyebrow>
            <Card pad={0} flat>
              {g.rows.map(([ic, label, val, dest], i) => (
                <div key={label} onClick={() => dest && nav.go(dest)} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '13px 14px', borderBottom: i < g.rows.length - 1 ? '1px solid var(--line)' : 'none', cursor: dest ? 'pointer' : 'default' }}>
                  <Icon name={ic} size={18} color="var(--ink-2)" />
                  <span style={{ flex: 1, fontSize: 14, fontWeight: 500 }}>{label}</span>
                  {val && <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}>{val}</span>}
                  <Icon name="chevR" size={15} color="var(--ink-4)" />
                </div>
              ))}
            </Card>
          </div>
        ))}
        <button onClick={() => nav.reset('onboarding')} style={{ height: 46, borderRadius: 'var(--r-md)', border: '1px solid var(--line-2)', background: 'var(--card)', fontFamily: 'var(--sans)', fontSize: 13.5, fontWeight: 600, color: 'var(--ink-2)', cursor: 'pointer' }}>Replay onboarding</button>
        <div style={{ textAlign: 'center', fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-4)' }}>BodyOps · v1.0.0 · build 240</div>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

/* ═══════════════ EMPTY STATE (reusable) ═══════════════ */
function EmptyState({ icon, title, body, cta, onCta, secondary }) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 30, gap: 6 }}>
      <div style={{ width: 64, height: 64, borderRadius: 18, background: 'var(--card)', border: '1.5px dashed var(--line-3)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 10 }}>
        <Icon name={icon} size={28} color="var(--ink-3)" /></div>
      <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: -0.3 }}>{title}</div>
      <div style={{ fontSize: 13.5, color: 'var(--ink-2)', lineHeight: 1.5, maxWidth: 250, marginTop: 4 }}>{body}</div>
      {cta && <Btn size="md" icon="plus" onClick={onCta} style={{ marginTop: 16 }}>{cta}</Btn>}
      {secondary && <button style={{ marginTop: 4, background: 'none', border: 'none', fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--ink-3)', cursor: 'pointer' }}>{secondary}</button>}
    </div>
  );
}
function EmptyMeals({ nav }) {
  return (<>
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px 8px', flexShrink: 0 }}>
      <div><Eyebrow>Nutrition</Eyebrow><div style={{ fontSize: 21, fontWeight: 800, marginTop: 2 }}>Meals</div></div>
      <button onClick={() => nav && nav.go('meal-camera')} style={{ width: 42, height: 42, borderRadius: 'var(--r-md)', background: 'var(--fill-ink)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="camera" size={21} color="#fff" /></button>
    </div>
    <EmptyState icon="meal" title="No meals yet today" body="Snap a photo of your first meal — the AI handles calories and macros for you." cta="Log your first meal" onCta={() => nav && nav.go('meal-camera')} secondary="Or add manually" />
  </>);
}

/* ═══════════════ SUCCESS / CELEBRATION (full-bleed) ═══════════════ */
function CelebrateScreen({ nav, D }) {
  const c = D.celebrate;
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--fill-ink)', minHeight: 0, color: '#fff' }}>
      <div style={{ flexShrink: 0, padding: '14px 16px' }}>
        <button onClick={() => nav.back()} style={{ width: 36, height: 36, borderRadius: 999, background: 'rgba(255,255,255,0.14)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="x" size={18} color="#fff" /></button>
      </div>
      <div className="bo-scroll" style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 28, gap: 8 }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.55)', fontWeight: 600, letterSpacing: 0.1, textTransform: 'uppercase' }}>Milestone unlocked</div>
        <div style={{ position: 'relative', margin: '14px 0' }}>
          <div style={{ width: 130, height: 130, borderRadius: 999, border: '2px solid rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ width: 100, height: 100, borderRadius: 999, background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 34, fontWeight: 700 }}>{c.big}</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.6)', letterSpacing: 0.06 }}>LOST</span>
            </div>
          </div>
          <div style={{ position: 'absolute', top: -6, right: -6, width: 38, height: 38, borderRadius: 999, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="trophy" size={20} color="var(--ink)" /></div>
        </div>
        <div style={{ fontSize: 26, fontWeight: 800, letterSpacing: -0.5 }}>{c.title}</div>
        <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.78)', lineHeight: 1.55, maxWidth: 290, marginTop: 6 }}>{c.body}</div>
        <Row gap={0} style={{ marginTop: 24, width: '100%', maxWidth: 300 }}>
          {[[c.stat1.v, c.stat1.l], [c.stat2.v, c.stat2.l]].map(([v, l], i) => (
            <React.Fragment key={i}>
              {i > 0 && <div style={{ width: 1, background: 'rgba(255,255,255,0.16)', alignSelf: 'stretch' }} />}
              <div style={{ flex: 1 }}><div style={{ fontFamily: 'var(--mono)', fontSize: 20, fontWeight: 700 }}>{v}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.5)', marginTop: 3 }}>{l}</div></div>
            </React.Fragment>
          ))}
        </Row>
        <Card pad={13} style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.12)', marginTop: 22, width: '100%', maxWidth: 300 }}>
          <Row justify="space-between"><Row gap={9}><Icon name="target" size={16} color="#fff" /><span style={{ fontSize: 12.5, color: '#fff', fontWeight: 600 }}>{c.next}</span></Row>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.6)' }}>{c.nextMeta}</span></Row>
        </Card>
      </div>
      <div style={{ flexShrink: 0, padding: '12px 20px 28px', display: 'flex', gap: 10 }}>
        <Btn size="lg" icon="share" variant="secondary" style={{ background: 'rgba(255,255,255,0.12)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)', width: 56, padding: 0 }}> </Btn>
        <Btn full size="lg" style={{ background: '#fff', color: 'var(--ink)', border: 'none' }} onClick={() => nav.reset('home')}>Keep going</Btn>
      </div>
    </div>
  );
}

window.MSCREENS = Object.assign(window.MSCREENS || {}, {
  onboarding: OnboardingScreen, reminders: RemindersScreen, settings: SettingsScreen,
  celebrate: CelebrateScreen, 'empty-meals': EmptyMeals,
});
Object.assign(window, { OnboardingScreen, EmptyState, EmptyMeals, Toggle, SelectCard });
