/* BodyOps · Mobile — Meal logging flow */

function MealsScreen({ nav, D }) {
  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px 8px', flexShrink: 0 }}>
        <div>
          <Eyebrow>Nutrition</Eyebrow>
          <div style={{ fontSize: 21, fontWeight: 800, letterSpacing: -0.4, marginTop: 2 }}>Meals</div>
        </div>
        <button onClick={() => nav.go('meal-camera')} className="focusable" style={{ width: 42, height: 42, borderRadius: 'var(--r-md)', background: 'var(--fill-ink)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon name="camera" size={21} color="#fff" />
        </button>
      </div>
      <ScreenBody pad={14} gap={13}>
        {/* today summary */}
        <Card pad={15}>
          <Row justify="space-between">
            <Eyebrow>Today's intake</Eyebrow>
            <Tag>{D.nutrition.cal.target - D.nutrition.cal.v} kcal left</Tag>
          </Row>
          <Row gap={14} style={{ marginTop: 12 }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 26, fontWeight: 700 }}>{D.nutrition.cal.v.toLocaleString()}</span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ink-3)' }}>/ {D.nutrition.cal.target.toLocaleString()} kcal</span>
              </div>
              <Bar value={(D.nutrition.cal.v / D.nutrition.cal.target) * 100} h={6} style={{ marginTop: 8 }} />
            </div>
          </Row>
          <div style={{ display: 'flex', gap: 8, marginTop: 13 }}>
            {[['Protein', D.nutrition.protein], ['Carbs', D.nutrition.carbs], ['Fat', D.nutrition.fat]].map(([l, m]) => (
              <div key={l} style={{ flex: 1, background: 'var(--card-2)', border: '1px solid var(--line)', borderRadius: 'var(--r-sm)', padding: '9px 10px' }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: 0.04 }}>{l}</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 14, fontWeight: 700, marginTop: 2 }}>{m.v}<span style={{ fontSize: 10, color: 'var(--ink-3)', fontWeight: 500 }}>/{m.target}g</span></div>
              </div>
            ))}
          </div>
        </Card>

        {/* today meals */}
        <Eyebrow style={{ paddingLeft: 4 }}>Today · {D.mealsToday.length} logged</Eyebrow>
        <Col gap={9}>
          {D.mealsToday.map(m => <MealRow key={m.id} m={m} onClick={() => nav.go('meal-detail', { id: m.id })} />)}
        </Col>

        {/* earlier days */}
        <Eyebrow style={{ paddingLeft: 4, marginTop: 4 }}>Earlier</Eyebrow>
        <Col gap={9}>
          {D.mealHistory.slice(1).map((d, i) => (
            <Card key={i} pad={14} flat>
              <Row justify="space-between">
                <div>
                  <div style={{ fontSize: 13.5, fontWeight: 600 }}>{d.date}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>{d.meals} meals</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 15, fontWeight: 700 }}>{d.total.toLocaleString()}<span style={{ fontSize: 11, color: 'var(--ink-3)' }}> kcal</span></div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', marginTop: 1 }}>{d.p}g protein</div>
                </div>
              </Row>
            </Card>
          ))}
        </Col>
        <Spacer h={4} />
      </ScreenBody>
    </>
  );
}

function MealRow({ m, onClick }) {
  return (
    <Card pad={0} onClick={onClick} flat style={{ overflow: 'hidden', borderColor: 'var(--line-2)' }}>
      <Row gap={0} align="stretch">
        <ImageSlot label="" icon="meal" h={72} w={72} radius={0} style={{ borderRadius: 0, border: 'none', borderRight: '1px solid var(--line)' }} />
        <div style={{ flex: 1, padding: '11px 13px', minWidth: 0 }}>
          <Row justify="space-between">
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)', fontWeight: 600 }}>{m.time} · {m.slot.toUpperCase()}</span>
            <Confidence level={m.conf} showLabel={false} />
          </Row>
          <div style={{ fontSize: 14, fontWeight: 700, marginTop: 3, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{m.title}</div>
          <Row justify="space-between" style={{ marginTop: 5 }}>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11, fontWeight: 700 }}>{m.kcal} kcal</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)' }}>P{m.p} · C{m.c} · F{m.f}</span>
          </Row>
        </div>
      </Row>
    </Card>
  );
}

