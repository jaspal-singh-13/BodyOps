/* BodyOps · Conversational Logging — AI chat that can log anything.
   detectIntent(text) → {type, ...} or null
   ChatWithLogging — full drop-in chat UI supporting meal/weight/workout logging.
   Exports to window. */

/* ─── Intent detection ─────────────────────────────────────────────────── */
const FOOD_DB = {
  'protein shake': { kcal:160, p:30, c:8, f:3 }, 'whey': { kcal:120, p:25, c:3, f:2 },
  'chicken': { kcal:165, p:31, c:0, f:3.6 }, 'breast': { kcal:165, p:31, c:0, f:3.6 },
  'rice': { kcal:200, p:4, c:44, f:0.4 }, 'oats': { kcal:150, p:5, c:27, f:3 },
  'eggs': { kcal:140, p:12, c:1, f:10 }, 'egg': { kcal:70, p:6, c:0.5, f:5 },
  'banana': { kcal:90, p:1, c:23, f:0.3 }, 'apple': { kcal:72, p:0.4, c:19, f:0.2 },
  'bread': { kcal:120, p:4, c:22, f:1.5 }, 'wrap': { kcal:220, p:8, c:36, f:5 },
  'salad': { kcal:80, p:3, c:10, f:3 }, 'broccoli': { kcal:55, p:3.7, c:11, f:0.6 },
  'coffee': { kcal:5, p:0, c:1, f:0 }, 'milk': { kcal:60, p:3.2, c:4.8, f:3.3 },
  'greek yogurt': { kcal:100, p:17, c:6, f:0.7 }, 'yogurt': { kcal:100, p:17, c:6, f:0.7 },
  'pizza': { kcal:280, p:12, c:34, f:10 }, 'burger': { kcal:480, p:28, c:40, f:22 },
  'salmon': { kcal:180, p:25, c:0, f:8 }, 'tuna': { kcal:150, p:33, c:0, f:1 },
  'pasta': { kcal:220, p:8, c:43, f:1.3 }, 'granola': { kcal:200, p:5, c:36, f:6 },
};
const MEAL_SLOTS = { breakfast:['08:00'],lunch:['13:00'],dinner:['19:00'],snack:['16:00'] };
const WORKOUT_KEYWORDS = ['workout','gym','training','session','push day','pull day','legs','chest','back','shoulders','bench','squat','deadlift','press','row','curl','finished','completed','did my','crushed'];
const WEIGHT_KEYWORDS = ['weighed','weight','scale','morning weight','check in','check-in'];

function detectIntent(text) {
  const t = text.toLowerCase();
  // Weight intent
  const kgMatch = t.match(/\b(\d{2,3}(?:\.\d{1,2})?)\s*kg\b/);
  const isWeightCtx = WEIGHT_KEYWORDS.some(w => t.includes(w)) || (kgMatch && !WORKOUT_KEYWORDS.some(w => t.includes(w)));
  if (kgMatch && isWeightCtx) {
    return { type: 'weight', value: parseFloat(kgMatch[1]) };
  }
  // Workout intent
  const isWorkout = WORKOUT_KEYWORDS.some(w => t.includes(w));
  if (isWorkout) {
    const exMatch = t.match(/(\d{2,3}(?:\.\d)?)\s*kg/);
    const repsMatch = t.match(/(\d+)\s*(?:rep|reps|x)/);
    return { type: 'workout', raw: text, weight: exMatch ? parseFloat(exMatch[1]) : null, reps: repsMatch ? parseInt(repsMatch[1]) : null,
      session: t.includes('push') ? 'Push Day A' : t.includes('pull') ? 'Pull Day A' : t.includes('leg') ? 'Legs A' : 'Session' };
  }
  // Meal intent — look for food words or meal contexts
  const mealCtxKw = ['had','ate','eat','eating','for breakfast','for lunch','for dinner','having','just had','just ate','drank','drinking'];
  const foundMealCtx = mealCtxKw.some(w => t.includes(w));
  const detectedFoods = Object.entries(FOOD_DB).filter(([food]) => t.includes(food));
  if (foundMealCtx || detectedFoods.length > 0) {
    const slotKw = Object.keys(MEAL_SLOTS).find(s => t.includes(s));
    const slot = slotKw ? slotKw.charAt(0).toUpperCase() + slotKw.slice(1) : 'Meal';
    // Build detected items
    let items = detectedFoods.map(([name, n]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), ...n }));
    if (items.length === 0) {
      // Infer from context
      items = [{ name: 'Mixed meal (estimated)', kcal: 450, p: 35, c: 45, f: 12 }];
    }
    const totals = items.reduce((a, it) => ({ kcal: a.kcal + it.kcal, p: a.p + it.p, c: a.c + it.c, f: a.f + it.f }), { kcal:0,p:0,c:0,f:0 });
    return { type: 'meal', slot, items, totals, conf: detectedFoods.length > 0 ? 'high' : 'med' };
  }
  return null;
}

