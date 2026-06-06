/* BodyOps · Desktop — Progress, Coach, Settings */

/* ═══════════════ PROGRESS ═══════════════ */
function ProgressDesktop({ nav, D }) {
  const [range, setRange] = React.useState('Month');
  const p = D.progress;
  return (
    <>
      <DesktopTopBar title="Progress" sub="ANALYTICS HUB"
        right={<div style={{ display: 'flex', background: 'var(--paper-2)', borderRadius: 'var(--r-md)', padding: 3 }}>
          {['Week','Month','6 Months'].map(r => <button key={r} onClick={() => setRange(r)} style={{ height: 32, padding: '0 14px', borderRadius: 'var(--r-sm)', border: 'none', cursor: 'pointer', background: range === r ? 'var(--card)' : 'transparent', boxShadow: range === r ? 'var(--sh-1)' : 'none', fontFamily: 'var(--mono)', fontSize: 11.5, fontWeight: 700, color: range === r ? 'var(--ink)' : 'var(--ink-3)' }}>{r}</button>)}
        </div>} />
      <DeskBody>
        {/* stat row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 16, marginBottom: 18 }}>
          {[['arrowD','1.4 kg','Avg loss / wk'],['weight','8.6 kg','Total lost'],['workout','92%','Workout rate'],['flame','86%','Habit rate'],['target',D.goal.aheadDays + 'd','Ahead of plan']].map(([ic, v, l]) => (
            <Card key={l} pad={16}>
              <Icon name={ic} size={17} color="var(--ink-2)" />
              <div style={{ fontFamily: 'var(--mono)', fontSize: 23, fontWeight: 700, marginTop: 9 }}>{v}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)', textTransform: 'uppercase', marginTop: 3 }}>{l}</div>
            </Card>
          ))}
        </div>
        {/* main grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 18 }}>
          <Card pad={20}>
            <Row justify="space-between"><div><Eyebrow>Weight trend & projection</Eyebrow><div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', marginTop: 3 }}>Projected goal <b style={{ color: 'var(--ink)' }}>{D.goal.projDate}</b></div></div><Tag><Icon name="arrowD" size={10} /> on pace</Tag></Row>
            <div style={{ marginTop: 16 }}><WeightChart data={D.weightWeekly} goal={D.goal.goal} height={210} /></div>
          </Card>
          <Card pad={20}>
            <Eyebrow>Habit consistency · 8 weeks</Eyebrow>
            <div style={{ marginTop: 18, display: 'flex', justifyContent: 'center' }}>
              <HabitGrid weeks={p.habit} cols={7} cell={30} gap={6} labels={['Mon','','Wed','','Fri','','Sun']} />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 7, marginTop: 16 }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-4)' }}>LESS</span>
              {[0.1,0.4,0.7,1].map((v, i) => <div key={i} style={{ width: 13, height: 13, borderRadius: 3, background: `rgba(29,28,26,${0.18 + v * 0.7})` }} />)}
              <span style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-4)' }}>MORE</span>
            </div>
          </Card>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18, marginTop: 18 }}>
          <Card pad={20}>
            <Row justify="space-between"><Eyebrow>Calories vs target</Eyebrow><span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>5 / 7 under</span></Row>
            <div style={{ marginTop: 16 }}><BarChart data={p.calBars} target={D.nutrition.cal.target} unit="" height={150} /></div>
          </Card>
          <Card pad={20}>
            <Row justify="space-between"><Eyebrow>Protein vs target</Eyebrow><span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>4 / 7 hit</span></Row>
            <div style={{ marginTop: 16 }}><BarChart data={p.proteinBars} target={D.nutrition.protein.target} unit="g" height={150} targetLabel="GOAL" /></div>
          </Card>
        </div>
        {/* milestones */}
        <Eyebrow style={{ margin: '22px 0 12px' }}>Milestones</Eyebrow>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          {D.milestones.map(m => (
            <Card key={m.id} pad={16}>
              <Row justify="space-between"><div style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', background: m.done ? 'var(--fill-ink)' : 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name={m.icon} size={19} color={m.done ? '#fff' : 'var(--ink-2)'} /></div>
                {m.done ? <Tag>✓ {m.date}</Tag> : null}</Row>
              <div style={{ fontSize: 14, fontWeight: 700, marginTop: 12 }}>{m.title}</div>
              {!m.done ? <><div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 3 }}>{m.meta}</div><Bar value={m.prog} h={5} style={{ marginTop: 9 }} /></>
                : <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 3 }}>Achieved</div>}
            </Card>
          ))}
        </div>
      </DeskBody>
    </>
  );
}

