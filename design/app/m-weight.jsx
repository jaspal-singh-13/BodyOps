/* BodyOps · Mobile — Weight tracking */

function WeightScreen({ nav, D }) {
  const [range, setRange] = React.useState('6W');
  return (
    <>
      <MobileTopBar title="Weight" onBack={() => nav.back()}
        right={<Btn size="sm" icon="plus" onClick={() => nav.go('weight-entry')}>Log</Btn>} />
      <ScreenBody pad={14} gap={13}>
        {/* hero */}
        <Card pad={16}>
          <Row justify="space-between" align="flex-start">
            <div>
              <Eyebrow>Latest</Eyebrow>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginTop: 4 }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 40, fontWeight: 700, lineHeight: 1 }}>{D.goal.current}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 16, color: 'var(--ink-3)' }}>kg</span>
              </div>
              <Row gap={6} style={{ marginTop: 8 }}>
                <Tag><Icon name="arrowD" size={10} /> 0.3 kg today</Tag>
                <Tag><Icon name="arrowD" size={10} /> {D.goal.lost} kg total</Tag>
              </Row>
            </div>
            <Ring value={D.goal.pctToGoal} size={84} stroke={8}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 17, fontWeight: 700 }}>{D.goal.pctToGoal}%</span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 8.5, color: 'var(--ink-3)', textTransform: 'uppercase', marginTop: 1 }}>to goal</span>
            </Ring>
          </Row>
        </Card>

        {/* trend chart */}
        <Card pad={15}>
          <Row justify="space-between">
            <Eyebrow>Trend</Eyebrow>
            <div style={{ display: 'flex', gap: 5 }}>
              {['2W','6W','6M'].map(r => <Chip key={r} active={range === r} onClick={() => setRange(r)} style={{ height: 26, padding: '0 9px', fontSize: 10.5 }}>{r}</Chip>)}
            </div>
          </Row>
          <div style={{ marginTop: 12 }}>
            <WeightChart data={D.weightWeekly} goal={D.goal.goal} height={170} />
          </div>
        </Card>

        {/* insight */}
        <Card pad={14} style={{ background: 'var(--card-2)' }}>
          <Row gap={10} align="flex-start">
            <CoachMark size={34} />
            <div style={{ flex: 1, fontSize: 12.5, lineHeight: 1.5 }}>
              Your loss is <b>steeper than plan</b> — averaging 1.4 kg/week vs your 1.15 kg target. At this pace you'll hit 77 kg around <b>Sep 21</b>.
            </div>
          </Row>
        </Card>

        {/* averages */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <AvgCard label="7-day avg" v={D.weightAvg.week} prev={D.weightAvg.lastWeek} />
          <AvgCard label="30-day avg" v={D.weightAvg.month} prev={D.weightAvg.prevMonth} />
        </div>

        {/* log */}
        <Eyebrow style={{ paddingLeft: 4 }}>Recent entries</Eyebrow>
        <Card pad={0} flat>
          {D.weightLog.map((e, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', borderBottom: i < D.weightLog.length - 1 ? '1px solid var(--line)' : 'none' }}>
              <div style={{ width: 42 }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)' }}>{e.day.toUpperCase()}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 600 }}>{e.date.split(' ')[1]}</div>
              </div>
              <div style={{ flex: 1 }}>
                {e.tag && <Tag style={{ fontSize: 8.5 }}>{e.tag}</Tag>}
              </div>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: e.delta < 0 ? 'var(--ink)' : 'var(--ink-3)', fontWeight: 600 }}>
                {e.delta > 0 ? '+' : ''}{e.delta}
              </span>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 15, fontWeight: 700, width: 56, textAlign: 'right' }}>{e.w}</span>
            </div>
          ))}
        </Card>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

function AvgCard({ label, v, prev }) {
  const diff = (v - prev).toFixed(1);
  return (
    <Card pad={13} flat>
      <Eyebrow>{label}</Eyebrow>
      <div style={{ fontFamily: 'var(--mono)', fontSize: 22, fontWeight: 700, marginTop: 6 }}>{v}<span style={{ fontSize: 11, color: 'var(--ink-3)' }}> kg</span></div>
      <Row gap={4} style={{ marginTop: 4 }}>
        <Icon name="arrowD" size={12} color="var(--ink-2)" />
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-2)' }}>{Math.abs(diff)} kg vs prev</span>
      </Row>
    </Card>
  );
}

/* ───────────────────────── Weight entry ──────────────────────────────────── */
function WeightEntryScreen({ nav, D }) {
  const [val, setVal] = React.useState('98.4');
  const press = (k) => setVal(v => {
    if (k === 'del') return v.length > 1 ? v.slice(0, -1) : '0';
    if (k === '.') return v.includes('.') ? v : v + '.';
    return (v === '0' ? '' : v) + k;
  });
  const diff = (parseFloat(val) - D.weightLog[1].w).toFixed(1);
  return (
    <>
      <MobileTopBar title="Log weight" onBack={() => nav.back()} sub="Friday · June 6 · 07:02" />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 20 }}>
          <Eyebrow>This morning</Eyebrow>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 64, fontWeight: 700, lineHeight: 1, letterSpacing: -1 }}>{val}</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 22, color: 'var(--ink-3)' }}>kg</span>
          </div>
          <Row gap={6} style={{ marginTop: 4 }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontFamily: 'var(--mono)', fontSize: 12, fontWeight: 600, color: 'var(--ink-2)', background: 'var(--paper-2)', padding: '5px 10px', borderRadius: 999 }}>
              <Icon name={diff <= 0 ? 'arrowD' : 'arrowU'} size={13} /> {Math.abs(diff)} kg from yesterday
            </span>
          </Row>
          <div style={{ marginTop: 18, display: 'flex', gap: 16 }}>
            <Stat label="Yesterday" value={`${D.weightLog[1].w} kg`} />
            <div style={{ width: 1, background: 'var(--line)' }} />
            <Stat label="7-day avg" value={`${D.weightAvg.week} kg`} />
            <div style={{ width: 1, background: 'var(--line)' }} />
            <Stat label="Goal" value={`${D.goal.goal} kg`} />
          </div>
        </div>
        {/* keypad */}
        <div style={{ flexShrink: 0, padding: '8px 14px 14px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
            {['1','2','3','4','5','6','7','8','9','.','0','del'].map(k => (
              <button key={k} onClick={() => press(k)} style={{ height: 52, borderRadius: 'var(--r-md)', border: '1px solid var(--line)', background: 'var(--card)', fontFamily: 'var(--mono)', fontSize: 20, fontWeight: 600, color: 'var(--ink)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {k === 'del' ? <Icon name="back" size={20} /> : k}
              </button>
            ))}
          </div>
          <Btn full size="lg" icon="check" style={{ marginTop: 10 }} onClick={() => nav.reset('weight')}>Save weight</Btn>
        </div>
      </div>
    </>
  );
}

window.MSCREENS = Object.assign(window.MSCREENS || {}, { weight: WeightScreen, 'weight-entry': WeightEntryScreen });