/* ─── AI response generator ─────────────────────────────────────────────── */
function generateResponse(text, intent, D) {
  if (!intent) {
    const fallbacks = [
      "Got it. Is there anything you'd like me to log or track right now?",
      "Noted. Want me to update your plan based on that?",
      "I hear you. You're on track today — anything specific I can help with?",
      "Understood. Keep going — you're 32 days ahead of schedule.",
    ];
    return fallbacks[Math.floor(Math.random() * fallbacks.length)];
  }
  if (intent.type === 'weight') {
    const diff = (intent.value - D.weightLog[0].w).toFixed(1);
    return `Got it — logging ${intent.value} kg. ${diff > 0 ? 'Up' : 'Down'} ${Math.abs(diff)} kg from yesterday. Trend is still pointing the right direction.`;
  }
  if (intent.type === 'meal') {
    return `Nice — I've broken that down for you below. Confirm when you're happy with the numbers.`;
  }
  if (intent.type === 'workout') {
    return `Strong work. I've captured that ${intent.session} session — ${intent.weight ? `${intent.weight} kg noted` : 'volume logged'}. I'll update your progression targets for next time.`;
  }
}

/* ─── Log action cards ───────────────────────────────────────────────────── */
function WeightLogCard({ intent, D, onConfirm }) {
  const [done, setDone] = React.useState(false);
  const diff = (intent.value - D.goal.current).toFixed(1);
  if (done) return (
    <div style={{ padding: '11px 14px', background: 'var(--paper-2)', borderRadius: 'var(--r-md)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: 9 }}>
      <Icon name="check" size={16} color="var(--ink)" stroke={2.6} /><span style={{ fontFamily: 'var(--mono)', fontSize: 12.5, fontWeight: 700, color: 'var(--ink)' }}>{intent.value} kg logged ✓</span>
    </div>
  );
  return (
    <div style={{ background: 'var(--card)', border: '1.5px solid var(--line-3)', borderRadius: 'var(--r-md)', overflow: 'hidden', width: '100%', maxWidth: 320 }}>
      <div style={{ padding: '13px 15px', display: 'flex', alignItems: 'center', gap: 14 }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 30, fontWeight: 700, lineHeight: 1 }}>{intent.value}</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}>kg</div>
        </div>
        <div style={{ flex: 1, borderLeft: '1px solid var(--line)', paddingLeft: 14 }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 10.5, color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: 0.06 }}>Vs last entry</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 16, fontWeight: 700, marginTop: 3, display: 'flex', alignItems: 'center', gap: 5 }}>
            <Icon name={diff <= 0 ? 'arrowD' : 'arrowU'} size={14} />
            {Math.abs(diff)} kg
          </div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)', marginTop: 3 }}>Previous: {D.goal.current} kg</div>
        </div>
      </div>
      <div style={{ padding: '10px 14px 13px', borderTop: '1px solid var(--line)', display: 'flex', gap: 8 }}>
        <Btn full size="sm" icon="check" onClick={() => { setDone(true); onConfirm && onConfirm(intent); }}>Log {intent.value} kg</Btn>
        <Btn variant="ghost" size="sm">Edit</Btn>
      </div>
    </div>
  );
}

