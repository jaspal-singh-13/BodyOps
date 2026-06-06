/* BodyOps · Desktop — Meals, Weight, Workouts */

/* ═══════════════ MEALS ═══════════════ */
function MealsDesktop({ nav, D }) {
  return (
    <>
      <DesktopTopBar title="Meals" sub="FRIDAY · JUNE 6"
        right={<div style={{ display: 'flex', gap: 10 }}>
          <Btn size="sm" variant="secondary" icon="cal">Jun 6</Btn>
          <Btn size="sm" icon="camera">Log meal</Btn>
        </div>} />
      <DeskBody>
        <div style={{ display: 'flex', gap: 18, alignItems: 'flex-start' }}>
          {/* timeline */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <Eyebrow style={{ marginBottom: 12 }}>Today · {D.mealsToday.length} meals logged</Eyebrow>
            <Col gap={12}>
              {D.mealsToday.map(m => (
                <Card key={m.id} pad={0} style={{ overflow: 'hidden' }}>
                  <div style={{ display: 'flex' }}>
                    <ImageSlot label="" icon="meal" h={118} w={140} radius={0} style={{ borderRadius: 0, border: 'none', borderRight: '1px solid var(--line)' }} />
                    <div style={{ flex: 1, padding: 16 }}>
                      <Row justify="space-between">
                        <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', fontWeight: 600 }}>{m.time} · {m.slot.toUpperCase()}</span>
                        <Row gap={8}><Tag><Icon name="coach" size={10} /> AI logged</Tag><Confidence level={m.conf} /></Row>
                      </Row>
                      <div style={{ fontSize: 16, fontWeight: 700, marginTop: 6 }}>{m.title}</div>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', marginTop: 4 }}>{m.items.join(' · ')}</div>
                      <div style={{ display: 'flex', gap: 22, marginTop: 12 }}>
                        {[['kcal', m.kcal],['P', m.p + 'g'],['C', m.c + 'g'],['F', m.f + 'g']].map(([l, v]) => (
                          <div key={l}><span style={{ fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 700 }}>{v}</span><span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)', marginLeft: 4 }}>{l}</span></div>
                        ))}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', padding: '0 16px' }}><Icon name="dots" size={18} color="var(--ink-4)" /></div>
                  </div>
                </Card>
              ))}
              {/* add zone */}
              <div className="hatch" style={{ height: 92, borderRadius: 'var(--r-lg)', flexDirection: 'column', gap: 8, cursor: 'pointer' }}>
                <Icon name="camera" size={22} color="var(--ink-3)" />
                <span className="hatch-label">DROP A PHOTO OR CLICK TO CAPTURE</span>
              </div>
            </Col>

            <Eyebrow style={{ margin: '22px 0 12px' }}>Earlier this week</Eyebrow>
            <Card pad={0} flat>
              {D.mealHistory.slice(1).map((d, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 18px', borderBottom: i < D.mealHistory.length - 2 ? '1px solid var(--line)' : 'none' }}>
                  <div><div style={{ fontSize: 13.5, fontWeight: 600 }}>{d.date}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 1 }}>{d.meals} meals</div></div>
                  <div style={{ display: 'flex', gap: 26, alignItems: 'center' }}>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--ink-2)' }}>{d.p}g protein</span>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 15, fontWeight: 700 }}>{d.total.toLocaleString()} kcal</span>
                    <Icon name="chevR" size={15} color="var(--ink-4)" />
                  </div>
                </div>
              ))}
            </Card>
          </div>

          {/* rail — today summary */}
          <div style={{ width: 300, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 18 }}>
            <Card pad={18}>
              <Eyebrow>Today's totals</Eyebrow>
              <div style={{ display: 'flex', justifyContent: 'center', margin: '14px 0' }}>
                <DonutStat value={D.nutrition.cal.v} total={D.nutrition.cal.target} label="kcal" size={140} stroke={12} />
              </div>
              <Col gap={12}>
                <MacroLine label="Protein" v={D.nutrition.protein.v} t={D.nutrition.protein.target} unit="g" />
                <MacroLine label="Carbs" v={D.nutrition.carbs.v} t={D.nutrition.carbs.target} unit="g" />
                <MacroLine label="Fat" v={D.nutrition.fat.v} t={D.nutrition.fat.target} unit="g" />
              </Col>
              <div style={{ marginTop: 14, paddingTop: 13, borderTop: '1px solid var(--line)', textAlign: 'center' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--ink-2)' }}><b style={{ color: 'var(--ink)' }}>{D.nutrition.cal.target - D.nutrition.cal.v}</b> kcal remaining</span>
              </div>
            </Card>
            <Card pad={16} style={{ background: 'var(--card-2)' }}>
              <Row gap={9} align="flex-start"><CoachMark size={32} /><span style={{ flex: 1, fontSize: 12.5, lineHeight: 1.5 }}>You're <b>58g protein short</b> with one meal left. A chicken-and-rice dinner closes the gap.</span></Row>
            </Card>
          </div>
        </div>
      </DeskBody>
    </>
  );
}

