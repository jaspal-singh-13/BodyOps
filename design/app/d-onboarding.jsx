/* BodyOps · Desktop — Onboarding wizard (full-screen, two-pane) */

function OnboardingDesktop({ D, onDone }) {
  const [step, setStep] = React.useState(0);
  const steps = [
    { k: 'welcome', label: 'Welcome' },
    { k: 'goal', label: 'Your goal' },
    { k: 'current', label: 'Current weight' },
    { k: 'target', label: 'Goal weight' },
    { k: 'activity', label: 'Activity level' },
    { k: 'frequency', label: 'Training' },
    { k: 'reminders', label: 'Reminders' },
  ];
  const [d, setD] = React.useState({ goalW: 77, curW: 107, activity: 'Moderate', freq: 5, goal: 'Lose fat', reminders: ['Weigh-in', 'Workout', 'Protein'] });
  const set = (k, v) => setD(x => ({ ...x, [k]: v }));
  const cur = steps[step].k;
  const next = () => step < steps.length - 1 ? setStep(step + 1) : (onDone && onDone());

  return (
    <div style={{ height: '100%', display: 'flex', background: 'var(--paper)' }}>
      {/* left rail */}
      <div style={{ width: 300, flexShrink: 0, background: 'var(--fill-ink)', padding: '32px 28px', display: 'flex', flexDirection: 'column', color: '#fff' }}>
        <Row gap={10}><div style={{ width: 32, height: 32, borderRadius: 9, background: 'rgba(255,255,255,0.14)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="bolt" size={18} color="#fff" /></div><div style={{ fontSize: 17, fontWeight: 800 }}>BodyOps</div></Row>
        <div style={{ marginTop: 40, fontSize: 22, fontWeight: 800, letterSpacing: -0.4, lineHeight: 1.25 }}>Let's build your<br />operating system.</div>
        <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', marginTop: 12, lineHeight: 1.55 }}>Six quick questions. Takes about 90 seconds — then your dashboard is ready.</div>
        <div style={{ marginTop: 40, display: 'flex', flexDirection: 'column', gap: 4 }}>
          {steps.slice(1).map((s, i) => {
            const idx = i + 1, done = idx < step, on = idx === step;
            return (
              <div key={s.k} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '9px 0', opacity: idx > step ? 0.45 : 1 }}>
                <div style={{ width: 26, height: 26, borderRadius: 999, border: '1.5px solid ' + (on || done ? '#fff' : 'rgba(255,255,255,0.4)'), background: done ? '#fff' : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {done ? <Icon name="check" size={13} color="var(--ink)" stroke={2.6} /> : <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, color: '#fff' }}>{idx}</span>}
                </div>
                <span style={{ fontSize: 13, fontWeight: on ? 700 : 500 }}>{s.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <div className="bo-scroll" style={{ flex: 1, overflowY: 'auto', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40 }}>
          <div style={{ width: '100%', maxWidth: 460 }}>
            {cur === 'welcome' && (
              <div style={{ textAlign: 'center' }}>
                <div style={{ width: 72, height: 72, borderRadius: 20, background: 'var(--fill-ink)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 22px' }}><Icon name="bolt" size={36} color="#fff" /></div>
                <div style={{ fontSize: 30, fontWeight: 800, letterSpacing: -0.6 }}>Welcome to BodyOps</div>
                <div style={{ fontSize: 15, color: 'var(--ink-2)', lineHeight: 1.55, marginTop: 12 }}>Your AI accountability system for reaching a target weight — meal photos, progressive overload, daily missions, and a coach that keeps you honest.</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginTop: 28 }}>
                  {[['camera', 'Snap meals'], ['trend', 'Smart overload'], ['coach', 'AI coach']].map(([ic, t]) => (
                    <div key={t} style={{ padding: 16, border: '1px solid var(--line)', borderRadius: 'var(--r-md)', background: 'var(--card)' }}>
                      <Icon name={ic} size={20} /><div style={{ fontSize: 12, fontWeight: 600, marginTop: 9 }}>{t}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {cur === 'goal' && <OnbStepD eyebrow="Your goal" title="What are you here to do?">
              <Col gap={11}>
                {[['Lose fat', 'Reach a lower target weight', 'arrowD'],['Build muscle', 'Gain lean mass', 'arrowU'],['Recomp', 'Lose fat & build muscle', 'target']].map(([t, s, ic]) =>
                  <SelectCard key={t} title={t} sub={s} icon={ic} active={d.goal === t} onClick={() => set('goal', t)} />)}
              </Col>
            </OnbStepD>}
            {cur === 'current' && <OnbStepD eyebrow="Starting point" title="What's your current weight?">
              <BigNumberPicker value={d.curW} unit="kg" onChange={v => set('curW', v)} min={50} max={180} />
              <Row gap={12} style={{ marginTop: 22 }}><Field label="Height" value="182" suffix="cm" /><Field label="Age" value="30" suffix="yrs" /><Field label="Sex" value="Male" /></Row>
            </OnbStepD>}
            {cur === 'target' && <OnbStepD eyebrow="Destination" title="What's your goal weight?">
              <BigNumberPicker value={d.goalW} unit="kg" onChange={v => set('goalW', v)} min={50} max={180} />
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 22 }}>
                <Card pad={14} style={{ background: 'var(--card-2)' }}><Eyebrow>To lose</Eyebrow><div style={{ fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 700, marginTop: 6 }}>{d.curW - d.goalW} kg</div></Card>
                <Card pad={14} style={{ background: 'var(--card-2)' }}><Eyebrow>Est. timeline</Eyebrow><div style={{ fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 700, marginTop: 6 }}>~{Math.round((d.curW - d.goalW) / 1.2)} wks</div></Card>
              </div>
            </OnbStepD>}
            {cur === 'activity' && <OnbStepD eyebrow="Daily activity" title="How active is your day?">
              <Col gap={11}>{[['Sedentary', 'Desk job, little movement'],['Light', 'Some walking daily'],['Moderate', 'On my feet often'],['Very active', 'Physical job']].map(([t, s]) => <SelectCard key={t} title={t} sub={s} active={d.activity === t} onClick={() => set('activity', t)} />)}</Col>
            </OnbStepD>}
            {cur === 'frequency' && <OnbStepD eyebrow="Training" title="How often will you train?">
              <div style={{ textAlign: 'center', margin: '6px 0 22px' }}><div style={{ fontFamily: 'var(--mono)', fontSize: 60, fontWeight: 700 }}>{d.freq}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ink-3)' }}>days per week</div></div>
              <div style={{ display: 'flex', gap: 9, justifyContent: 'center' }}>{[2,3,4,5,6,7].map(n => <button key={n} onClick={() => set('freq', n)} style={{ width: 52, height: 52, borderRadius: 'var(--r-md)', border: '1.5px solid ' + (d.freq === n ? 'var(--ink)' : 'var(--line-2)'), background: d.freq === n ? 'var(--fill-ink)' : 'var(--card)', color: d.freq === n ? '#fff' : 'var(--ink)', fontFamily: 'var(--mono)', fontSize: 18, fontWeight: 700, cursor: 'pointer' }}>{n}</button>)}</div>
              <Card pad={14} style={{ marginTop: 22, background: 'var(--card-2)' }}><Row gap={9}><Icon name="info" size={16} /><span style={{ fontSize: 13, color: 'var(--ink-2)' }}>At {d.freq} days we'll set up a <b>Push / Pull / Legs</b> split with built-in progressive overload.</span></Row></Card>
            </OnbStepD>}
            {cur === 'reminders' && <OnbStepD eyebrow="Stay accountable" title="When should we nudge you?">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {[['Weigh-in', '07:00 daily', 'weight'],['Protein', '15:00 daily', 'meal'],['Workout', '18:00 Mon–Sat', 'workout'],['Wind down', '23:00 daily', 'moon']].map(([t, time, ic]) => {
                  const on = d.reminders.includes(t);
                  return <Card key={t} pad={14} flat onClick={() => set('reminders', on ? d.reminders.filter(x => x !== t) : [...d.reminders, t])} style={{ borderColor: on ? 'var(--line-3)' : 'var(--line)', cursor: 'pointer' }}>
                    <Row justify="space-between"><div style={{ width: 34, height: 34, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name={ic} size={17} color="var(--ink-2)" /></div><Toggle on={on} /></Row>
                    <div style={{ fontSize: 13.5, fontWeight: 700, marginTop: 11 }}>{t}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>{time}</div>
                  </Card>;
                })}
              </div>
            </OnbStepD>}
          </div>
        </div>
        {/* footer */}
        <div style={{ flexShrink: 0, height: 76, borderTop: '1px solid var(--line)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 30px' }}>
          <button onClick={() => setStep(Math.max(0, step - 1))} style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'var(--sans)', fontSize: 13.5, fontWeight: 600, color: 'var(--ink-3)', display: 'flex', alignItems: 'center', gap: 6 }}><Icon name="back" size={16} /> Back</button>
          <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}>{step === 0 ? '' : `Step ${step} of ${steps.length - 1}`}</span>
          <Btn size="md" iconRight={step === steps.length - 1 ? 'check' : 'chevR'} onClick={next}>{step === 0 ? 'Get started' : step === steps.length - 1 ? 'Finish & open dashboard' : 'Continue'}</Btn>
        </div>
      </div>
    </div>
  );
}

function OnbStepD({ eyebrow, title, children }) {
  return (
    <div>
      <Eyebrow>{eyebrow}</Eyebrow>
      <div style={{ fontSize: 27, fontWeight: 800, letterSpacing: -0.5, marginTop: 8 }}>{title}</div>
      <div style={{ marginTop: 26 }}>{children}</div>
    </div>
  );
}

Object.assign(window, { OnboardingDesktop, OnbStepD });
