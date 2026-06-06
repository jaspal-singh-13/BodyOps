/* BodyOps · Mobile — Workout flow */

function WorkoutScreen({ nav, D }) {
  const w = D.workout;
  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px 8px', flexShrink: 0 }}>
        <div>
          <Eyebrow>{w.split} · {w.week}</Eyebrow>
          <div style={{ fontSize: 21, fontWeight: 800, letterSpacing: -0.4, marginTop: 2 }}>Workout</div>
        </div>
        <button onClick={() => nav.go('workout-summary')} style={{ width: 42, height: 42, borderRadius: 'var(--r-md)', background: 'var(--card)', border: '1px solid var(--line-2)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="cal" size={20} />
        </button>
      </div>
      <ScreenBody pad={14} gap={13}>
        {/* today session */}
        <Card pad={16} elevated style={{ background: 'var(--fill-ink)', border: 'none' }}>
          <Row justify="space-between" align="flex-start">
            <div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.55)', fontWeight: 600, letterSpacing: 0.08, textTransform: 'uppercase' }}>Today · {w.dayLabel}</div>
              <div style={{ fontSize: 23, fontWeight: 800, color: '#fff', marginTop: 4, letterSpacing: -0.3 }}>{w.today}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.6)', marginTop: 4 }}>Chest · Shoulders · Triceps</div>
            </div>
            <div style={{ width: 46, height: 46, borderRadius: 'var(--r-md)', background: 'rgba(255,255,255,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon name="workout" size={24} color="#fff" /></div>
          </Row>
          <div style={{ display: 'flex', gap: 18, marginTop: 16 }}>
            {[[w.exercisesN, 'exercises'],[18, 'sets'],[w.duration.replace('~',''), 'est.']].map(([v, l]) => (
              <div key={l}><div style={{ fontFamily: 'var(--mono)', fontSize: 18, fontWeight: 700, color: '#fff' }}>{v}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', marginTop: 1 }}>{l}</div></div>
            ))}
          </div>
          <Btn full size="lg" icon="play" style={{ marginTop: 16, background: '#fff', color: 'var(--ink)', border: 'none' }} onClick={() => nav.go('workout-active')}>Start workout</Btn>
        </Card>

        {/* exercises preview */}
        <Eyebrow style={{ paddingLeft: 4 }}>Exercises · with progression</Eyebrow>
        <Col gap={9}>
          {w.exercises.map((ex, i) => (
            <Card key={ex.id} pad={13} onClick={() => nav.go('exercise-detail', { id: ex.id })} flat style={{ borderColor: 'var(--line-2)' }}>
              <Row gap={12}>
                <div style={{ width: 28, height: 28, borderRadius: 999, background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, color: 'var(--ink-2)', flexShrink: 0 }}>{i + 1}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: 700 }}>{ex.name}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)', marginTop: 2 }}>{ex.muscle} · {ex.sets} sets</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-4)', textTransform: 'uppercase' }}>Last</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--ink-3)' }}>{ex.lastW}kg × {ex.lastR}</div>
                </div>
                <div style={{ width: 1, height: 30, background: 'var(--line)' }} />
                <div style={{ textAlign: 'right', minWidth: 64 }}>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-4)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 3 }}>
                    {ex.up && <Icon name="arrowU" size={10} color="var(--ink)" />}Target</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700 }}>{ex.sugW}kg × {ex.sugR}</div>
                </div>
              </Row>
            </Card>
          ))}
        </Col>

        {/* week split */}
        <Eyebrow style={{ paddingLeft: 4, marginTop: 4 }}>This week</Eyebrow>
        <Card pad={12} flat>
          <div style={{ display: 'flex', gap: 6 }}>
            {w.plan.map((d, i) => (
              <div key={i} style={{ flex: 1, textAlign: 'center', padding: '9px 2px', borderRadius: 'var(--r-sm)',
                background: d.today ? 'var(--fill-ink)' : d.done ? 'var(--paper-2)' : 'transparent',
                border: d.today ? 'none' : '1px solid var(--line)' }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 9, fontWeight: 600, color: d.today ? 'rgba(255,255,255,0.6)' : 'var(--ink-3)' }}>{d.day.toUpperCase()}</div>
                <div style={{ marginTop: 6, height: 18, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {d.rest ? <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-4)' }}>REST</span>
                    : d.done ? <Icon name="check" size={15} color="var(--ink)" stroke={2.4} />
                    : <Icon name="workout" size={16} color={d.today ? '#fff' : 'var(--ink-3)'} />}
                </div>
              </div>
            ))}
          </div>
        </Card>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

