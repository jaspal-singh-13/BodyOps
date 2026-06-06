/* BodyOps · Mobile — Home dashboard + Daily Missions */

function HomeScreen({ nav, D }) {
  const g = D.goal, n = D.nutrition;
  const pct = Math.round((g.lost / 30) * 100);
  return (
    <>
      {/* header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px 6px', flexShrink: 0 }}>
        <div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', fontWeight: 600, letterSpacing: 0.06 }}>FRI · JUN 6 · DAY {D.user.dayN}</div>
          <div style={{ fontSize: 20, fontWeight: 800, letterSpacing: -0.4, marginTop: 2, whiteSpace: 'nowrap' }}>Good morning, Alex</div>
        </div>
        <button onClick={() => nav.go('settings')} style={{ border: 'none', background: 'none', cursor: 'pointer', padding: 0 }}>
          <Avatar initials={D.user.initials} size={40} />
        </button>
      </div>

      <ScreenBody pad={14} gap={13} style={{ paddingTop: 8 }}>
        {/* HERO — progress to goal */}
        <Card pad={16} elevated style={{ background: 'var(--fill-ink)', border: 'none' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.55)', fontWeight: 600, letterSpacing: 0.08, textTransform: 'uppercase' }}>Current weight</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginTop: 4 }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 38, fontWeight: 700, color: '#fff', lineHeight: 1 }}>{g.current}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 15, color: 'rgba(255,255,255,0.6)' }}>kg</span>
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700,
                color: '#fff', background: 'rgba(255,255,255,0.14)', padding: '5px 9px', borderRadius: 999 }}>
                <Icon name="arrowD" size={12} color="#fff" /> {g.lost} kg lost
              </span>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'rgba(255,255,255,0.55)', marginTop: 8 }}>{g.remaining} kg to goal</div>
            </div>
          </div>
          {/* track */}
          <div style={{ marginTop: 16 }}>
            <div style={{ height: 9, background: 'rgba(255,255,255,0.16)', borderRadius: 999, overflow: 'hidden', position: 'relative' }}>
              <div style={{ width: `${pct}%`, height: '100%', background: '#fff', borderRadius: 999 }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontFamily: 'var(--mono)', fontSize: 10.5, color: 'rgba(255,255,255,0.6)' }}>
              <span>{g.start} kg start</span>
              <span style={{ color: '#fff', fontWeight: 700 }}>{pct}% there</span>
              <span>{g.goal} kg goal</span>
            </div>
          </div>
          {/* projection */}
          <div style={{ marginTop: 14, paddingTop: 13, borderTop: '1px solid rgba(255,255,255,0.12)', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Icon name="target" size={15} color="rgba(255,255,255,0.8)" />
            <span style={{ fontSize: 12.5, color: 'rgba(255,255,255,0.82)' }}>On pace for <b style={{ color: '#fff' }}>{g.projDate}</b> — {g.aheadDays} days early</span>
          </div>
        </Card>

        {/* QUICK ACTIONS */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <Card pad={0} onClick={() => nav.go('meal-camera')} style={{ overflow: 'hidden' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: 14 }}>
              <div style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', background: 'var(--fill-ink)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon name="camera" size={20} color="#fff" /></div>
              <div><div style={{ fontSize: 13.5, fontWeight: 700, whiteSpace: 'nowrap' }}>Log meal</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)' }}>Snap a photo</div></div>
            </div>
          </Card>
          <Card pad={0} onClick={() => nav.go('weight-entry')} style={{ overflow: 'hidden' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: 14 }}>
              <div style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon name="weight" size={20} /></div>
              <div><div style={{ fontSize: 13.5, fontWeight: 700, whiteSpace: 'nowrap' }}>Weigh in</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)' }}>Logged ✓</div></div>
            </div>
          </Card>
        </div>

        {/* MISSIONS strip */}
        <Card pad={15} onClick={() => nav.go('missions')}>
          <Row justify="space-between">
            <Row gap={8}>
              <Eyebrow>Today's missions</Eyebrow>
              <Tag><Icon name="flame" size={10} fill color="var(--ink)" /> {D.missionStats.streak}d streak</Tag>
            </Row>
            <Icon name="chevR" size={16} color="var(--ink-3)" />
          </Row>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 12 }}>
            <Ring value={Math.round((D.missionStats.done / D.missionStats.total) * 100)} size={52} stroke={6}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700 }}>{D.missionStats.done}/{D.missionStats.total}</span>
            </Ring>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 7 }}>
              {D.missions.slice(0, 3).map(m => (
                <div key={m.id} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <MissionCheck done={m.done} sm />
                  <span style={{ fontSize: 12.5, color: m.done ? 'var(--ink-3)' : 'var(--ink)', textDecoration: m.done ? 'line-through' : 'none', flex: 1 }}>{m.label}</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>{m.meta}</span>
                </div>
              ))}
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', paddingLeft: 26 }}>+4 more</div>
            </div>
          </div>
        </Card>

        {/* NUTRITION today */}
        <Card pad={15}>
          <Row justify="space-between">
            <Eyebrow>Today · Nutrition</Eyebrow>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>{D.mealsToday.length} meals logged</span>
          </Row>
          <div style={{ display: 'flex', gap: 10, marginTop: 14, alignItems: 'center' }}>
            <DonutStat value={n.cal.v} total={n.cal.target} label="kcal" size={104} stroke={10} />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 12 }}>
              <MacroLine label="Protein" v={n.protein.v} t={n.protein.target} unit="g" />
              <MacroLine label="Carbs" v={n.carbs.v} t={n.carbs.target} unit="g" />
              <MacroLine label="Fat" v={n.fat.v} t={n.fat.target} unit="g" />
            </div>
          </div>
        </Card>

        {/* WORKOUT status */}
        <Card pad={15} onClick={() => nav.go('workout')}>
          <Row justify="space-between" align="flex-start">
            <Row gap={11} align="flex-start">
              <div style={{ width: 42, height: 42, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon name="workout" size={22} /></div>
              <div>
                <Eyebrow>Today's workout</Eyebrow>
                <div style={{ fontSize: 15.5, fontWeight: 700, marginTop: 3 }}>{D.workout.today}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>{D.workout.exercisesN} exercises · {D.workout.duration}</div>
              </div>
            </Row>
            <Tag>Ready</Tag>
          </Row>
          <Btn full size="md" icon="play" style={{ marginTop: 13 }} onClick={(e) => { e.stopPropagation(); nav.go('workout'); }}>Start session</Btn>
        </Card>

        {/* COACH message */}
        <Card pad={15} onClick={() => nav.go('coach')} style={{ background: 'var(--card-2)' }}>
          <Row gap={11} align="flex-start">
            <CoachMark size={38} />
            <div style={{ flex: 1 }}>
              <Row justify="space-between"><Eyebrow>Coach</Eyebrow><Icon name="chevR" size={15} color="var(--ink-3)" /></Row>
              <div style={{ fontSize: 13.5, lineHeight: 1.5, marginTop: 6, color: 'var(--ink)' }}>
                You're <b>{D.goal.aheadDays} days ahead</b> of schedule. One gap today — protein. Grab a shake after the gym to close it.
              </div>
            </div>
          </Row>
        </Card>

        {/* WEEKLY progress */}
        <Card pad={15} onClick={() => nav.tab('progress')}>
          <Row justify="space-between">
            <Eyebrow>This week</Eyebrow>
            <Tag><Icon name="arrowD" size={10} /> 1.1 kg</Tag>
          </Row>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginTop: 10 }}>
            <div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 28, fontWeight: 700 }}>98.8<span style={{ fontSize: 14, color: 'var(--ink-3)' }}> kg</span></div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)', marginTop: 1 }}>7-day average</div>
            </div>
            <Sparkline data={D.weightWeekly.map(p => p.w)} width={150} height={44} />
          </div>
        </Card>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