/* ═══════════════ COACH ═══════════════ */
function CoachDesktop({ nav, D }) {
  const c = D.coach;
  const [thread, setThread] = React.useState(c.thread);
  return (
    <>
      <DesktopTopBar title="Coach" sub="YOUR AI ACCOUNTABILITY PARTNER"
        right={<Tag><span style={{ width: 7, height: 7, borderRadius: 999, background: 'var(--ink)', display: 'inline-block' }} /> Online</Tag>} />
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {/* left — briefing + insights */}
        <div className="bo-scroll" style={{ flex: 1, overflowY: 'auto', padding: 26, display: 'flex', flexDirection: 'column', gap: 18 }}>
          <Card pad={22} style={{ background: 'var(--fill-ink)', border: 'none' }}>
            <Eyebrow style={{ color: 'rgba(255,255,255,0.5)' }}>Daily briefing · Friday</Eyebrow>
            <div style={{ fontSize: 22, fontWeight: 800, color: '#fff', marginTop: 8, letterSpacing: -0.4 }}>{c.headline}</div>
            <div style={{ fontSize: 13.5, color: 'rgba(255,255,255,0.78)', lineHeight: 1.55, marginTop: 11, maxWidth: 560 }}>{c.daily}</div>
          </Card>
          <div>
            <Eyebrow style={{ marginBottom: 12 }}>Do these today</Eyebrow>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              {c.actions.map((a, i) => (
                <Card key={i} pad={15} flat>
                  <Row gap={9}><Icon name="bolt" size={15} fill color="var(--ink)" /><div style={{ width: 20, height: 20, borderRadius: 6, border: '1.5px solid var(--line-3)', marginLeft: 'auto' }} /></Row>
                  <div style={{ fontSize: 13, fontWeight: 500, marginTop: 10, lineHeight: 1.4 }}>{a}</div>
                </Card>
              ))}
            </div>
          </div>
          <div>
            <Eyebrow style={{ marginBottom: 12 }}>Insights · this week</Eyebrow>
            <Col gap={11}>
              {c.insights.map((ins, i) => (
                <Card key={i} pad={16} flat>
                  <Row gap={13} align="flex-start">
                    <div style={{ width: 40, height: 40, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}><Icon name={ins.icon} size={20} color="var(--ink-2)" /></div>
                    <div style={{ flex: 1 }}>
                      <Row justify="space-between"><span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700, textTransform: 'uppercase' }}>{ins.type}</span><Tag style={{ border: ins.tone === 'watch' ? '1px solid var(--line-3)' : 'none' }}>{ins.tone === 'good' ? '✓ On track' : '! Watch'}</Tag></Row>
                      <div style={{ fontSize: 13, lineHeight: 1.5, marginTop: 7, color: 'var(--ink-2)' }}>{ins.text}</div>
                    </div>
                  </Row>
                </Card>
              ))}
            </Col>
          </div>
        </div>
        {/* right — chat panel */}
        <div style={{ width: 380, flexShrink: 0, borderLeft: '1px solid var(--line)', background: 'var(--card)', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ padding: '16px 18px', borderBottom: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
            <CoachMark size={32} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14, fontWeight: 800 }}>Chat with Coach</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)' }}>Log meals, weight, workouts via chat</div>
            </div>
            <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
              <div style={{ width: 7, height: 7, borderRadius: 999, background: 'var(--ink)' }} />
              <span style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)', fontWeight: 600 }}>ONLINE</span>
            </div>
          </div>
          <ChatWithLogging D={D} compact={true} initialThread={thread} />
        </div>
      </div>
    </>
  );
}