function MealLogCard({ intent, onConfirm }) {
  const [done, setDone] = React.useState(false);
  const t = intent.totals;
  if (done) return (
    <div style={{ padding: '11px 14px', background: 'var(--paper-2)', borderRadius: 'var(--r-md)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: 9 }}>
      <Icon name="check" size={16} color="var(--ink)" stroke={2.6} /><span style={{ fontFamily: 'var(--mono)', fontSize: 12.5, fontWeight: 700 }}>{intent.slot} logged — {t.kcal} kcal · {t.p}g P ✓</span>
    </div>
  );
  return (
    <div style={{ background: 'var(--card)', border: '1.5px solid var(--line-3)', borderRadius: 'var(--r-md)', overflow: 'hidden', width: '100%', maxWidth: 320 }}>
      <div style={{ padding: '11px 14px 8px', borderBottom: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', color: 'var(--ink-2)' }}>{intent.slot}</span>
        <Confidence level={intent.conf} />
      </div>
      <div style={{ padding: '8px 14px' }}>
        {intent.items.map((it, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: i < intent.items.length - 1 ? '1px solid var(--line)' : 'none' }}>
            <span style={{ fontSize: 12.5, fontWeight: 600 }}>{it.name}</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)' }}>{it.kcal} kcal · P{it.p}g</span>
          </div>
        ))}
      </div>
      <div style={{ padding: '10px 14px', background: 'var(--card-2)', display: 'flex', gap: 16 }}>
        {[['kcal',t.kcal],['P',t.p+'g'],['C',t.c+'g'],['F',t.f+'g']].map(([l,v]) => (
          <div key={l}><div style={{ fontFamily: 'var(--mono)', fontSize: 14, fontWeight: 700 }}>{v}</div><div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-3)', textTransform: 'uppercase' }}>{l}</div></div>
        ))}
      </div>
      <div style={{ padding: '10px 14px 13px', borderTop: '1px solid var(--line)', display: 'flex', gap: 8 }}>
        <Btn full size="sm" icon="check" onClick={() => { setDone(true); onConfirm && onConfirm(intent); }}>Log meal</Btn>
        <Btn variant="ghost" size="sm" icon="edit">Edit</Btn>
      </div>
    </div>
  );
}

function WorkoutLogCard({ intent, onConfirm }) {
  const [done, setDone] = React.useState(false);
  if (done) return (
    <div style={{ padding: '11px 14px', background: 'var(--paper-2)', borderRadius: 'var(--r-md)', border: '1px solid var(--line)', display: 'flex', alignItems: 'center', gap: 9 }}>
      <Icon name="check" size={16} color="var(--ink)" stroke={2.6} /><span style={{ fontFamily: 'var(--mono)', fontSize: 12.5, fontWeight: 700 }}>{intent.session} logged ✓</span>
    </div>
  );
  return (
    <div style={{ background: 'var(--card)', border: '1.5px solid var(--line-3)', borderRadius: 'var(--r-md)', overflow: 'hidden', width: '100%', maxWidth: 320 }}>
      <div style={{ padding: '12px 14px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ width: 40, height: 40, borderRadius: 'var(--r-md)', background: 'var(--fill-ink)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <Icon name="workout" size={21} color="#fff" /></div>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700 }}>{intent.session}</div>
          {intent.weight && <div style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--ink-3)', marginTop: 2 }}>
            {intent.weight} kg{intent.reps ? ` × ${intent.reps} reps` : ''} detected</div>}
        </div>
      </div>
      <div style={{ padding: '10px 14px 13px', borderTop: '1px solid var(--line)', display: 'flex', gap: 8 }}>
        <Btn full size="sm" icon="check" onClick={() => { setDone(true); onConfirm && onConfirm(intent); }}>Log session</Btn>
        <Btn variant="ghost" size="sm">Add notes</Btn>
      </div>
    </div>
  );
}

function LogActionCard({ intent, D, onConfirm }) {
  if (!intent) return null;
  if (intent.type === 'weight') return <WeightLogCard intent={intent} D={D} onConfirm={onConfirm} />;
  if (intent.type === 'meal') return <MealLogCard intent={intent} onConfirm={onConfirm} />;
  if (intent.type === 'workout') return <WorkoutLogCard intent={intent} onConfirm={onConfirm} />;
  return null;
}

