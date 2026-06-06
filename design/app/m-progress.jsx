/* BodyOps · Mobile — Progress analytics hub */

function ProgressScreen({ nav, D }) {
  const [range, setRange] = React.useState('Month');
  const p = D.progress;
  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px 8px', flexShrink: 0 }}>
        <div>
          <Eyebrow>Analytics</Eyebrow>
          <div style={{ fontSize: 21, fontWeight: 800, letterSpacing: -0.4, marginTop: 2 }}>Progress</div>
        </div>
        <button onClick={() => nav.go('weight')} style={{ width: 42, height: 42, borderRadius: 'var(--r-md)', background: 'var(--card)', border: '1px solid var(--line-2)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="weight" size={20} />
        </button>
      </div>
      {/* range switch */}
      <div style={{ padding: '0 14px 10px', flexShrink: 0 }}>
        <div style={{ display: 'flex', background: 'var(--paper-2)', borderRadius: 'var(--r-md)', padding: 3 }}>
          {['Week','Month','6 Months'].map(r => (
            <button key={r} onClick={() => setRange(r)} style={{ flex: 1, height: 34, borderRadius: 'var(--r-sm)', border: 'none', cursor: 'pointer',
              background: range === r ? 'var(--card)' : 'transparent', boxShadow: range === r ? 'var(--sh-1)' : 'none',
              fontFamily: 'var(--mono)', fontSize: 11.5, fontWeight: 700, color: range === r ? 'var(--ink)' : 'var(--ink-3)' }}>{r}</button>
          ))}
        </div>
      </div>

      <ScreenBody pad={14} gap={13} style={{ paddingTop: 4 }}>
        {/* goal projection */}
        <Card pad={16}>
          <Row justify="space-between" align="flex-start">
            <div>
              <Eyebrow>Goal projection</Eyebrow>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginTop: 6 }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 30, fontWeight: 700 }}>{D.goal.remaining}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--ink-3)' }}>kg to 77 kg</span>
              </div>
            </div>
            <Tag><Icon name="target" size={11} /> {D.goal.aheadDays}d ahead</Tag>
          </Row>
          <div style={{ marginTop: 12 }}><WeightChart data={D.weightWeekly} goal={D.goal.goal} height={150} /></div>
          <div style={{ marginTop: 6, fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-2)', textAlign: 'center' }}>
            Projected to reach goal <b>{D.goal.projDate}</b>
          </div>
        </Card>

        {/* key stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10 }}>
          <MiniStat icon="arrowD" v="1.4" unit="kg/wk" l="Avg loss" />
          <MiniStat icon="workout" v={p.workoutConsistency + '%'} l="Workouts" />
          <MiniStat icon="flame" v={p.habitCompletion + '%'} l="Habits" />
        </div>

        {/* calorie adherence */}
        <Card pad={15}>
          <Row justify="space-between"><Eyebrow>Calories vs target</Eyebrow><span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>5 / 7 under</span></Row>
          <div style={{ marginTop: 12 }}><BarChart data={p.calBars} target={D.nutrition.cal.target} unit="" height={130} /></div>
        </Card>

        {/* protein adherence */}
        <Card pad={15}>
          <Row justify="space-between"><Eyebrow>Protein vs target</Eyebrow><span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>4 / 7 hit</span></Row>
          <div style={{ marginTop: 12 }}><BarChart data={p.proteinBars} target={D.nutrition.protein.target} unit="g" height={130} targetLabel="GOAL" /></div>
        </Card>

        {/* habit consistency grid */}
        <Card pad={15}>
          <Row justify="space-between"><Eyebrow>Habit consistency · 8 weeks</Eyebrow><span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>{p.habitCompletion}%</span></Row>
          <div style={{ marginTop: 14, display: 'flex', justifyContent: 'center' }}>
            <HabitGrid weeks={p.habit} cols={7} cell={26} gap={5} labels={['Mon','','Wed','','Fri','','Sun']} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 7, marginTop: 12 }}>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-4)' }}>LESS</span>
            {[0.1, 0.4, 0.7, 1].map((v, i) => <div key={i} style={{ width: 12, height: 12, borderRadius: 3, background: `rgba(29,28,26,${0.18 + v * 0.7})` }} />)}
            <span style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-4)' }}>MORE</span>
          </div>
        </Card>

        {/* milestones */}
        <Eyebrow style={{ paddingLeft: 4 }}>Milestones</Eyebrow>
        <Col gap={9}>
          {D.milestones.map(m => (
            <Card key={m.id} pad={13} flat onClick={() => m.done && nav.go('celebrate')}>
              <Row gap={12}>
                <div style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', background: m.done ? 'var(--fill-ink)' : 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon name={m.icon} size={19} color={m.done ? '#fff' : 'var(--ink-2)'} /></div>
                <div style={{ flex: 1 }}>
                  <Row justify="space-between"><span style={{ fontSize: 13.5, fontWeight: 700 }}>{m.title}</span>
                    {m.done ? <Tag>✓ {m.date}</Tag> : <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>{m.meta}</span>}</Row>
                  {!m.done && m.prog != null && <Bar value={m.prog} h={5} style={{ marginTop: 8 }} />}
                </div>
              </Row>
            </Card>
          ))}
        </Col>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

function MiniStat({ icon, v, unit, l }) {
  return (
    <Card pad={12} flat>
      <Icon name={icon} size={16} color="var(--ink-2)" />
      <div style={{ fontFamily: 'var(--mono)', fontSize: 19, fontWeight: 700, marginTop: 7 }}>{v}{unit && <span style={{ fontSize: 10, color: 'var(--ink-3)', fontWeight: 500 }}> {unit}</span>}</div>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-3)', textTransform: 'uppercase', marginTop: 2 }}>{l}</div>
    </Card>
  );
}

window.MSCREENS = Object.assign(window.MSCREENS || {}, { progress: ProgressScreen });
Object.assign(window, { MiniStat });