/* ═══════════════ WEIGHT ═══════════════ */
function WeightDesktop({ nav, D }) {
  const [range, setRange] = React.useState('6W');
  return (
    <>
      <DesktopTopBar title="Weight" sub="TRACKING SINCE APR 24"
        right={<Btn size="sm" icon="plus">Log weight</Btn>} />
      <DeskBody>
        {/* top stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr 1fr 1fr', gap: 16, marginBottom: 18 }}>
          <Card pad={18} style={{ background: 'var(--fill-ink)', border: 'none' }}>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase' }}>Latest</div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginTop: 6 }}><span style={{ fontFamily: 'var(--mono)', fontSize: 38, fontWeight: 700, color: '#fff', lineHeight: 1 }}>{D.goal.current}</span><span style={{ fontFamily: 'var(--mono)', fontSize: 14, color: 'rgba(255,255,255,0.55)' }}>kg</span></div>
            <Tag style={{ marginTop: 12, background: 'rgba(255,255,255,0.14)', color: '#fff' }}><Icon name="arrowD" size={10} color="#fff" /> 8.6 kg total</Tag>
          </Card>
          {[['7-day avg', D.weightAvg.week, '−1.1 vs prev'],['30-day avg', D.weightAvg.month, '−2.8 vs prev'],['To goal', D.goal.remaining, `${D.goal.pctToGoal}% complete`]].map(([l, v, s]) => (
            <Card key={l} pad={18}>
              <Eyebrow>{l}</Eyebrow>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 30, fontWeight: 700, marginTop: 8 }}>{v}<span style={{ fontSize: 13, color: 'var(--ink-3)' }}> kg</span></div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 4 }}>{s}</div>
            </Card>
          ))}
        </div>
        {/* chart */}
        <Card pad={20} style={{ marginBottom: 18 }}>
          <Row justify="space-between">
            <Eyebrow>Weight trend</Eyebrow>
            <div style={{ display: 'flex', gap: 6 }}>{['2W','6W','3M','6M'].map(r => <Chip key={r} active={range === r} onClick={() => setRange(r)} style={{ height: 28, padding: '0 11px', fontSize: 11 }}>{r}</Chip>)}</div>
          </Row>
          <div style={{ marginTop: 16 }}><WeightChart data={D.weightWeekly} goal={D.goal.goal} height={230} /></div>
        </Card>
        {/* two columns */}
        <div style={{ display: 'flex', gap: 18, alignItems: 'flex-start' }}>
          <Card pad={0} flat style={{ flex: 1 }}>
            <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--line)' }}><Eyebrow>Recent entries</Eyebrow></div>
            {D.weightLog.map((e, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '70px 1fr 70px 70px', alignItems: 'center', padding: '13px 18px', borderBottom: i < D.weightLog.length - 1 ? '1px solid var(--line)' : 'none' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ink-2)' }}>{e.day} {e.date.split(' ')[1]}</span>
                <span>{e.tag && <Tag>{e.tag}</Tag>}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', textAlign: 'right' }}>{e.delta > 0 ? '+' : ''}{e.delta}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 15, fontWeight: 700, textAlign: 'right' }}>{e.w}</span>
              </div>
            ))}
          </Card>
          <Card pad={18} style={{ width: 330, flexShrink: 0, background: 'var(--card-2)' }}>
            <Row gap={10}><CoachMark size={34} /><div style={{ fontSize: 14, fontWeight: 800 }}>Trend insight</div></Row>
            <div style={{ fontSize: 13, lineHeight: 1.55, marginTop: 12 }}>Your loss rate is <b>steeper than plan</b> — 1.4 kg/wk vs your 1.15 kg target. The daily bounce (water, sodium) is normal; the 7-day average is what matters, and it's falling cleanly.</div>
            <div style={{ marginTop: 14, paddingTop: 13, borderTop: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between' }}>
              <Stat label="Projected goal" value={D.goal.projDate} />
              <Stat label="Ahead by" value={`${D.goal.aheadDays} days`} />
            </div>
          </Card>
        </div>
      </DeskBody>
    </>
  );
}