/* ═══════════════ SETTINGS ═══════════════ */
function SettingsDesktop({ nav, D }) {
  const [tab, setTab] = React.useState('Profile');
  const tabs = ['Profile', 'Goals & targets', 'Units', 'Reminders', 'Connected', 'Data'];
  return (
    <>
      <DesktopTopBar title="Settings" />
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <div style={{ width: 220, flexShrink: 0, borderRight: '1px solid var(--line)', padding: 16, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {tabs.map(t => (
            <button key={t} onClick={() => setTab(t)} style={{ textAlign: 'left', height: 38, padding: '0 12px', borderRadius: 'var(--r-md)', border: 'none', cursor: 'pointer', background: tab === t ? 'var(--paper-2)' : 'transparent', fontSize: 13, fontWeight: tab === t ? 700 : 500, color: tab === t ? 'var(--ink)' : 'var(--ink-2)' }}>{t}</button>
          ))}
        </div>
        <div className="bo-scroll" style={{ flex: 1, overflowY: 'auto', padding: 30 }}>
          <div style={{ maxWidth: 620 }}>
            {/* Profile */}
            <Card pad={20} style={{ marginBottom: 18 }}>
              <Row gap={16}><Avatar initials={D.user.initials} size={64} ring /><div style={{ flex: 1 }}><div style={{ fontSize: 19, fontWeight: 800 }}>{D.user.name}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'var(--ink-3)', marginTop: 3 }}>{D.user.job} · {D.user.age} yrs · {D.user.height} cm</div></div><Btn size="sm" variant="secondary" icon="edit">Edit</Btn></Row>
            </Card>
            <Eyebrow style={{ marginBottom: 12 }}>Goals & targets</Eyebrow>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 18 }}>
              <Field label="Start weight" value="107.0" suffix="kg" />
              <Field label="Goal weight" value="77.0" suffix="kg" />
              <Field label="Weekly target" value="1.15" suffix="kg/wk" />
              <Field label="Daily calories" value="2,100" suffix="kcal" />
              <Field label="Protein target" value="200" suffix="g" />
              <Field label="Goal date" value="Oct 23, 2026" icon="cal" />
            </div>
            <Eyebrow style={{ marginBottom: 12 }}>Connected services</Eyebrow>
            <Card pad={0} flat style={{ marginBottom: 18 }}>
              {[['Apple Health', 'Steps · weight sync', true],['Google Fit', 'Not connected', false],['Withings scale', 'Auto weigh-in', true]].map(([n, s, on], i) => (
                <div key={n} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', borderBottom: i < 2 ? '1px solid var(--line)' : 'none' }}>
                  <div style={{ width: 36, height: 36, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="link" size={17} color="var(--ink-2)" /></div>
                  <div style={{ flex: 1 }}><div style={{ fontSize: 13.5, fontWeight: 600 }}>{n}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>{s}</div></div>
                  <Toggle on={on} />
                </div>
              ))}
            </Card>
            <Eyebrow style={{ marginBottom: 12 }}>Data</Eyebrow>
            <Row gap={12}><Btn variant="secondary" icon="download">Export CSV</Btn><Btn variant="secondary" icon="download">Export PDF report</Btn></Row>
          </div>
        </div>
      </div>
    </>
  );
}

window.DSCREENS = Object.assign(window.DSCREENS || {}, { 'd-progress': ProgressDesktop, 'd-coach': CoachDesktop, 'd-settings': SettingsDesktop });