/* ─── ChatWithLogging component ─────────────────────────────────────────── */
function ChatWithLogging({ D, compact = false, initialThread }) {
  const thread = initialThread || D.coach.thread;
  const [messages, setMessages] = React.useState(
    thread.map(m => ({ ...m, id: Math.random() }))
  );
  const [input, setInput] = React.useState('');
  const scrollRef = React.useRef(null);
  const suggestions = [
    'I just weighed 98.2 kg',
    'Had chicken, rice & broccoli for lunch',
    'Finished push day — bench pressed 65 kg × 7',
    'Had a protein shake just now',
    'Is my protein too low?',
    'What should I eat tonight?',
  ];
  React.useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);
  const send = (text) => {
    if (!text.trim()) return;
    setInput('');
    const intent = detectIntent(text);
    const responseText = generateResponse(text, intent, D);
    const newMsgs = [
      { from: 'user', text, id: Math.random() },
      { from: 'coach', text: responseText, intent, id: Math.random() },
    ];
    setMessages(prev => [...prev, ...newMsgs]);
  };
  const bubbleR = compact ? 12 : 14;
  return (
    <>
      <div ref={scrollRef} className="bo-scroll" style={{ flex: 1, overflowY: 'auto', padding: compact ? '12px 14px' : 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((m, i) => (
          <div key={m.id || i} style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: m.from === 'coach' ? 'flex-start' : 'flex-end' }}>
            {m.from === 'coach' ? (
              <>
                <Row gap={8} align="flex-start" style={{ maxWidth: '90%' }}>
                  <CoachMark size={28} />
                  <div style={{ background: 'var(--paper)', border: '1px solid var(--line)', borderRadius: `4px ${bubbleR}px ${bubbleR}px ${bubbleR}px`, padding: '10px 13px', fontSize: compact ? 12.5 : 13, lineHeight: 1.5 }}>{m.text}</div>
                </Row>
                {m.intent && <div style={{ paddingLeft: 36 }}><LogActionCard intent={m.intent} D={D} /></div>}
              </>
            ) : (
              <div style={{ maxWidth: '82%', background: 'var(--fill-ink)', color: '#fff', borderRadius: `${bubbleR}px ${bubbleR}px 4px ${bubbleR}px`, padding: '10px 13px', fontSize: compact ? 12.5 : 13, lineHeight: 1.5, alignSelf: 'flex-end' }}>{m.text}</div>
            )}
          </div>
        ))}
      </div>
      {/* suggestions */}
      <div style={{ flexShrink: 0, borderTop: '1px solid var(--line)', padding: compact ? '8px 12px' : '10px 14px' }}>
        <div className="bo-scroll" style={{ display: 'flex', gap: 6, overflowX: 'auto', marginBottom: 8 }}>
          {suggestions.map((s, i) => <Chip key={i} onClick={() => send(s)} style={{ flexShrink: 0, fontSize: compact ? 10.5 : 11 }}>{s}</Chip>)}
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <div onKeyDown={e => e.key === 'Enter' && send(input)}
            contentEditable suppressContentEditableWarning
            onInput={e => setInput(e.currentTarget.textContent)}
            className="focusable" style={{ flex: 1, minHeight: 44, maxHeight: 120, overflowY: 'auto', borderRadius: 'var(--r-pill)', border: '1.5px solid var(--line-2)', background: 'var(--paper)', display: 'flex', alignItems: 'center', padding: '11px 16px', fontSize: 13.5, color: input ? 'var(--ink)' : 'var(--ink-4)', outline: 'none', cursor: 'text' }}
            data-placeholder="Log something or ask your coach…"
          />
          <button onClick={() => send(input || suggestions[Math.floor(Math.random()*3)])} style={{ width: 46, height: 46, borderRadius: 999, background: 'var(--fill-ink)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', flexShrink: 0 }}>
            <Icon name="send" size={19} color="#fff" />
          </button>
        </div>
      </div>
      <style>{`[data-placeholder]:empty:before{content:attr(data-placeholder);color:var(--ink-4);pointer-events:none}`}</style>
    </>
  );
}

Object.assign(window, { detectIntent, generateResponse, LogActionCard, WeightLogCard, MealLogCard, WorkoutLogCard, ChatWithLogging });
