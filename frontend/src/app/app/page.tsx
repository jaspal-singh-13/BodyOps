/**
 * Dashboard page — redesigned to match design/BodyOps.html layout.
 *
 * Layout:
 *   - Top header bar: title + date + Day N + streak + Log meal / Weigh in CTAs
 *   - 2-column grid (desktop): left = weight hero + nutrition + missions + trend chart
 *                               right = coach briefing + today's workout
 */

"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Dumbbell,
  Moon,
  Camera,
  Scale,
  Flame,
  CheckCircle2,
  Circle,
  Sparkles,
  TrendingDown,
  Footprints,
} from "lucide-react";
import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  ReferenceLine,
} from "recharts";
import { apiFetch } from "@/lib/api";
import { useRefresh } from "@/lib/refresh";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Settings {
  name: string;
  current_weight_kg: number;
  goal_weight_kg: number;
  calorie_target: number;
  protein_target_g: number;
  start_date: string;
}

interface HistoryItem {
  date: string;
  weight_kg: number;
  change_kg: number | null;
}

interface TrendData {
  projected_goal_date: string | null;
  moving_avg: { date: string; weight_kg: number; ma_7: number | null }[];
  total_loss_kg: number | null;
}

interface TodayWorkout {
  day_name: string;
  is_rest_day: boolean;
  exercises: { exercise_name: string }[];
  estimated_duration_min: number;
}

interface DailyNutrition {
  date: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  target_calories: number;
  target_protein_g: number;
  target_carbs_g: number;
  target_fat_g: number;
  meals_count: number;
}

interface MissionTask {
  id: string;
  name: string;
  description: string;
  task_type: string;
  completed: boolean;
  completed_at: string | null;
}

interface DailyMissions {
  date: string;
  tasks: MissionTask[];
  total: number;
  completed: number;
  percentage: number;
  streak: number;
}

interface CoachDaily {
  summary: string;
  focus: string[];
  next_step: string;
  generated_at: string;
  cached: boolean;
}

interface ProgressPreview {
  calorie_avg_7d: number;
  protein_avg_7d: number;
  weight_trend: { seven_day_avg: number | null; total_loss_kg: number | null };
}

