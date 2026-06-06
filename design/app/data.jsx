/* BodyOps · Mock data — user "Alex Chen", IT, 30y, 107→77kg, 5–6 gym days/wk.
   Realistic, internally consistent. Exports window.DATA */

const DATA = {
  user: {
    name: 'Alex Chen', initials: 'AC', age: 30, job: 'Software Engineer',
    height: 182, sex: 'Male', startDate: 'Apr 24, 2026', today: 'Jun 6, 2026',
    dayN: 44, planWeeks: 26,
  },

  goal: {
    start: 107.0, current: 98.4, goal: 77.0,
    lost: 8.6, remaining: 21.4, rate: 1.4,            // kg/week
    pctToGoal: Math.round((8.6 / 30) * 100),           // 29%
    projDate: 'Sep 21, 2026', planEndDate: 'Oct 23, 2026',
    aheadDays: 32,
  },

  // weekly average weights (7 points)
  weightWeekly: [
    { d: 'W1', w: 107.0 }, { d: 'W2', w: 105.1 }, { d: 'W3', w: 103.6 },
    { d: 'W4', w: 102.0 }, { d: 'W5', w: 100.7 }, { d: 'W6', w: 99.5 }, { d: 'Now', w: 98.4 },
  ],
  // recent daily log
  weightLog: [
    { date: 'Jun 6', day: 'Fri', w: 98.4, delta: -0.3, tag: 'Today' },
    { date: 'Jun 5', day: 'Thu', w: 98.7, delta: -0.2 },
    { date: 'Jun 4', day: 'Wed', w: 98.9, delta: +0.1 },
    { date: 'Jun 3', day: 'Tue', w: 98.8, delta: -0.4 },
    { date: 'Jun 2', day: 'Mon', w: 99.2, delta: -0.1 },
    { date: 'Jun 1', day: 'Sun', w: 99.3, delta: +0.2 },
    { date: 'May 31', day: 'Sat', w: 99.1, delta: -0.4 },
    { date: 'May 30', day: 'Fri', w: 99.5, delta: -0.2 },
  ],
  weightAvg: { week: 98.8, lastWeek: 99.9, month: 100.6, prevMonth: 103.4 },

  nutrition: {
    cal: { v: 1420, target: 2100 }, protein: { v: 142, target: 200 },
    carbs: { v: 158, target: 210 }, fat: { v: 39, target: 60 },
    water: { v: 2.5, target: 4.0 }, steps: { v: 7430, target: 10000 },
  },

  mealsToday: [
    { id: 'm1', time: '08:15', slot: 'Breakfast', title: 'Greek yogurt bowl',
      items: ['Greek yogurt', 'Granola', 'Blueberries'], kcal: 420, p: 32, c: 48, f: 11, conf: 'high' },
    { id: 'm2', time: '13:30', slot: 'Lunch', title: 'Chicken, rice & broccoli',
      items: ['Grilled chicken', 'Jasmine rice', 'Broccoli'], kcal: 640, p: 58, c: 70, f: 14, conf: 'high' },
    { id: 'm3', time: '16:00', slot: 'Snack', title: 'Protein shake + banana',
      items: ['Whey shake', 'Banana'], kcal: 360, p: 52, c: 40, f: 6, conf: 'med' },
  ],

  // the meal currently being analysed (camera → AI flow), the lunch plate
  analyzeMeal: {
    title: 'Chicken, rice & broccoli', kcal: 640, p: 58, c: 70, f: 14, conf: 'high',
    detected: [
      { name: 'Grilled chicken breast', qty: '180 g', kcal: 297, p: 56, c: 0, f: 6, conf: 'high' },
      { name: 'Jasmine rice', qty: '150 g', kcal: 195, p: 4, c: 44, f: 1, conf: 'high' },
      { name: 'Steamed broccoli', qty: '80 g', kcal: 28, p: 2, c: 6, f: 0, conf: 'med' },
      { name: 'Olive oil (drizzle)', qty: '~1 tbsp', kcal: 120, p: 0, c: 0, f: 14, conf: 'low' },
    ],
  },

  mealHistory: [
    { date: 'Today · Jun 6', total: 1420, p: 142, meals: 3 },
    { date: 'Yesterday · Jun 5', total: 2040, p: 198, meals: 4 },
    { date: 'Wed · Jun 4', total: 1980, p: 205, meals: 4 },
    { date: 'Tue · Jun 3', total: 2110, p: 191, meals: 5 },
  ],

  missions: [
    { id: 'logw', label: 'Log morning weight', meta: '98.4 kg', done: true, icon: 'weight' },
    { id: 'prot', label: 'Hit protein goal', meta: '142 / 200 g', done: false, prog: 71, icon: 'meal' },
    { id: 'cal',  label: 'Stay under calorie target', meta: '1,420 / 2,100', done: false, prog: 68, icon: 'target', onTrack: true },
    { id: 'work', label: 'Complete workout', meta: 'Push Day A', done: false, icon: 'workout' },
    { id: 'step', label: 'Walk 10,000 steps', meta: '7,430 / 10,000', done: false, prog: 74, icon: 'steps' },
    { id: 'water',label: 'Drink 4L water', meta: '2.5 / 4.0 L', done: false, prog: 63, icon: 'water' },
    { id: 'sleep',label: 'Sleep before 23:30', meta: 'Tonight', done: false, icon: 'moon' },
  ],
  missionStats: { done: 1, total: 7, streak: 12, bestStreak: 18, weekRate: 86 },

  workout: {
    today: 'Push Day A', split: 'Push · Pull · Legs', week: 'Week 7', dayLabel: 'Day 2 of 6',
    duration: '~58 min', exercisesN: 6, lastTrained: '2 days ago',
    plan: [
      { day: 'Mon', name: 'Pull Day A', done: true, focus: 'Back · Biceps' },
      { day: 'Tue', name: 'Push Day A', today: true, focus: 'Chest · Shoulders · Triceps' },
      { day: 'Wed', name: 'Legs A', focus: 'Quads · Hams · Calves' },
      { day: 'Thu', name: 'Pull Day B', focus: 'Back · Biceps' },
      { day: 'Fri', name: 'Push Day B', focus: 'Chest · Shoulders' },
      { day: 'Sat', name: 'Legs B', focus: 'Quads · Glutes' },
      { day: 'Sun', name: 'Rest', rest: true },
    ],
    exercises: [
      { id: 'bench', name: 'Barbell Bench Press', muscle: 'Chest', sets: 4,
        lastW: 60, lastR: 8, sugW: 62.5, sugR: '6+', note: 'Hit 8 reps last time — load up.', up: true },
      { id: 'incdb', name: 'Incline DB Press', muscle: 'Upper chest', sets: 3,
        lastW: 24, lastR: 10, sugW: 26, sugR: '8+', up: true },
      { id: 'ohp', name: 'Overhead Press', muscle: 'Shoulders', sets: 3,
        lastW: 40, lastR: 6, sugW: 40, sugR: '8', note: 'Stay at 40 — build reps to 8 first.', up: false },
      { id: 'fly', name: 'Cable Fly', muscle: 'Chest', sets: 3,
        lastW: 15, lastR: 12, sugW: 17.5, sugR: '10+', up: true },
      { id: 'push', name: 'Triceps Pushdown', muscle: 'Triceps', sets: 3,
        lastW: 25, lastR: 12, sugW: 27.5, sugR: '10+', up: true },
      { id: 'lat', name: 'Lateral Raise', muscle: 'Side delts', sets: 3,
        lastW: 10, lastR: 15, sugW: 12, sugR: '12+', up: true },
    ],
    // for active-session detail (bench)
    activeSets: [
      { set: 1, w: 62.5, target: '6+', reps: 8, done: true },
      { set: 2, w: 62.5, target: '6+', reps: 7, done: true },
      { set: 3, w: 62.5, target: '6+', reps: 6, done: false, current: true },
      { set: 4, w: 62.5, target: '6+', reps: null, done: false },
    ],
    summary: {
      name: 'Push Day A', duration: '54 min', volume: '6,840 kg', sets: 18,
      prs: 2, exercises: 6,
      prList: ['Bench Press · 62.5 kg × 8', 'Cable Fly · 17.5 kg × 11'],
    },
  },

  coach: {
    headline: "You're 32 days ahead of schedule.",
    daily: "Weight's trending down nicely — down 1.1 kg this week. You've got a Push session today; last bench was strong so I've bumped you to 62.5 kg. One gap: protein. You're averaging 168 g but the target is 200 g. Let's close that with a shake after the gym.",
    insights: [
      { type: 'Weight', icon: 'weight', tone: 'good', text: '7-day average down 1.1 kg. Trend is steeper than your 1.4 kg/wk plan — you\'re ahead.' },
      { type: 'Nutrition', icon: 'meal', tone: 'watch', text: 'Protein hit target only 3 of 7 days. Aim to front-load it at breakfast.' },
      { type: 'Workout', icon: 'workout', tone: 'good', text: '6 of 6 sessions completed last week. Bench and rows both progressed.' },
    ],
    actions: [
      'Add a 50 g protein shake post-workout today',
      'Push bench to 62.5 kg × 6+',
      'Get a 20-min walk in — you\'re 2,570 steps short',
    ],
    thread: [
      { from: 'coach', text: "Morning, Alex. Down to 98.4 kg — that's 8.6 kg gone. How are you feeling going into today's Push session?" },
      { from: 'user', text: "Good but my left shoulder's a little tight." },
      { from: 'coach', text: "Noted. Let's keep Overhead Press at 40 kg today instead of adding load, and add a thorough warm-up set. If it flares up, swap to machine press. Want me to adjust the session?" },
      { from: 'user', text: "Yeah do that." },
      { from: 'coach', text: "Done ✓ Overhead Press held at 40 kg, machine press queued as a backup. Everything else still progresses. Go get it." },
    ],
    suggestions: ['Why am I not losing faster?', 'Plan my refeed day', 'Is my protein too low?'],
  },

  reminders: [
    { id: 'weigh', label: 'Morning weigh-in', time: '07:00', days: 'Every day', on: true, icon: 'weight' },
    { id: 'protein', label: 'Protein check-in', time: '15:00', days: 'Every day', on: true, icon: 'meal' },
    { id: 'work', label: 'Workout reminder', time: '18:00', days: 'Mon–Sat', on: true, icon: 'workout' },
    { id: 'sleep', label: 'Wind down for sleep', time: '23:00', days: 'Every day', on: true, icon: 'moon' },
    { id: 'water', label: 'Hydration nudges', time: 'Every 2h', days: '09:00–21:00', on: false, icon: 'water' },
  ],

  progress: {
    calBars: [
      { d: 'Mon', v: 2040 }, { d: 'Tue', v: 1980 }, { d: 'Wed', v: 2110, under: false },
      { d: 'Thu', v: 1920 }, { d: 'Fri', v: 2050 }, { d: 'Sat', v: 2240, under: false }, { d: 'Sun', v: 1880 },
    ],
    proteinBars: [
      { d: 'Mon', v: 198 }, { d: 'Tue', v: 205 }, { d: 'Wed', v: 191, under: false },
      { d: 'Thu', v: 210 }, { d: 'Fri', v: 184, under: false }, { d: 'Sat', v: 201 }, { d: 'Sun', v: 142, under: false },
    ],
    // 8 weeks × 7 days habit completion (0..1)
    habit: [
      [1,1,.8,1,1,.6,1],[1,.8,1,1,1,1,.4],[1,1,1,.8,1,1,1],[.8,1,1,1,.6,1,1],
      [1,1,.8,1,1,1,.8],[1,1,1,1,1,.6,1],[.8,1,1,.8,1,1,1],[1,1,.8,1,.6,0,0],
    ],
    workoutConsistency: 92, // %
    habitCompletion: 86,
    weeklyLoss: [-1.9, -1.5, -1.6, -1.3, -1.2, -1.1],
  },

  milestones: [
    { id: 'kg5', title: 'First 5 kg gone', date: 'May 18', done: true, icon: 'trophy' },
    { id: 'streak30', title: '30-day login streak', meta: '12 / 30 days', prog: 40, done: false, icon: 'flame' },
    { id: 'kg10', title: '10 kg milestone', meta: '1.4 kg to go', prog: 86, done: false, icon: 'target' },
    { id: 'protein', title: 'Protein week', meta: '5 / 7 days', prog: 71, done: false, icon: 'meal' },
  ],

  // celebration shown on the success state
  celebrate: {
    big: '5 kg', title: 'First 5 kilos, gone.',
    body: "You hit 102.0 kg — that's 5 kg down from your start weight. The hardest part is starting, and you're already past it.",
    stat1: { v: '23 days', l: 'to get here' }, stat2: { v: '−1.6 kg', l: 'per week' },
    next: 'Next stop: 10 kg lost', nextMeta: '1.4 kg to go',
  },
};

window.DATA = DATA;