/* ═══════════════ WORKOUTS ═══════════════ */
function WorkoutsDesktop({ nav, D }) {
  const w = D.workout;
  return (
    <>
      <DesktopTopBar title="Workouts" sub={`${w.split.toUpperCase()} · ${w.week.toUpperCase()}`}
        right={<Btn size="sm" icon="play">Start session</Btn>} />
      <DeskBody>
        {/* week strip */}
        <Card pad={14} flat style={{ marginBottom: 18 }}>
          <div style={{ display: 'flex', gap: 8 }}>
            {w.plan.map((d, i) => (
              <div key={i} style={{ flex: 1, textAlign: 'center', padding: '12px 4px', borderRadius: 'var(--r-md)',
                background: d.today ? 'var(--fill-ink)' : d.done ? 'var(--paper-2)' : 'transparent', border: d.today ? 'none' : '1px solid var(--line)' }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10, fontWeight: 600, color: d.today ? 'rgba(255,255,255,0.6)' : 'var(--ink-3)' }}>{d.day.toUpperCase()}</div>
                <div style={{ fontSize: 12.5, fontWeight: 700, marginTop: 6, color: d.today ? '#fff' : 'var(--ink)' }}>{d.rest ? 'Rest' : d.name.replace(' Day', '')}</div>
                <div style={{ marginTop: 6, height: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {d.done ? <Icon name="check" size={14} color="var(--ink)" stroke={2.4} /> : !d.rest && <Icon name="workout" size={14} color={d.today ? '#fff' : 'var(--ink-4)'} />}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <div style={{ display: 'flex', gap: 18, alignItems: 'flex-start' }}>
          {/* today exercises table */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <Card pad={0}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div><div style={{ fontSize: 17, fontWeight: 800 }}>{w.today}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>Chest · Shoulders · Triceps · {w.exercisesN} exercises</div></div>
                <Btn size="sm" icon="play">Start</Btn>
              </div>
              {/* table header */}
              <div style={{ display: 'grid', gridTemplateColumns: '28px 1fr 90px 110px 130px 40px', padding: '10px 20px', borderBottom: '1px solid var(--line)', background: 'var(--card-2)' }}>
                {['','EXERCISE','SETS','LAST','TARGET — PROGRESSION',''].map((h, i) => <div key={i} style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)', fontWeight: 600 }}>{h}</div>)}
              </div>
              {w.exercises.map((ex, i) => (
                <div key={ex.id} onClick={() => {}} style={{ display: 'grid', gridTemplateColumns: '28px 1fr 90px 110px 130px 40px', alignItems: 'center', padding: '14px 20px', borderBottom: i < w.exercises.length - 1 ? '1px solid var(--line)' : 'none' }}>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, color: 'var(--ink-3)' }}>{i + 1}</div>
                  <div><div style={{ fontSize: 14, fontWeight: 700 }}>{ex.name}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)', marginTop: 1 }}>{ex.muscle}</div></div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 13 }}>{ex.sets} ×</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 12.5, color: 'var(--ink-3)' }}>{ex.lastW}kg × {ex.lastR}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    {ex.up ? <Icon name="arrowU" size={14} color="var(--ink)" /> : <Icon name="target" size={13} color="var(--ink-3)" />}
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 13.5, fontWeight: 700 }}>{ex.sugW}kg × {ex.sugR}</span>
                  </div>
                  <Icon name="chevR" size={15} color="var(--ink-4)" />
                </div>
              ))}
            </Card>
          </div>
          {/* rail — volume + last */}
          <div style={{ width: 300, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 18 }}>
            <Card pad={18}>
              <Eyebrow>This week</Eyebrow>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginTop: 14 }}>
                {[['Sessions', '5/6'],['Volume', '34.2t'],['PRs', '4'],['Consistency', '92%']].map(([l, v]) => (
                  <div key={l}><div style={{ fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 700 }}>{v}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)', textTransform: 'uppercase', marginTop: 2 }}>{l}</div></div>
                ))}
              </div>
            </Card>
            <Card pad={18} style={{ background: 'var(--card-2)' }}>
              <Row gap={10}><Icon name="trend" size={18} /><div style={{ fontSize: 13.5, fontWeight: 800 }}>Progression logic</div></Row>
              <div style={{ fontSize: 12.5, lineHeight: 1.55, marginTop: 11 }}>When you hit the top of a rep range across all sets, we add load next session (≈2.5 kg upper, 5 kg lower). Miss it, and we hold to let you build reps first.</div>
            </Card>
          </div>
        </div>
      </DeskBody>
    </>
  );
}

window.DSCREENS = Object.assign(window.DSCREENS || {}, { 'd-meals': MealsDesktop, 'd-weight': WeightDesktop, 'd-workouts': WorkoutsDesktop });
