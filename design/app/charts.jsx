/* BodyOps · Charts — minimal grayscale SVG viz. Exports to window. */

/* Smooth-ish weight trend line with goal line + target band + actual dots */
function WeightChart({ data, goal, start, height = 180, showAxis = true, target }) {
  // data: [{d:'label', w:number}]
  const W = 600, H = height, padL = 4, padR = 4, padT = 16, padB = showAxis ? 26 : 8;
  const xs = data.map((_, i) => padL + (i / (data.length - 1)) * (W - padL - padR));
  const allW = data.map(d => d.w).concat([goal]);
  const min = Math.min(...allW) - 2, max = Math.max(...allW) + 2;
  const y = w => padT + (1 - (w - min) / (max - min)) * (H - padT - padB);
  const pts = data.map((d, i) => [xs[i], y(d.w)]);
  const path = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  const area = `${path} L${xs[xs.length-1]} ${H-padB} L${xs[0]} ${H-padB} Z`;
  const goalY = y(goal);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} preserveAspectRatio="none" style={{ display: 'block', overflow: 'visible' }}>
      <defs>
        <linearGradient id="wgFade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="rgba(29,28,26,0.10)" />
          <stop offset="1" stopColor="rgba(29,28,26,0)" />
        </linearGradient>
      </defs>
      {/* goal line */}
      <line x1="0" y1={goalY} x2={W} y2={goalY} stroke="var(--ink-3)" strokeWidth="1" strokeDasharray="5 4" />
      <text x={W-2} y={goalY-6} textAnchor="end" fontFamily="var(--mono)" fontSize="11" fontWeight="600" fill="var(--ink-3)">GOAL {goal}kg</text>
      <path d={area} fill="url(#wgFade)" />
      <path d={path} fill="none" stroke="var(--ink)" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      {/* endpoint */}
      <circle cx={pts[pts.length-1][0]} cy={pts[pts.length-1][1]} r="4.5" fill="var(--card)" stroke="var(--ink)" strokeWidth="2.5" />
      {showAxis && data.map((d, i) => (i % Math.ceil(data.length/6) === 0 || i === data.length-1) && (
        <text key={i} x={xs[i]} y={H-7} textAnchor={i===0?'start':i===data.length-1?'end':'middle'}
          fontFamily="var(--mono)" fontSize="10.5" fill="var(--ink-4)">{d.d}</text>
      ))}
    </svg>
  );
}

/* Vertical bar series — calories / protein adherence vs target */
function BarChart({ data, target, unit = '', height = 150, targetLabel = 'TARGET' }) {
  const W = 600, H = height, padT = 18, padB = 24, gap = 10;
  const max = Math.max(...data.map(d => d.v), target) * 1.12;
  const bw = (W - gap * (data.length - 1)) / data.length;
  const y = v => padT + (1 - v / max) * (H - padT - padB);
  const tY = y(target);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} preserveAspectRatio="none" style={{ display: 'block', overflow: 'visible' }}>
      {data.map((d, i) => {
        const x = i * (bw + gap);
        const barY = y(d.v);
        const under = d.under;
        return (
          <g key={i}>
            <rect x={x} y={barY} width={bw} height={H - padB - barY} rx="3"
              fill={under === false ? 'var(--fill-2)' : 'var(--ink)'} opacity={under === false ? 1 : 0.88} />
            <text x={x + bw/2} y={H-8} textAnchor="middle" fontFamily="var(--mono)" fontSize="10.5" fill="var(--ink-4)">{d.d}</text>
          </g>
        );
      })}
      <line x1="0" y1={tY} x2={W} y2={tY} stroke="var(--ink-2)" strokeWidth="1.2" strokeDasharray="5 4" />
      <text x={W-2} y={tY-6} textAnchor="end" fontFamily="var(--mono)" fontSize="10.5" fontWeight="600" fill="var(--ink-2)">{targetLabel} {target}{unit}</text>
    </svg>
  );
}

/* Sparkline — tiny inline trend */
function Sparkline({ data, width = 96, height = 30, stroke = 1.8 }) {
  const min = Math.min(...data), max = Math.max(...data);
  const xs = data.map((_, i) => (i / (data.length - 1)) * width);
  const y = v => height - 3 - ((v - min) / (max - min || 1)) * (height - 6);
  const path = data.map((v, i) => `${i ? 'L' : 'M'}${xs[i].toFixed(1)} ${y(v).toFixed(1)}`).join(' ');
  return (
    <svg width={width} height={height} style={{ display: 'block', overflow: 'visible' }}>
      <path d={path} fill="none" stroke="var(--ink)" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={xs[xs.length-1]} cy={y(data[data.length-1])} r="2.6" fill="var(--ink)" />
    </svg>
  );
}

/* Consistency dot-matrix — weeks × days habit heatmap */
function HabitGrid({ weeks, cols = 7, cell = 15, gap = 4, labels }) {
  // weeks: array of arrays of 0..1 completion
  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${cols}, ${cell}px)`, gap, width: 'max-content' }}>
        {weeks.flat().map((v, i) => (
          <div key={i} title={`${Math.round(v*100)}%`} style={{
            width: cell, height: cell, borderRadius: 3,
            background: v === 0 ? 'var(--fill)' : `rgba(29,28,26,${0.22 + v * 0.68})`,
            border: '1px solid rgba(29,28,26,0.04)',
          }} />
        ))}
      </div>
      {labels && (
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
          {labels.map((l, i) => <span key={i} style={{ fontFamily: 'var(--mono)', fontSize: 9.5, color: 'var(--ink-4)' }}>{l}</span>)}
        </div>
      )}
    </div>
  );
}

/* Big donut for daily macro ring stat */
function DonutStat({ value, total, label, unit, size = 116, stroke = 11 }) {
  const pct = Math.min(100, (value / total) * 100);
  return (
    <Ring value={pct} size={size} stroke={stroke}>
      <span style={{ fontFamily: 'var(--mono)', fontSize: size * 0.2, fontWeight: 700, color: 'var(--ink)', lineHeight: 1 }}>{value}</span>
      <span style={{ fontFamily: 'var(--mono)', fontSize: 10, color: 'var(--ink-3)', marginTop: 3 }}>/ {total}{unit}</span>
      {label && <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--ink-4)', textTransform: 'uppercase', letterSpacing: 0.06, marginTop: 2 }}>{label}</span>}
    </Ring>
  );
}

Object.assign(window, { WeightChart, BarChart, Sparkline, HabitGrid, DonutStat });