/* ───────────────────────── Camera capture (full-bleed) ───────────────────── */
function MealCameraScreen({ nav, D }) {
  return (
    <div style={{ flex: 1, background: '#1a1917', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      {/* top bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px', position: 'relative', zIndex: 3 }}>
        <button onClick={() => nav.back()} style={{ width: 38, height: 38, borderRadius: 999, background: 'rgba(255,255,255,0.12)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
          <Icon name="x" size={18} color="#fff" />
        </button>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 11.5, color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>SNAP YOUR MEAL</span>
        <button style={{ width: 38, height: 38, borderRadius: 999, background: 'rgba(255,255,255,0.12)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
          <Icon name="bolt" size={18} color="#fff" />
        </button>
      </div>
      {/* viewfinder */}
      <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="hatch" style={{ position: 'absolute', inset: 16, borderRadius: 'var(--r-lg)', background: '#26241f', borderColor: 'rgba(255,255,255,0.16)' }}>
          <span className="hatch-label" style={{ background: 'rgba(255,255,255,0.1)', borderColor: 'rgba(255,255,255,0.18)', color: 'rgba(255,255,255,0.7)' }}>CAMERA · LIVE PREVIEW</span>
        </div>
        {/* corner guides */}
        {[[16,16,'tl'],[16,16,'tr'],[16,16,'bl'],[16,16,'br']].map((c, i) => {
          const pos = ['tl','tr','bl','br'][i];
          const s = { position: 'absolute', width: 26, height: 26, borderColor: 'rgba(255,255,255,0.85)', borderStyle: 'solid', borderWidth: 0 };
          if (pos[0]==='t') { s.top = 38; s.borderTopWidth = 3; } else { s.bottom = 38; s.borderBottomWidth = 3; }
          if (pos[1]==='l') { s.left = 38; s.borderLeftWidth = 3; s.borderTopLeftRadius = pos[0]==='t'?10:0; s.borderBottomLeftRadius = pos[0]==='b'?10:0; }
          else { s.right = 38; s.borderRightWidth = 3; s.borderTopRightRadius = pos[0]==='t'?10:0; s.borderBottomRightRadius = pos[0]==='b'?10:0; }
          return <div key={i} style={s} />;
        })}
        <div style={{ position: 'absolute', bottom: 30, left: 0, right: 0, textAlign: 'center', fontFamily: 'var(--mono)', fontSize: 11, color: 'rgba(255,255,255,0.55)' }}>Center your plate in the frame</div>
      </div>
      {/* controls */}
      <div style={{ padding: '20px 16px 30px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative', zIndex: 3 }}>
        <button style={{ width: 48, height: 48, borderRadius: 'var(--r-md)', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.16)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
          <Icon name="meal" size={20} color="#fff" />
        </button>
        <button onClick={() => nav.go('meal-analyzing')} style={{ width: 74, height: 74, borderRadius: 999, background: 'transparent', border: '4px solid rgba(255,255,255,0.9)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0 }}>
          <div style={{ width: 58, height: 58, borderRadius: 999, background: '#fff' }} />
        </button>
        <button onClick={() => nav.go('meal-analyzing')} style={{ width: 48, height: 48, borderRadius: 'var(--r-md)', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.16)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', gap: 2 }}>
          <Icon name="edit" size={17} color="#fff" />
          <span style={{ fontFamily: 'var(--mono)', fontSize: 7.5, color: 'rgba(255,255,255,0.7)' }}>MANUAL</span>
        </button>
      </div>
    </div>
  );
}

/* ───────────────────────── AI analyzing (loading) ────────────────────────── */
function MealAnalyzingScreen({ nav, D }) {
  const [step, setStep] = React.useState(0);
  const steps = ['Detecting food items', 'Estimating portions', 'Calculating macros'];
  React.useEffect(() => {
    const t1 = setInterval(() => setStep(s => Math.min(s + 1, steps.length - 1)), 700);
    const t2 = setTimeout(() => nav.replace('meal-analysis'), 2400);
    return () => { clearInterval(t1); clearTimeout(t2); };
  }, []);
  return (
    <div style={{ flex: 1, background: 'var(--paper)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 28, gap: 22 }}>
      <div style={{ position: 'relative', width: 200, height: 200 }}>
        <ImageSlot label="MEAL PHOTO" icon="meal" h={200} w={200} radius="var(--r-lg)" />
        {/* scan line */}
        <div style={{ position: 'absolute', inset: 0, borderRadius: 'var(--r-lg)', overflow: 'hidden' }}>
          <div className="bo-scan" style={{ position: 'absolute', left: 0, right: 0, height: 3, background: 'var(--ink)', boxShadow: '0 0 12px 2px rgba(29,28,26,0.4)' }} />
        </div>
        <span style={{ position: 'absolute', top: 10, left: 10, fontFamily: 'var(--mono)', fontSize: 9, fontWeight: 700, background: 'var(--fill-ink)', color: '#fff', padding: '3px 6px', borderRadius: 4 }}>AI · ANALYZING</span>
      </div>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 17, fontWeight: 700 }}>Reading your plate…</div>
        <div style={{ fontFamily: 'var(--mono)', fontSize: 12, color: 'var(--ink-2)', marginTop: 10, height: 18 }}>{steps[step]}…</div>
      </div>
      <div style={{ display: 'flex', gap: 6 }}>
        {steps.map((_, i) => <div key={i} style={{ width: i === step ? 22 : 6, height: 6, borderRadius: 999, background: i <= step ? 'var(--ink)' : 'var(--fill-2)', transition: 'all .3s' }} />)}
      </div>
      <style>{`@keyframes boScan { 0%{top:4%} 100%{top:96%} } .bo-scan{ animation: boScan 1.1s ease-in-out infinite alternate; }`}</style>
    </div>
  );
}

/* ───────────────────────── AI analysis result / confirm ──────────────────── */
function MealAnalysisScreen({ nav, D }) {
  const meal = D.analyzeMeal;
  const [items, setItems] = React.useState(meal.detected);
  const totals = items.reduce((a, it) => ({ kcal: a.kcal + it.kcal, p: a.p + it.p, c: a.c + it.c, f: a.f + it.f }), { kcal: 0, p: 0, c: 0, f: 0 });
  const remove = (i) => setItems(items.filter((_, x) => x !== i));
  return (
    <>
      <MobileTopBar title="Review meal" onBack={() => nav.back()} sub="AI detected · tap to edit" />
      <ScreenBody pad={14} gap={13}>
        <div style={{ position: 'relative' }}>
          <ImageSlot label="MEAL PHOTO" icon="camera" h={150} radius="var(--r-lg)" />
          <span style={{ position: 'absolute', top: 10, left: 10, fontFamily: 'var(--mono)', fontSize: 9.5, fontWeight: 700, background: 'var(--fill-ink)', color: '#fff', padding: '4px 8px', borderRadius: 5, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            <Icon name="coach" size={11} color="#fff" /> {items.length} items found
          </span>
          <button style={{ position: 'absolute', bottom: 10, right: 10, height: 30, padding: '0 10px', borderRadius: 999, background: 'rgba(255,255,255,0.92)', border: '1px solid var(--line-2)', fontFamily: 'var(--mono)', fontSize: 10.5, fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: 5, cursor: 'pointer' }} onClick={() => nav.replace('meal-camera')}>
            <Icon name="camera" size={13} /> Retake
          </button>
        </div>

        {/* totals */}
        <Card pad={15}>
          <Row justify="space-between" align="center">
            <div>
              <div style={{ fontSize: 15, fontWeight: 700 }}>{meal.title}</div>
              <Row gap={6} style={{ marginTop: 4 }}><Eyebrow>Overall confidence</Eyebrow><Confidence level={meal.conf} /></Row>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 24, fontWeight: 700 }}>{totals.kcal}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)' }}>kcal total</div>
            </div>
          </Row>
          <div style={{ display: 'flex', gap: 8, marginTop: 13 }}>
            {[['P', totals.p],['C', totals.c],['F', totals.f]].map(([l, v]) => (
              <div key={l} style={{ flex: 1, background: 'var(--card-2)', border: '1px solid var(--line)', borderRadius: 'var(--r-sm)', padding: '8px 10px', textAlign: 'center' }}>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 700 }}>{v}g</div>
                <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-3)' }}>{l === 'P' ? 'PROTEIN' : l === 'C' ? 'CARBS' : 'FAT'}</div>
              </div>
            ))}
          </div>
        </Card>

        {/* detected items */}
        <Eyebrow style={{ paddingLeft: 4 }}>Detected items · tap to adjust</Eyebrow>
        <Col gap={8}>
          {items.map((it, i) => (
            <Card key={i} pad={12} flat style={{ borderColor: it.conf === 'low' ? 'var(--line-3)' : 'var(--line)' }}>
              <Row justify="space-between" align="flex-start">
                <div style={{ flex: 1, minWidth: 0 }}>
                  <Row gap={7}><span style={{ fontSize: 13.5, fontWeight: 600 }}>{it.name}</span></Row>
                  <Row gap={8} style={{ marginTop: 4 }}>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-2)' }}>{it.qty}</span>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}>· {it.kcal} kcal · P{it.p}</span>
                  </Row>
                  {it.conf === 'low' && <div style={{ marginTop: 7, fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-2)', background: 'var(--paper-2)', padding: '5px 8px', borderRadius: 5, display: 'inline-flex', gap: 5, alignItems: 'center' }}><Icon name="info" size={12} /> Low confidence — confirm portion</div>}
                </div>
                <Col gap={8} style={{ alignItems: 'flex-end' }}>
                  <Confidence level={it.conf} showLabel={false} />
                  <button onClick={() => remove(i)} style={{ width: 26, height: 26, borderRadius: 7, border: '1px solid var(--line-2)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                    <Icon name="x" size={13} color="var(--ink-3)" />
                  </button>
                </Col>
              </Row>
            </Card>
          ))}
          <button style={{ height: 44, borderRadius: 'var(--r-md)', border: '1.5px dashed var(--line-3)', background: 'transparent', fontFamily: 'var(--sans)', fontSize: 13.5, fontWeight: 600, color: 'var(--ink-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7, cursor: 'pointer' }}>
            <Icon name="plus" size={16} /> Add an item
          </button>
        </Col>
        <Spacer h={70} />
      </ScreenBody>
      {/* sticky confirm */}
      <div style={{ flexShrink: 0, padding: '12px 14px 14px', borderTop: '1px solid var(--line)', background: 'var(--card)', display: 'flex', gap: 10 }}>
        <select defaultValue="Lunch" style={{ height: 48, borderRadius: 'var(--r-md)', border: '1px solid var(--line-2)', background: 'var(--card)', fontFamily: 'var(--mono)', fontSize: 12.5, fontWeight: 600, padding: '0 12px', color: 'var(--ink)' }}>
          <option>Breakfast</option><option>Lunch</option><option>Dinner</option><option>Snack</option>
        </select>
        <Btn full size="lg" icon="check" onClick={() => nav.reset('meals')}>Confirm & log</Btn>
      </div>
    </>
  );
}

/* ───────────────────────── Meal detail ───────────────────────────────────── */
function MealDetailScreen({ nav, params, D }) {
  const m = D.mealsToday.find(x => x.id === params.id) || D.mealsToday[1];
  return (
    <>
      <MobileTopBar title={m.slot} onBack={() => nav.back()} sub={`${m.time} · today`}
        right={<button style={{ width: 38, height: 38, borderRadius: 'var(--r-md)', border: '1px solid var(--line-2)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}><Icon name="edit" size={17} /></button>} />
      <ScreenBody pad={14} gap={13}>
        <ImageSlot label="MEAL PHOTO" icon="camera" h={170} radius="var(--r-lg)" />
        <div>
          <div style={{ fontSize: 19, fontWeight: 800, letterSpacing: -0.3 }}>{m.title}</div>
          <Row gap={8} style={{ marginTop: 6 }}>
            <Tag><Icon name="coach" size={10} /> AI logged</Tag>
            <Confidence level={m.conf} />
          </Row>
        </div>
        <Card pad={15}>
          <Row justify="space-around">
            {[['Calories', m.kcal, 'kcal'],['Protein', m.p, 'g'],['Carbs', m.c, 'g'],['Fat', m.f, 'g']].map(([l, v, u], i) => (
              <React.Fragment key={l}>
                {i > 0 && <div style={{ width: 1, background: 'var(--line)', alignSelf: 'stretch' }} />}
                <div style={{ textAlign: 'center', flex: 1 }}>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 18, fontWeight: 700 }}>{v}</div>
                  <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-3)', textTransform: 'uppercase', marginTop: 2 }}>{l}</div>
                </div>
              </React.Fragment>
            ))}
          </Row>
        </Card>
        <Eyebrow style={{ paddingLeft: 4 }}>Items</Eyebrow>
        <Col gap={8}>
          {m.items.map((it, i) => (
            <Card key={i} pad={13} flat>
              <Row justify="space-between"><span style={{ fontSize: 13.5, fontWeight: 600 }}>{it}</span><Icon name="chevR" size={15} color="var(--ink-4)" /></Row>
            </Card>
          ))}
        </Col>
        <Spacer h={6} />
      </ScreenBody>
    </>
  );
}

window.MSCREENS = Object.assign(window.MSCREENS || {}, {
  meals: MealsScreen, 'meal-camera': MealCameraScreen, 'meal-analyzing': MealAnalyzingScreen,
  'meal-analysis': MealAnalysisScreen, 'meal-detail': MealDetailScreen,
});