/* ───────────────────────── Active session (full-bleed) ───────────────────── */
function WorkoutActiveScreen({ nav, D }) {
  const w = D.workout;
  const [exIdx, setExIdx] = React.useState(0);
  const [sets, setSets] = React.useState(w.activeSets);
  const [resting, setResting] = React.useState(false);
  const ex = w.exercises[exIdx];
  const logSet = (i) => { setSets(sets.map((s, x) => x === i ? { ...s, done: true, current: false } : (x === i + 1 ? { ...s, current: true } : s))); setResting(true); setTimeout(() => setResting(false), 1400); };
  const doneSets = sets.filter(s => s.done).length;
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--paper)', minHeight: 0 }}>
      {/* header */}
      <div style={{ flexShrink: 0, padding: '14px 14px 12px', background: 'var(--fill-ink)', color: '#fff' }}>
        <Row justify="space-between">
          <button onClick={() => nav.back()} style={{ width: 34, height: 34, borderRadius: 999, background: 'rgba(255,255,255,0.14)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="chevD" size={18} color="#fff" /></button>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.55)' }}>{w.today.toUpperCase()}</div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 19, fontWeight: 700, color: '#fff', letterSpacing: 1 }}>24:18</div>
          </div>
          <button style={{ width: 34, height: 34, borderRadius: 999, background: 'rgba(255,255,255,0.14)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="pause" size={16} color="#fff" /></button>
        </Row>
        {/* exercise progress dots */}
        <div style={{ display: 'flex', gap: 4, marginTop: 14 }}>
          {w.exercises.map((_, i) => <div key={i} style={{ flex: 1, height: 4, borderRadius: 999, background: i < exIdx ? '#fff' : i === exIdx ? 'rgba(255,255,255,0.85)' : 'rgba(255,255,255,0.22)' }} />)}
        </div>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'rgba(255,255,255,0.6)', marginTop: 8 }}>Exercise {exIdx + 1} of {w.exercises.length}</div>
      </div>

      <div className="bo-scroll" style={{ flex: 1, overflowY: 'auto', padding: 14, display: 'flex', flexDirection: 'column', gap: 13 }}>
        {/* current exercise */}
        <div>
          <Row justify="space-between" align="flex-start">
            <div>
              <div style={{ fontSize: 22, fontWeight: 800, letterSpacing: -0.4 }}>{ex.name}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', marginTop: 3 }}>{ex.muscle} · {doneSets}/{sets.length} sets done</div>
            </div>
            <button onClick={() => nav.go('exercise-detail', { id: ex.id })} style={{ width: 36, height: 36, borderRadius: 'var(--r-md)', border: '1px solid var(--line-2)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="info" size={17} /></button>
          </Row>
        </div>

        {/* suggested overload banner */}
        <Card pad={13} style={{ background: 'var(--card-2)' }}>
          <Row gap={10}>
            <Icon name="trend" size={18} />
            <div style={{ flex: 1, fontSize: 12.5, lineHeight: 1.45 }}>
              <b>Suggested:</b> {ex.sugW} kg × {ex.sugR}. {ex.note || `You hit ${ex.lastR} reps at ${ex.lastW} kg last time.`}
            </div>
          </Row>
        </Card>

        {/* set log */}
        <Card pad={0} flat>
          <div style={{ display: 'grid', gridTemplateColumns: '46px 1fr 1fr 56px', padding: '10px 14px', borderBottom: '1px solid var(--line)' }}>
            {['SET','KG','REPS',''].map(h => <div key={h} style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)', fontWeight: 600 }}>{h}</div>)}
          </div>
          {sets.map((s, i) => (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: '46px 1fr 1fr 56px', alignItems: 'center', padding: '11px 14px', borderBottom: i < sets.length - 1 ? '1px solid var(--line)' : 'none',
              background: s.current ? 'var(--card-2)' : 'transparent' }}>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 14, fontWeight: 700, color: s.done ? 'var(--ink)' : 'var(--ink-3)' }}>{s.set}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 700 }}>{s.w}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 700, color: s.reps ? 'var(--ink)' : 'var(--ink-4)' }}>{s.reps || s.target}</div>
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                {s.done ? <div style={{ width: 30, height: 30, borderRadius: 8, background: 'var(--fill-ink)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="check" size={16} color="#fff" stroke={2.6} /></div>
                  : <button onClick={() => logSet(i)} disabled={!s.current} style={{ width: 30, height: 30, borderRadius: 8, border: '1.5px solid ' + (s.current ? 'var(--ink)' : 'var(--line-2)'), background: 'var(--card)', cursor: s.current ? 'pointer' : 'default', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: s.current ? 1 : 0.4 }}><Icon name="check" size={15} color="var(--ink-3)" stroke={2.2} /></button>}
              </div>
            </div>
          ))}
        </Card>

        {resting && (
          <Card pad={13} style={{ borderColor: 'var(--line-3)' }}>
            <Row justify="space-between"><Row gap={8}><Icon name="clock" size={16} /><span style={{ fontSize: 13, fontWeight: 600 }}>Rest timer</span></Row>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 700 }}>1:30</span></Row>
          </Card>
        )}
        <Spacer h={70} />
      </div>

      {/* bottom action */}
      <div style={{ flexShrink: 0, padding: '12px 14px', paddingBottom: 24, borderTop: '1px solid var(--line)', background: 'var(--card)', display: 'flex', gap: 10 }}>
        <Btn variant="secondary" size="lg" icon="chevL" onClick={() => setExIdx(Math.max(0, exIdx - 1))} style={{ width: 56, padding: 0 }}> </Btn>
        {exIdx < w.exercises.length - 1
          ? <Btn full size="lg" iconRight="chevR" onClick={() => { setExIdx(exIdx + 1); setSets(w.activeSets); }}>Next exercise</Btn>
          : <Btn full size="lg" icon="check" onClick={() => nav.replace('workout-summary')}>Finish workout</Btn>}
      </div>
    </div>
  );
}