interface StepsHistoryItem {
  date: string;
  steps: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function daysBetween(a: string, b: string) {
  return Math.round(
    (new Date(b).getTime() - new Date(a).getTime()) / 86_400_000
  );
}

function fmtDate(d: Date) {
  return d.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const router = useRouter();
  const { refreshKey } = useRefresh();

  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [latestWeight, setLatestWeight] = useState<HistoryItem | null>(null);
  const [firstWeight, setFirstWeight] = useState<number | null>(null);
  const [weightHistory7d, setWeightHistory7d] = useState<HistoryItem[]>([]);
  const [projectedDate, setProjectedDate] = useState<string | null>(null);
  const [projectedRaw, setProjectedRaw] = useState<string | null>(null);
  const [trendData, setTrendData] = useState<TrendData | null>(null);
  const [todayWorkout, setTodayWorkout] = useState<TodayWorkout | null | "loading">("loading");
  const [nutrition, setNutrition] = useState<DailyNutrition | null>(null);
  const [missions, setMissions] = useState<DailyMissions | null>(null);
  const [weightLoggedToday, setWeightLoggedToday] = useState(false);
  const [coachDaily, setCoachDaily] = useState<CoachDaily | null>(null);
  const [progressPreview, setProgressPreview] = useState<ProgressPreview | null>(null);
  const [todaySteps, setTodaySteps] = useState<number | null>(null);
  const [greeting, setGreeting] = useState("Good morning");

  const fetchAll = useCallback(() => {
    const today = (() => {
      const d = new Date();
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    })();

    apiFetch<Settings>("/settings")
      .then((data) => setSettings(data))
      .catch(() => router.push("/onboarding"))
      .finally(() => setLoading(false));

    apiFetch<HistoryItem[]>("/weight/history")
      .then((h) => {
        if (h.length > 0) {
          setLatestWeight(h[0]);
          setWeightLoggedToday(h[0].date === today);
          setFirstWeight(h[h.length - 1].weight_kg);
          setWeightHistory7d(h.slice(0, 7).reverse());
        } else {
          setLatestWeight(null);
          setWeightLoggedToday(false);
          setFirstWeight(null);
          setWeightHistory7d([]);
        }
      })
      .catch(() => {});

    apiFetch<TrendData>("/weight/trend")
      .then((t) => {
        setTrendData(t);
        const raw = t.projected_goal_date;
        if (raw) {
          const d = new Date(raw + "T00:00:00");
          setProjectedDate(
            d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "2-digit" })
          );
          setProjectedRaw(raw);
        } else {
          setProjectedDate(null);
          setProjectedRaw(null);
        }
      })
      .catch(() => {});

    apiFetch<TodayWorkout>("/workouts/today")
      .then((tw) => setTodayWorkout(tw))
      .catch(() => setTodayWorkout(null));

    apiFetch<DailyNutrition>("/meals/today")
      .then(setNutrition)
      .catch(() => {});

    apiFetch<DailyMissions>("/tasks/today")
      .then(setMissions)
      .catch(() => {});

    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    apiFetch<CoachDaily>("/coach/daily", { headers: { "X-Timezone": tz } })
      .then((d) =>
        setCoachDaily({
          summary: d.summary,
          focus: d.focus ?? [],
          next_step: d.next_step ?? "",
          generated_at: d.generated_at ?? "",
          cached: d.cached,
        })
      )
      .catch(() => {});

    apiFetch<ProgressPreview>("/progress/summary", { headers: { "X-Timezone": tz } })
      .then(setProgressPreview)
      .catch(() => {});

    apiFetch<StepsHistoryItem[]>("/steps/history")
      .then((h) => {
        const entry = h.find((s) => s.date === today);
        setTodaySteps(entry?.steps ?? null);
      })
      .catch(() => {});
  }, [router]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll, refreshKey]);

  useEffect(() => {
    function onVisibility() {
      if (document.visibilityState === "visible") fetchAll();
    }
    document.addEventListener("visibilitychange", onVisibility);
    return () => document.removeEventListener("visibilitychange", onVisibility);
  }, [fetchAll]);

  useEffect(() => {
    const hour = new Date().getHours();
    setGreeting(hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening");
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400 text-sm">Loading…</p>
      </div>
    );
  }

  if (!settings) return null;

  const displayWeight = latestWeight?.weight_kg ?? settings.current_weight_kg;
  const remaining = displayWeight - settings.goal_weight_kg;
  const startWeight = firstWeight ?? settings.current_weight_kg;
  const kgLost = startWeight - displayWeight;
  const progressPct = Math.min(100, Math.max(0, (kgLost / Math.max(0.1, startWeight - settings.goal_weight_kg)) * 100));

  // Day N calculation
  const todayStr = (() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  })();
  const dayN = settings.start_date ? Math.max(1, daysBetween(settings.start_date, todayStr) + 1) : null;
  const totalDays =
    settings.start_date && projectedRaw
      ? Math.max(dayN ?? 1, daysBetween(settings.start_date, projectedRaw) + 1)
      : null;
  const todayDelta = weightLoggedToday ? latestWeight?.change_kg ?? null : null;

  return (
    <div className="p-4 md:p-6 flex flex-col gap-4 min-h-full">
      {/* ── Header bar ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-extrabold text-zinc-900 tracking-tight">Dashboard</h1>
          <p className="font-mono text-[11px] text-zinc-500 uppercase tracking-widest mt-0.5">
            {fmtDate(new Date())}
            {dayN && (
              <span className="text-zinc-400"> · Day {dayN}{totalDays ? ` of ${totalDays}` : ""}</span>
            )}
          </p>
        </div>
        {/* Streak + CTA buttons */}
        <div className="flex items-center gap-2">
          {missions && missions.streak > 0 && (
            <span className="inline-flex items-center gap-1 font-mono text-[10.5px] font-bold text-orange-600 bg-orange-50 px-2.5 py-1.5 rounded-xl uppercase tracking-wider">
              <Flame size={11} />
              {missions.streak}-day streak
            </span>
          )}
          <Link href="/app/weight">
            <button className="h-9 px-4 rounded-xl border border-zinc-200 bg-white text-[13px] font-semibold text-zinc-700 flex items-center gap-2 hover:bg-zinc-50 transition-colors shadow-sm">
              <Scale size={15} className="text-zinc-500" />
              {weightLoggedToday ? "Logged ✓" : "Weigh in"}
            </button>
          </Link>
          <Link href="/app/meals?mode=camera">
            <button className="h-9 px-4 rounded-xl bg-zinc-900 text-[13px] font-semibold text-white flex items-center gap-2 hover:bg-zinc-800 transition-colors shadow-sm">
              <Camera size={15} />
              Log meal
            </button>
          </Link>
        </div>
      </div>

      {/* ── 2-column grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-4">
        {/* LEFT column */}
        <div className="flex flex-col gap-4">
          {/* Weight hero */}
          <WeightHeroCard
            displayWeight={displayWeight}
            kgLost={kgLost}
            remaining={remaining}
            startWeight={startWeight}
            startDate={settings.start_date}
            goalWeight={settings.goal_weight_kg}
            progressPct={progressPct}
            projectedDate={projectedDate}
            projectedRaw={projectedRaw}
            todayDelta={todayDelta}
          />

          {/* Nutrition + Missions side-by-side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
            <NutritionCard nutrition={nutrition} />
            <MissionsCard missions={missions} nutrition={nutrition} latestWeight={latestWeight} />
          </div>

          {/* Weight trend chart */}
          {weightHistory7d.length >= 2 && (
            <WeightTrendCard
              data={weightHistory7d}
              trendData={trendData}
              goalWeight={settings.goal_weight_kg}
            />
          )}
        </div>

        {/* RIGHT column */}
        <div className="flex flex-col gap-4">
          <CoachBriefingCard coach={coachDaily} />
          <TodayWorkoutCard workout={todayWorkout} />
          <StepsDashCard steps={todaySteps} />
          {progressPreview && (
            <WeeklyStatsCard preview={progressPreview} />
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Weight Hero Card
// ---------------------------------------------------------------------------

function WeightHeroCard({
  displayWeight, kgLost, remaining, startWeight, startDate, goalWeight,
  progressPct, projectedDate, projectedRaw, todayDelta,
}: {
  displayWeight: number; kgLost: number; remaining: number; startWeight: number;
  startDate: string; goalWeight: number; progressPct: number;
  projectedDate: string | null; projectedRaw: string | null; todayDelta: number | null;
}) {
  const startLabel = startDate
    ? new Date(startDate + "T00:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "2-digit" })
    : null;

  // Days early/late vs goal-weight-date projection relative to today
  const daysToGoal = projectedRaw
    ? Math.round((new Date(projectedRaw).getTime() - Date.now()) / 86_400_000)
    : null;

  return (
    <div className="bg-zinc-900 rounded-2xl p-5 shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-[10px] tracking-widest font-semibold uppercase text-white/50">
            Current weight
          </p>
          <div className="flex items-center gap-2.5 mt-1.5">
            <div className="flex items-baseline gap-1.5">
              <span className="font-mono text-[42px] font-bold text-white leading-none">{displayWeight}</span>
              <span className="font-mono text-[16px] text-white/60">kg</span>
            </div>
            {todayDelta != null && todayDelta !== 0 && (
              <span className="inline-flex items-center gap-0.5 font-mono text-[11px] font-bold text-white bg-white/10 px-2 py-1 rounded-full">
                {todayDelta < 0 ? "↓" : "↑"} {Math.abs(todayDelta).toFixed(1)} today
              </span>
            )}
          </div>
        </div>

        {/* 3 horizontal stats */}
        <div className="flex gap-5 text-right">
          <HeroStat value={`${Math.abs(kgLost).toFixed(1)}`} label={kgLost >= 0 ? "kg lost" : "kg gained"} />
          <HeroStat value={`${Math.abs(remaining).toFixed(1)}`} label="kg to goal" />
          <HeroStat value={`${Math.round(progressPct)}%`} label="complete" />
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-5">
        <div className="h-2 rounded-full overflow-hidden bg-white/15">
          <div className="h-full bg-white rounded-full transition-all" style={{ width: `${progressPct}%` }} />
        </div>
        <div className="flex justify-between mt-1.5 font-mono text-[10px] text-white/50">
          <span>{startWeight} kg{startLabel ? ` · ${startLabel}` : ""}</span>
          <span>{goalWeight} kg goal</span>
        </div>
      </div>

      {projectedDate && (
        <div className="mt-3 pt-3 border-t border-white/10 flex items-center gap-2">
          <span className="text-base">🎯</span>
          <span className="text-[12.5px] text-white/80">
            On pace for <b className="text-white">{projectedDate}</b>
            {daysToGoal != null && daysToGoal > 0 && (
              <span className="text-white/50"> · {daysToGoal} days out</span>
            )}
          </span>
        </div>
      )}
    </div>
  );
}

function HeroStat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <p className="font-mono text-[18px] font-bold text-white leading-none">{value}</p>
      <p className="font-mono text-[9px] uppercase tracking-wider text-white/50 mt-1">{label}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Nutrition Card
// ---------------------------------------------------------------------------

function NutritionCard({ nutrition }: { nutrition: DailyNutrition | null }) {
  const empty = !nutrition || nutrition.meals_count === 0;

  return (
    <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
      <div className="flex items-center justify-between mb-4">
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
          Today · Nutrition
        </p>
        {nutrition && (
          <span className="font-mono text-[10.5px] text-zinc-400">
            {nutrition.meals_count} meal{nutrition.meals_count !== 1 ? "s" : ""} logged
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        <DonutStat
          value={nutrition?.calories ?? 0}
          total={nutrition?.target_calories ?? 2000}
          label="kcal"
          size={108}
          stroke={11}
        />
        <div className="flex-1 flex flex-col gap-3">
          <MacroLine label="Protein" v={nutrition?.protein_g ?? 0} t={nutrition?.target_protein_g ?? 150} />
          <MacroLine label="Carbs" v={nutrition?.carbs_g ?? 0} t={nutrition?.target_carbs_g ?? 200} />
          <MacroLine label="Fat" v={nutrition?.fat_g ?? 0} t={nutrition?.target_fat_g ?? 65} />
        </div>
      </div>

      {empty && (
        <p className="font-mono text-[10.5px] text-zinc-400 text-center mt-3">
          Log your first meal to start tracking
        </p>
      )}
    </div>
  );
}

function DonutStat({ value, total, label, size, stroke }: {
  value: number; total: number; label: string; size: number; stroke: number;
}) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(1, Math.max(0, value / Math.max(1, total)));
  const dash = pct * circ;
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e4e3df" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1d1c1a" strokeWidth={stroke}
          strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-[15px] font-bold leading-none">{value.toLocaleString()}</span>
        <span className="font-mono text-[9px] text-zinc-400 mt-0.5">{label}</span>
      </div>
    </div>
  );
}

function MacroLine({ label, v, t }: { label: string; v: number; t: number }) {
  const pct = Math.min(100, Math.max(0, (v / Math.max(1, t)) * 100));
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-[12px] font-semibold text-zinc-600">{label}</span>
        <span className="font-mono text-[11px] text-zinc-400">
          <b className="text-zinc-900">{Math.round(v)}</b> / {Math.round(t)}g
        </span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-zinc-100 overflow-hidden">
        <div className="h-full rounded-full bg-zinc-900 transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Daily Missions Card (with live values)
// ---------------------------------------------------------------------------

function MissionsCard({
  missions,
  nutrition,
  latestWeight,
}: {
  missions: DailyMissions | null;
  nutrition: DailyNutrition | null;
  latestWeight: { weight_kg: number } | null;
}) {
  if (!missions) return null;

  const allDone = missions.total > 0 && missions.completed === missions.total;

  function getTaskValue(task: MissionTask): string | null {
    switch (task.task_type) {
      case "log_weight":
        return latestWeight ? `${latestWeight.weight_kg} kg` : null;
      case "protein_target":
        if (!nutrition) return null;
        return `${Math.round(nutrition.protein_g)} / ${Math.round(nutrition.target_protein_g)} g`;
      case "calorie_target":
        if (!nutrition) return null;
        return `${Math.round(nutrition.calories).toLocaleString()} / ${Math.round(nutrition.target_calories).toLocaleString()} kcal`;
      default:
        return null;
    }
  }

  const r = 52 / 2 - 6 / 2;
  const circ = 2 * Math.PI * r;
  const pct = missions.total > 0 ? missions.completed / missions.total : 0;
  const dash = pct * circ;

  return (
    <Link href="/app/missions">
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4 cursor-pointer hover:bg-zinc-50 transition-colors">
        <div className="flex items-center justify-between mb-3">
          <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
            {allDone ? "All done 🎯" : "Daily Missions"}
          </p>
          <span className="font-mono text-[10.5px] text-zinc-400">
            {missions.completed}/{missions.total} complete
          </span>
        </div>

        <div className="flex items-center gap-4">
          {/* Ring */}
          <div className="relative shrink-0" style={{ width: 52, height: 52 }}>
            <svg width={52} height={52} viewBox="0 0 52 52">
              <circle cx={26} cy={26} r={r} fill="none" stroke="#e4e3df" strokeWidth={6} />
              <circle cx={26} cy={26} r={r} fill="none"
                stroke={allDone ? "#16a34a" : "#1d1c1a"} strokeWidth={6}
                strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="round"
                transform="rotate(-90 26 26)" />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="font-mono text-[11px] font-bold">{missions.completed}/{missions.total}</span>
            </div>
          </div>

          {/* Tasks with values */}
          <div className="flex-1 flex flex-col gap-2">
            {missions.tasks.map((task) => {
              const val = getTaskValue(task);
              return (
                <div key={task.id} className="flex items-center gap-2">
                  {task.completed ? (
                    <CheckCircle2 size={13} className="text-green-600 shrink-0" />
                  ) : (
                    <Circle size={13} className="text-zinc-300 shrink-0" />
                  )}
                  <span className={`text-[12px] flex-1 min-w-0 truncate ${task.completed ? "line-through text-zinc-400" : "text-zinc-700"}`}>
                    {task.name}
                  </span>
                  {val && (
                    <span className="font-mono text-[10px] text-zinc-400 shrink-0">{val}</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Weight Trend Chart
// ---------------------------------------------------------------------------

function WeightTrendCard({
  data,
  trendData,
  goalWeight,
}: {
  data: { date: string; weight_kg: number }[];
  trendData: TrendData | null;
  goalWeight: number;
}) {
  const chartData = data.map((d) => ({
    date: d.date.slice(5), // MM-DD
    weight: d.weight_kg,
  }));

  const vals = data.map((d) => d.weight_kg);
  const minVal = Math.min(...vals, goalWeight);
  const maxVal = Math.max(...vals);
  const yMin = Math.floor(minVal - 0.5);
  const yMax = Math.ceil(maxVal + 0.5);

  // Derive 7-day avg and weekly change from moving_avg
  const movingAvg = trendData?.moving_avg ?? [];
  const latestMa7 = movingAvg.slice().reverse().find((d) => d.ma_7 != null)?.ma_7 ?? null;
  const weeklyChange = (() => {
    if (data.length < 2) return null;
    const latest = data[data.length - 1].weight_kg;
    const weekAgo = data[0].weight_kg;
    return +(latest - weekAgo).toFixed(2);
  })();

  return (
    <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
            Weight Trend
          </p>
          {latestMa7 && (
            <p className="text-[13px] font-semibold text-zinc-900 mt-0.5">
              7-day avg: <span className="font-mono">{latestMa7.toFixed(1)} kg</span>
            </p>
          )}
        </div>
        {weeklyChange != null && (
          <span className={`inline-flex items-center gap-1 font-mono text-[11px] font-bold px-2.5 py-1 rounded-full ${
            weeklyChange <= 0 ? "text-green-700 bg-green-50" : "text-red-600 bg-red-50"
          }`}>
            <TrendingDown size={11} />
            {weeklyChange <= 0 ? "" : "+"}{weeklyChange.toFixed(2)} kg/wk
          </span>
        )}
      </div>

      <ResponsiveContainer width="100%" height={130}>
        <LineChart data={chartData} margin={{ top: 5, right: 8, bottom: 0, left: 0 }}>
          <XAxis
            dataKey="date"
            tick={{ fontSize: 9, fontFamily: "var(--font-geist-mono, monospace)", fill: "#a1a1aa" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis domain={[yMin, yMax]} hide />
          <Tooltip
            contentStyle={{ background: "#1d1c1a", border: "none", borderRadius: 8, fontSize: 11 }}
            labelStyle={{ color: "#a1a1aa", fontFamily: "monospace" }}
            itemStyle={{ color: "#fff", fontFamily: "monospace" }}
            formatter={(v) => [`${v} kg`, ""]}
          />
          {goalWeight >= yMin && goalWeight <= yMax && (
            <ReferenceLine y={goalWeight} stroke="#a1a1aa" strokeDasharray="3 3"
              label={{ value: `Goal ${goalWeight}kg`, fontSize: 9, fill: "#a1a1aa", position: "insideTopRight" }} />
          )}
          <Line
            type="monotone"
            dataKey="weight"
            stroke="#1d1c1a"
            strokeWidth={2}
            dot={{ r: 3, fill: "#1d1c1a", strokeWidth: 0 }}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Coach Briefing Card (right column)
// ---------------------------------------------------------------------------

function CoachBriefingCard({ coach }: { coach: CoachDaily | null }) {
  if (!coach) {
    return (
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-zinc-900 flex items-center justify-center shrink-0">
            <Sparkles size={15} color="#fff" />
          </div>
          <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
            Coach Briefing
          </p>
        </div>
        <p className="text-[12.5px] text-zinc-400 leading-relaxed">
          Complete your first mission to unlock daily coaching.
        </p>
      </div>
    );
  }

  const updatedLabel = coach.generated_at
    ? new Date(coach.generated_at).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })
    : null;

  // Suggestion chips: next_step first, then focus items (max 2 total)
  const chips = [coach.next_step, ...coach.focus].filter((s) => s && s.trim().length > 0).slice(0, 2);

  return (
    <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-lg bg-zinc-900 flex items-center justify-center shrink-0">
          <Sparkles size={15} color="#fff" />
        </div>
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
          Coach Briefing
        </p>
        {updatedLabel && (
          <span className="ml-auto font-mono text-[9.5px] text-zinc-400">Updated {updatedLabel}</span>
        )}
      </div>

      <p className="text-[13px] text-zinc-700 leading-relaxed line-clamp-5">
        {coach.summary}
      </p>

      {chips.length > 0 && (
        <div className="flex flex-col gap-1.5 mt-3">
          {chips.map((chip, i) => (
            <div
              key={i}
              className="flex items-start gap-2 rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2"
            >
              <CheckCircle2 size={13} className="text-zinc-400 shrink-0 mt-0.5" />
              <span className="text-[12px] text-zinc-700 leading-snug">{chip}</span>
            </div>
          ))}
        </div>
      )}

      <Link href="/app/coach" className="block mt-3">
        <button className="w-full h-9 rounded-xl border border-zinc-200 bg-white text-[12.5px] font-semibold text-zinc-700 flex items-center justify-center gap-1.5 hover:bg-zinc-50 transition-colors">
          <Sparkles size={13} className="text-zinc-500" />
          Open coach
        </button>
      </Link>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Today's Workout Card
// ---------------------------------------------------------------------------

function TodayWorkoutCard({ workout }: { workout: TodayWorkout | null | "loading" }) {
  if (workout === "loading") return null;

  if (workout === null) {
    return (
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase mb-3">
          Today&apos;s Workout
        </p>
        <p className="text-sm text-zinc-400">
          Import a workout plan to unlock this card.{" "}
          <Link href="/app/workouts" className="text-zinc-700 underline">
            Import plan
          </Link>
        </p>
      </div>
    );
  }

  if (workout.is_rest_day) {
    return (
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase mb-3">
          Today&apos;s Workout
        </p>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-zinc-50 flex items-center justify-center shrink-0">
            <Moon size={18} className="text-zinc-400" />
          </div>
          <p className="text-[15px] font-bold text-zinc-900">Rest Day</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
      <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase mb-3">
        Today&apos;s Workout
      </p>
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-zinc-100 flex items-center justify-center shrink-0">
          <Dumbbell size={18} className="text-zinc-700" />
        </div>
        <div>
          <p className="text-[15px] font-bold text-zinc-900">{workout.day_name}</p>
          <p className="font-mono text-[10.5px] text-zinc-400 mt-0.5">
            {workout.exercises.length} exercises · ~{workout.estimated_duration_min} min
          </p>
        </div>
      </div>
      <Link href="/app/workouts" className="btn-primary block text-center text-sm px-4">
        Start session
      </Link>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Weekly Stats Card (bottom of right column)
// ---------------------------------------------------------------------------

function WeeklyStatsCard({ preview }: { preview: ProgressPreview }) {
  const hasData = preview.calorie_avg_7d > 0 || preview.protein_avg_7d > 0;
  if (!hasData) return null;

  return (
    <Link href="/app/progress">
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4 cursor-pointer hover:bg-zinc-50 transition-colors">
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase mb-3">
          This Week
        </p>
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-zinc-50 rounded-xl p-2.5">
            <p className="font-mono text-[9px] text-zinc-400 uppercase tracking-wider mb-0.5">Avg kcal</p>
            <p className="font-mono text-[15px] font-bold text-zinc-900 leading-none">
              {preview.calorie_avg_7d > 0 ? Math.round(preview.calorie_avg_7d).toLocaleString() : "—"}
            </p>
          </div>
          <div className="bg-zinc-50 rounded-xl p-2.5">
            <p className="font-mono text-[9px] text-zinc-400 uppercase tracking-wider mb-0.5">Avg protein</p>
            <p className="font-mono text-[15px] font-bold text-zinc-900 leading-none">
              {preview.protein_avg_7d > 0 ? `${Math.round(preview.protein_avg_7d)}g` : "—"}
            </p>
          </div>
        </div>
        <p className="font-mono text-[10px] text-zinc-400 mt-2 text-right">View full progress →</p>
      </div>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Steps Dashboard Card
// ---------------------------------------------------------------------------

const _STEPS_GOAL = 10_000;

function StepsDashCard({ steps }: { steps: number | null }) {
  const pct = steps != null ? Math.min(100, (steps / _STEPS_GOAL) * 100) : 0;
  const R = 19;
  const circ = 2 * Math.PI * R;
  const fill = (pct / 100) * circ;

  return (
    <Link href="/app/steps">
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4 cursor-pointer hover:bg-zinc-50 transition-colors">
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase mb-3">
          Today · Steps
        </p>
        {steps != null ? (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-zinc-50 flex items-center justify-center shrink-0">
              <Footprints size={18} className="text-zinc-700" />
            </div>
            <div className="flex-1">
              <p className="font-mono text-[18px] font-bold text-zinc-900 leading-none">
                {steps.toLocaleString()}
              </p>
              <p className="font-mono text-[10px] text-zinc-400 mt-0.5">
                {Math.round(pct)}% of {_STEPS_GOAL.toLocaleString()} goal
              </p>
            </div>
            <svg width={48} height={48} viewBox="0 0 48 48" style={{ transform: "rotate(-90deg)", flexShrink: 0 }}>
              <circle cx={24} cy={24} r={R} fill="none" stroke="#e4e3df" strokeWidth={5} />
              <circle cx={24} cy={24} r={R} fill="none" stroke="#1d1c1a" strokeWidth={5}
                strokeDasharray={`${fill} ${circ - fill}`} strokeLinecap="round" />
            </svg>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-zinc-50 flex items-center justify-center shrink-0">
              <Footprints size={18} className="text-zinc-400" />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-zinc-500">No steps logged yet</p>
              <p className="text-[11px] text-zinc-400 mt-0.5">Tap to log today&apos;s steps</p>
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}
