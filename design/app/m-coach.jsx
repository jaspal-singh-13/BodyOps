/* BodyOps · Mobile — AI Coach (summary + conversational) */

function CoachScreen({ nav, D }) {
  const c = D.coach;
  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px 8px', flexShrink: 0 }}>
        <Row gap={11}>
          <CoachMark size={40} />
          <div>
            <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: -0.3 }}>Coach</div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)' }}>Updated 7:02 AM</div>
          </div>
        </Row>
        <button onClick={() => nav.go('coach-chat')} style={{ height: 38, padding: '0 13px', borderRadius: 'var(--r-md)', background: 'var(--card)', border: '1px solid var(--line-2)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 7, fontFamily: 'var(--sans)', fontSize: 13, fontWeight: 600 }}>
          <Icon name="coach" size={15} /> Chat
        </button>
      </div>
      <ScreenBody pad={14} gap={13}>
        {/* headline */}
        <Card pad={16} style={{ background: 'var(--fill-ink)', border: 'none' }}>
          <Eyebrow style={{ color: 'rgba(255,255,255,0.5)' }}>Daily briefing · Friday</Eyebrow>
          <div style={{ fontSize: 19, fontWeight: 800, color: '#fff', marginTop: 8, letterSpacing: -0.3, lineHeight: 1.25 }}>{c.headline}</div>
          <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.78)', lineHeight: 1.55, marginTop: 10 }}>{c.daily}</div>
        </Card>

        {/* action recommendations */}
        <Card pad={15}>
          <Row gap={8}><Icon name="bolt" size={16} fill color="var(--ink)" /><Eyebrow>Do these today</Eyebrow></Row>
          <Col gap={2} style={{ marginTop: 10 }}>
            {c.actions.map((a, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '11px 0', borderBottom: i < c.actions.length - 1 ? '1px solid var(--line)' : 'none' }}>
                <div style={{ width: 22, height: 22, borderRadius: 6, border: '1.5px solid var(--line-3)', flexShrink: 0 }} />
                <span style={{ flex: 1, fontSize: 13.5, fontWeight: 500 }}>{a}</span>
                <Icon name="chevR" size={15} color="var(--ink-4)" />
              </div>
            ))}
          </Col>
        </Card>

        {/* insight cards */}
        <Eyebrow style={{ paddingLeft: 4 }}>Insights</Eyebrow>
        <Col gap={9}>
          {c.insights.map((ins, i) => (
            <Card key={i} pad={14} flat>
              <Row gap={11} align="flex-start">
                <div style={{ width: 36, height: 36, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon name={ins.icon} size={18} color="var(--ink-2)" /></div>
                <div style={{ flex: 1 }}>
                  <Row justify="space-between">
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.04 }}>{ins.type}</span>
                    <Tag style={{ background: ins.tone === 'good' ? 'var(--paper-2)' : 'transparent', border: ins.tone === 'watch' ? '1px solid var(--line-3)' : 'none' }}>
                      {ins.tone === 'good' ? '✓ On track' : '! Watch'}</Tag>
                  </Row>
                  <div style={{ fontSize: 12.5, lineHeight: 1.5, marginTop: 7, color: 'var(--ink-2)' }}>{ins.text}</div>
                </div>
              </Row>
            </Card>
          ))}
        </Col>

        {/* weekly review entry */}
        <Card pad={15} onClick={() => nav.tab('progress')}>
          <Row justify="space-between">
            <Row gap={11}>
              <div style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', background: 'var(--paper-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="cal" size={19} /></div>
              <div><div style={{ fontSize: 14, fontWeight: 700 }}>Weekly review</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 1 }}>Ready · Week 6 recap</div></div>
            </Row>
            <Icon name="chevR" size={17} color="var(--ink-3)" />
          </Row>
        </Card>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

/* ───────────────────────── Conversational coach (full-bleed) ──────────────── */
function CoachChatScreen({ nav, D }) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--paper)', minHeight: 0 }}>
      <MobileTopBar title="Coach" onBack={() => nav.back()} sub="Log anything · ask anything"
        right={<div style={{ display: 'flex', alignItems: 'center', gap: 6, marginRight: 4 }}>
          <div style={{ width: 7, height: 7, borderRadius: 999, background: 'var(--ink)' }} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)', fontWeight: 600 }}>ONLINE</span>
        </div>} />
      <div style={{ flexShrink: 0, padding: '8px 14px', borderBottom: '1px solid var(--line)', background: 'var(--card-2)' }}>
        <div style={{ display: 'flex', gap: 7, overflowX: 'auto' }} className="bo-scroll">
          {['Log a meal 🍽','Log my weight ⚖️','Log workout 💪'].map((hint, i) => (
            <span key={i} style={{ flexShrink: 0, fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-2)', background: 'var(--paper-2)', padding: '5px 10px', borderRadius: 999, border: '1px solid var(--line-2)' }}>{hint}</span>
          ))}
        </div>
      </div>
      <ChatWithLogging D={D} initialThread={D.coach.thread} />
    </div>
  );
}

window.MSCREENS = Object.assign(window.MSCREENS || {}, { coach: CoachScreen, 'coach-chat': CoachChatScreen });