/* ───────────────────────── Exercise detail ───────────────────────────────── */
function ExerciseDetailScreen({ nav, params, D }) {
  const ex = D.workout.exercises.find(e => e.id === params.id) || D.workout.exercises[0];
  const hist = [
    { d: 'May 21', w: 55, r: 8 }, { d: 'May 26', w: 57.5, r: 7 }, { d: 'May 30', w: 57.5, r: 9 },
    { d: 'Jun 2', w: 60, r: 7 }, { d: 'Jun 4', w: 60, r: 8 },
  ];
  return (
    <>
      <MobileTopBar title={ex.name} onBack={() => nav.back()} sub={`${ex.muscle} · ${ex.sets} working sets`} />
      <ScreenBody pad={14} gap={13}>
        <ImageSlot label="FORM DEMO · LOOP" icon="play" h={140} radius="var(--r-lg)" />

        {/* progression suggestion */}
        <Card pad={15} style={{ background: 'var(--fill-ink)', border: 'none' }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.55)', textTransform: 'uppercase', letterSpacing: 0.06 }}>Today's target · progressive overload</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 12 }}>
            <div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'rgba(255,255,255,0.5)' }}>LAST</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 18, fontWeight: 700, color: 'rgba(255,255,255,0.8)' }}>{ex.lastW}kg × {ex.lastR}</div>
            </div>
            <Icon name="chevR" size={20} color="rgba(255,255,255,0.4)" />
            <div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'rgba(255,255,255,0.5)' }}>SUGGESTED</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 700, color: '#fff' }}>{ex.sugW}kg × {ex.sugR}</div>
            </div>
          </div>
          <div style={{ marginTop: 12, paddingTop: 11, borderTop: '1px solid rgba(255,255,255,0.12)', fontSize: 12, color: 'rgba(255,255,255,0.75)', lineHeight: 1.45 }}>
            {ex.note || `You completed all sets at ${ex.lastW} kg last session — time to add load.`}
          </div>
        </Card>

        {/* progression chart */}
        <Card pad={15}>
          <Row justify="space-between"><Eyebrow>Working weight · last 5</Eyebrow><Tag><Icon name="arrowU" size={10} /> +5 kg / 3wk</Tag></Row>
          <div style={{ marginTop: 12 }}>
            <BarChart data={hist.map(h => ({ d: h.d.split(' ')[1], v: h.w }))} target={ex.sugW} unit="kg" height={130} targetLabel="NEXT" />
          </div>
        </Card>

        {/* history list */}
        <Eyebrow style={{ paddingLeft: 4 }}>Recent sessions</Eyebrow>
        <Card pad={0} flat>
          {hist.slice().reverse().map((h, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', borderBottom: i < hist.length - 1 ? '1px solid var(--line)' : 'none' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ink-2)' }}>{h.d}</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 14, fontWeight: 700 }}>{h.w} kg × {h.r}</span>
            </div>
          ))}
        </Card>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

