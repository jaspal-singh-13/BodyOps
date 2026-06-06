/* BodyOps · Desktop — Dashboard (multi-column command center) */

function DashboardDesktop({ nav, D }) {
  const g = D.goal, n = D.nutrition;
  const pct = Math.round((g.lost / 30) * 100);
  return (
    <>
      <DesktopTopBar title="Dashboard" sub={`FRIDAY · JUNE 6, 2026 · DAY ${D.user.dayN} OF ${D.user.planWeeks * 7}`}
        right={<div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <Tag><Icon name="flame" size={11} fill color="var(--ink)" /> {D.missionStats.streak}-day streak</Tag>
          <Btn size="sm" variant="secondary" icon="weight" onClick={() => nav.go('d-weight')}>Weigh in</Btn>
          <Btn size="sm" icon="camera" onClick={() => nav.go('d-meals')}>Log meal</Btn>
        </div>} />
      <DeskBody>
        <div style={{ display: 'flex', gap: 18, alignItems: 'flex-start' }}>
          {/* MAIN COLUMN */}
          <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 18 }}>
            {/* hero */}
            <Card pad={22} style={{ background: 'var(--fill-ink)', border: 'none' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'rgba(255,255,255,0.5)', fontWeight: 600, letterSpacing: 0.08, textTransform: 'uppercase' }}>Current weight</div>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginTop: 6 }}>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 52, fontWeight: 700, color: '#fff', lineHeight: 1 }}>{g.current}</span>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 18, color: 'rgba(255,255,255,0.55)' }}>kg</span>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 700, color: '#fff', background: 'rgba(255,255,255,0.14)', padding: '5px 10px', borderRadius: 999, marginLeft: 8 }}>
                      <Icon name="arrowD" size={13} color="#fff" /> 0.3 today</span>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 30 }}>
                  {[[g.lost, 'kg lost'],[g.remaining, 'kg to goal'],[pct + '%', 'complete']].map(([v, l]) => (
                    <div key={l} style={{ textAlign: 'right' }}>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 700, color: '#fff' }}>{v}</div>
                      <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', marginTop: 2 }}>{l}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ marginTop: 22 }}>
                <div style={{ height: 10, background: 'rgba(255,255,255,0.16)', borderRadius: 999, overflow: 'hidden' }}>
                  <div style={{ width: `${pct}%`, height: '100%', background: '#fff', borderRadius: 999 }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 9, fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.55)' }}>
                  <span>{g.start} kg · {D.user.startDate}</span>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}><Icon name="target" size={13} color="rgba(255,255,255,0.75)" /> On pace for <b style={{ color: '#fff' }}>{g.projDate}</b> · {g.aheadDays} days early</span>
                  <span>{g.goal} kg goal</span>
                </div>
              </div>
            </Card>

            {/* nutrition + missions */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
              <Card pad={18}>
                <Row justify="space-between"><Eyebrow>Today · Nutrition</Eyebrow><span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>{D.mealsToday.length} meals</span></Row>
                <div style={{ display: 'flex', gap: 16, marginTop: 14, alignItems: 'center' }}>
                  <DonutStat value={n.cal.v} total={n.cal.target} label="kcal" size={108} stroke={10} />
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 13 }}>
                    <MacroLine label="Protein" v={n.protein.v} t={n.protein.target} unit="g" />
                    <MacroLine label="Carbs" v={n.carbs.v} t={n.carbs.target} unit="g" />
                    <MacroLine label="Fat" v={n.fat.v} t={n.fat.target} unit="g" />
                  </div>
                </div>
              </Card>
              <Card pad={18}>
                <Row justify="space-between">
                  <Eyebrow>Daily missions</Eyebrow>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700 }}>{D.missionStats.done}/{D.missionStats.total}</span>
                </Row>
                <Col gap={1} style={{ marginTop: 10 }}>
                  {D.missions.slice(0, 5).map(m => (
                    <div key={m.id} style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '7px 0' }}>
                      <MissionCheck done={m.done} sm />
                      <span style={{ flex: 1, fontSize: 12.5, color: m.done ? 'var(--ink-3)' : 'var(--ink)', textDecoration: m.done ? 'line-through' : 'none' }}>{m.label}</span>
                      <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)' }}>{m.meta}</span>
                    </div>
                  ))}
                </Col>
              </Card>
            </div>

            {/* weight trend */}
            <Card pad={18}>
              <Row justify="space-between">
                <div><Eyebrow>Weight trend</Eyebrow><div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', marginTop: 3 }}>7-day avg <b style={{ color: 'var(--ink)' }}>98.8 kg</b> · down 1.1 kg this week</div></div>
                <Tag><Icon name="arrowD" size={10} /> ahead of plan</Tag>
              </Row>
              <div style={{ marginTop: 14 }}><WeightChart data={D.weightWeekly} goal={D.goal.goal} height={180} /></div>
            </Card>
          </div>

          {/* RIGHT RAIL */}
          <div style={{ width: 332, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 18 }}>
            {/* coach */}
            <Card pad={18} style={{ background: 'var(--card-2)' }}>
              <Row gap={10}><CoachMark size={36} /><div><div style={{ fontSize: 14, fontWeight: 800 }}>Coach briefing</div><div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)' }}>Updated 7:02 AM</div></div></Row>
              <div style={{ fontSize: 13, lineHeight: 1.55, marginTop: 13, color: 'var(--ink)' }}>{D.coach.daily}</div>
              <Col gap={7} style={{ marginTop: 14 }}>
                {D.coach.actions.slice(0, 2).map((a, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 9, padding: '9px 11px', background: 'var(--card)', border: '1px solid var(--line)', borderRadius: 'var(--r-sm)' }}>
                    <div style={{ width: 18, height: 18, borderRadius: 5, border: '1.5px solid var(--line-3)', flexShrink: 0 }} />
                    <span style={{ fontSize: 12, fontWeight: 500 }}>{a}</span>
                  </div>
                ))}
              </Col>
              <Btn full size="sm" variant="secondary" icon="coach" style={{ marginTop: 12 }} onClick={() => nav.go('d-coach')}>Open coach</Btn>
            </Card>

            {/* workout */}
            <Card pad={18}>
              <Eyebrow>Today's workout</Eyebrow>
              <Row gap={12} style={{ marginTop: 12 }}>
                <div style={{ width: 46, height: 46, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="workout" size={23} /></div>
                <div style={{ flex: 1 }}><div style={{ fontSize: 15.5, fontWeight: 800 }}>{D.workout.today}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>{D.workout.exercisesN} exercises · {D.workout.duration}</div></div>
              </Row>
              <Btn full size="md" icon="play" style={{ marginTop: 14 }} onClick={() => nav.go('d-workouts')}>Start session</Btn>
            </Card>

            {/* water + steps */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18 }}>
              <Card pad={16}>
                <Row justify="space-between"><Icon name="water" size={18} color="var(--ink-2)" /><span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)' }}>63%</span></Row>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 20, fontWeight: 700, marginTop: 10 }}>2.5<span style={{ fontSize: 11, color: 'var(--ink-3)' }}>/4L</span></div>
                <Bar value={63} h={5} style={{ marginTop: 8 }} />
              </Card>
              <Card pad={16}>
                <Row justify="space-between"><Icon name="steps" size={18} color="var(--ink-2)" /><span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)' }}>74%</span></Row>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 20, fontWeight: 700, marginTop: 10 }}>7.4<span style={{ fontSize: 11, color: 'var(--ink-3)' }}>/10k</span></div>
                <Bar value={74} h={5} style={{ marginTop: 8 }} />
              </Card>
            </div>
          </div>
        </div>
      </DeskBody>
    </>
  );
}

window.DSCREENS = Object.assign(window.DSCREENS || {}, { dashboard: DashboardDesktop });