function MacroLine({ label, v, t, unit }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--ink-2)' }}>{label}</span>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}><b style={{ color: 'var(--ink)' }}>{v}</b> / {t}{unit}</span>
      </div>
      <Bar value={(v / t) * 100} h={6} />
    </div>
  );
}

function MissionCheck({ done, sm, onClick }) {
  const s = sm ? 18 : 24;
  return (
    <button onClick={onClick} style={{ border: 'none', background: 'none', padding: 0, cursor: onClick ? 'pointer' : 'default', flexShrink: 0 }}>
      <div style={{ width: s, height: s, borderRadius: sm ? 6 : 8,
        border: done ? 'none' : '1.5px solid var(--line-3)', background: done ? 'var(--fill-ink)' : 'var(--card)',
        display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {done && <Icon name="check" size={sm ? 12 : 15} color="#fff" stroke={2.6} />}
      </div>
    </button>
  );
}

/* ───────────────────────── Daily Missions screen ─────────────────────────── */
function MissionsScreen({ nav, D }) {
  const [items, setItems] = React.useState(D.missions);
  const toggle = (id) => setItems(items.map(m => m.id === id ? { ...m, done: !m.done } : m));
  const doneN = items.filter(m => m.done).length;
  const pct = Math.round((doneN / items.length) * 100);
  return (
    <>
      <MobileTopBar title="Daily Missions" onBack={() => nav.back()} sub="Friday · June 6" />
      <ScreenBody pad={14} gap={13}>
        {/* progress header */}
        <Card pad={16}>
          <Row justify="space-between" align="center">
            <div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', fontWeight: 600 }}>COMPLETION</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 34, fontWeight: 700, marginTop: 2 }}>{pct}%</div>
              <div style={{ fontSize: 12.5, color: 'var(--ink-2)', marginTop: 2 }}>{doneN} of {items.length} done today</div>
            </div>
            <Ring value={pct} size={88} stroke={9}>
              <Icon name="flame" size={20} fill color="var(--ink)" />
              <span style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, marginTop: 2 }}>{D.missionStats.streak}d</span>
            </Ring>
          </Row>
          <div style={{ display: 'flex', gap: 18, marginTop: 14, paddingTop: 13, borderTop: '1px solid var(--line)' }}>
            <Stat label="Current streak" value={`${D.missionStats.streak} days`} />
            <Stat label="Best streak" value={`${D.missionStats.bestStreak} days`} />
            <Stat label="This week" value={`${D.missionStats.weekRate}%`} />
          </div>
        </Card>

        <Eyebrow style={{ paddingLeft: 4, marginTop: 2 }}>Today's checklist</Eyebrow>
        <Col gap={9}>
          {items.map(m => (
            <Card key={m.id} pad={13} onClick={() => toggle(m.id)} flat style={{ borderColor: m.done ? 'var(--line)' : 'var(--line-2)' }}>
              <Row gap={12}>
                <MissionCheck done={m.done} onClick={() => toggle(m.id)} />
                <div style={{ width: 34, height: 34, borderRadius: 'var(--r-sm)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon name={m.icon} size={17} color="var(--ink-2)" />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: m.done ? 'var(--ink-3)' : 'var(--ink)', textDecoration: m.done ? 'line-through' : 'none' }}>{m.label}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>{m.meta}</div>
                  {m.prog != null && !m.done && <Bar value={m.prog} h={4} style={{ marginTop: 7 }} />}
                </div>
                {m.onTrack && !m.done && <Tag>On track</Tag>}
              </Row>
            </Card>
          ))}
        </Col>
        <Spacer h={4} />
      </ScreenBody>
    </>
  );
}

function Stat({ label, value }) {
  return (
    <div style={{ flex: 1 }}>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.04 }}>{label}</div>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 700, marginTop: 3 }}>{value}</div>
    </div>
  );
}

window.MSCREENS = Object.assign(window.MSCREENS || {}, { home: HomeScreen, missions: MissionsScreen });
Object.assign(window, { MacroLine, MissionCheck, Stat });