/* ───────────────────────── Workout summary ───────────────────────────────── */
function WorkoutSummaryScreen({ nav, D }) {
  const s = D.workout.summary;
  return (
    <>
      <MobileTopBar title="Session complete" onBack={() => nav.tab('workout')}
        right={<button style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', border: '1px solid var(--line-2)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="share" size={17} /></button>} />
      <ScreenBody pad={14} gap={13}>
        <Card pad={18} style={{ textAlign: 'center' }}>
          <div style={{ width: 56, height: 56, borderRadius: 999, background: 'var(--fill-ink)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto' }}>
            <Icon name="check" size={28} color="#fff" stroke={2.6} /></div>
          <div style={{ fontSize: 20, fontWeight: 800, marginTop: 12, letterSpacing: -0.3 }}>{s.name} done</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--ink-3)', marginTop: 3 }}>Logged · Friday, June 6 · {s.duration}</div>
        </Card>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {[['Duration', s.duration, 'clock'],['Total volume', s.volume, 'workout'],['Sets done', s.sets, 'list'],['New PRs', s.prs, 'trophy']].map(([l, v, ic]) => (
            <Card key={l} pad={14} flat>
              <Icon name={ic} size={18} color="var(--ink-2)" />
              <div style={{ fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 700, marginTop: 8 }}>{v}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)', textTransform: 'uppercase', marginTop: 2 }}>{l}</div>
            </Card>
          ))}
        </div>

        <Card pad={15}>
          <Row gap={8}><Icon name="trophy" size={16} /><Eyebrow>Personal records</Eyebrow></Row>
          <Col gap={8} style={{ marginTop: 11 }}>
            {s.prList.map((p, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '10px 12px', background: 'var(--card-2)', borderRadius: 'var(--r-sm)', border: '1px solid var(--line)' }}>
                <Icon name="bolt" size={15} fill color="var(--ink)" />
                <span style={{ fontFamily: 'var(--mono)', fontSize: 12.5, fontWeight: 600 }}>{p}</span>
              </div>
            ))}
          </Col>
        </Card>

        <Card pad={14} style={{ background: 'var(--card-2)' }}>
          <Row gap={10} align="flex-start"><CoachMark size={34} />
            <div style={{ flex: 1, fontSize: 12.5, lineHeight: 1.5 }}>Strong session — two PRs and you progressed bench again. That's 6 of 6 this week. Rest up; <b>Legs A</b> tomorrow.</div>
          </Row>
        </Card>
        <Btn full size="lg" onClick={() => nav.tab('home')}>Back to home</Btn>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

window.MSCREENS = Object.assign(window.MSCREENS || {}, {
  workout: WorkoutScreen, 'workout-active': WorkoutActiveScreen,
  'exercise-detail': ExerciseDetailScreen, 'workout-summary': WorkoutSummaryScreen,
});
