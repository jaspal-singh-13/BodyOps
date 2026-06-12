/**
 * Dashboard page — landing page after login for authenticated users.
 *
 * Fetches settings, latest weight, trend, today's workout, and today's
 * nutrition in parallel. Redirects to `/onboarding` if settings are missing.
 *
 * Card stack (design/app/m-home.jsx order):
 *   1. Hero — weight progress
 *   3. Quick Actions — Log meal + Weigh in (Phase 4)
 *   4. Today · Nutrition — donut + macro bars (Phase 4)
 *   5. Today's workout
 */

"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Dumbbell, Moon, Camera, Scale, Flame, CheckCircle2, Circle, ChevronRight, Sparkles, BarChart2 } from "lucide-react";
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
}

interface HistoryItem {
  date: string;
  weight_kg: number;
  change_kg: number | null;
}

interface TrendData {
  projected_goal_date: string | null;
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

interface CoachPreview {
  summary: string;
  cached: boolean;
}

interface ProgressPreview {
  calorie_avg_7d: number;
  protein_avg_7d: number;
  weight_trend: { seven_day_avg: number | null; total_loss_kg: number | null };
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
  const [projectedDate, setProjectedDate] = useState<string | null>(null);
  const [todayWorkout, setTodayWorkout] = useState<TodayWorkout | null | "loading">("loading");
  const [nutrition, setNutrition] = useState<DailyNutrition | null>(null);
  const [missions, setMissions] = useState<DailyMissions | null>(null);
  const [weightLoggedToday, setWeightLoggedToday] = useState(false);
  const [coachPreview, setCoachPreview] = useState<CoachPreview | null>(null);
  const [progressPreview, setProgressPreview] = useState<ProgressPreview | null>(null);

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
        } else {
          setLatestWeight(null);
          setWeightLoggedToday(false);
        }
      })
      .catch(() => {});

    apiFetch<TrendData>("/weight/trend")
      .then((t) => {
        const raw = t.projected_goal_date;
        if (raw) {
          const d = new Date(raw + "T00:00:00");
          const formatted = d.toLocaleDateString("en-GB", {
            day: "numeric",
            month: "short",
            year: "2-digit",
          });
          setProjectedDate(formatted);
        } else {
          setProjectedDate(null);
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
    apiFetch<CoachPreview>("/coach/daily", { headers: { "X-Timezone": tz } })
      .then((d) => setCoachPreview({ summary: d.summary, cached: d.cached }))
      .catch(() => {});

    apiFetch<ProgressPreview>("/progress/summary", { headers: { "X-Timezone": tz } })
      .then(setProgressPreview)
      .catch(() => {});
  }, [router]);

  // Re-fetch when refreshKey increments (triggered by sub-pages or ChatDrawer after mutations)
  useEffect(() => {
    fetchAll();
  }, [fetchAll, refreshKey]);

  // Re-fetch when the tab regains visibility (user switches back from another tab)
  useEffect(() => {
    function handleVisibilityChange() {
      if (document.visibilityState === "visible") fetchAll();
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [fetchAll]);

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

  return (
    <div className="p-4 max-w-lg mx-auto flex flex-col gap-3">
      {/* Greeting */}
      <div className="pt-2 pb-1">
        <h1 className="text-xl font-extrabold text-zinc-900 tracking-tight">
          Good morning, {settings.name.split(" ")[0]}
        </h1>
        <p className="text-zinc-500 text-sm mt-0.5">Let&apos;s crush today.</p>
      </div>

      {/* ── 1. Hero — Weight progress ── */}
      <div className="bg-zinc-900 rounded-2xl p-4 shadow-md">
        <div className="flex items-start justify-between">
          <div>
            <p className="font-mono text-[10px] tracking-widest font-semibold uppercase"
              style={{ color: "rgba(255,255,255,0.55)" }}>
              Current weight
            </p>
            <div className="flex items-baseline gap-1.5 mt-1">
              <span className="font-mono text-[38px] font-bold text-white leading-none">
                {displayWeight}
              </span>
              <span className="font-mono text-[15px]" style={{ color: "rgba(255,255,255,0.6)" }}>
                kg
              </span>
            </div>
          </div>
          <div className="text-right">
            <span className="inline-flex items-center gap-1 font-mono text-[11px] font-bold text-white bg-white/10 px-2.5 py-1.5 rounded-full">
              ↓ {(settings.current_weight_kg - displayWeight).toFixed(1)} kg lost
            </span>
            <p className="font-mono text-[10.5px] mt-2" style={{ color: "rgba(255,255,255,0.55)" }}>
              {remaining.toFixed(1)} kg to goal
            </p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <div className="h-[9px] rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.16)" }}>
            <div
              className="h-full bg-white rounded-full"
              style={{
                width: `${Math.min(100, Math.max(0,
                  ((settings.current_weight_kg - displayWeight) /
                    Math.max(0.1, settings.current_weight_kg - settings.goal_weight_kg)) * 100
                ))}%`,
              }}
            />
          </div>
          <div className="flex justify-between mt-2 font-mono text-[10.5px]"
            style={{ color: "rgba(255,255,255,0.6)" }}>
            <span>{settings.current_weight_kg} kg start</span>
            <span>{settings.goal_weight_kg} kg goal</span>
          </div>
        </div>

        {/* Projection */}
        {projectedDate && (
          <div className="mt-3 pt-3 border-t flex items-center gap-2"
            style={{ borderColor: "rgba(255,255,255,0.12)" }}>
            <span style={{ color: "rgba(255,255,255,0.8)" }}>🎯</span>
            <span className="text-[12.5px]" style={{ color: "rgba(255,255,255,0.82)" }}>
              On pace for <b className="text-white">{projectedDate}</b>
            </span>
          </div>
        )}
      </div>

      {/* ── 2. Missions strip ── */}
      <MissionsStrip missions={missions} />

      {/* ── 3. Quick Actions ── */}
      <div className="grid grid-cols-2 gap-2.5">
        <Link href="/app/meals?mode=camera">
          <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-3.5 flex items-center gap-2.5 cursor-pointer hover:bg-zinc-50 transition-colors">
            <div className="w-[38px] h-[38px] rounded-xl bg-zinc-900 flex items-center justify-center shrink-0">
              <Camera size={20} color="#fff" />
            </div>
            <div>
              <p className="text-[13.5px] font-bold whitespace-nowrap">Log meal</p>
              <p className="font-mono text-[10px] text-zinc-400">Snap a photo</p>
            </div>
          </div>
        </Link>
        <Link href="/app/weight">
          <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-3.5 flex items-center gap-2.5 cursor-pointer hover:bg-zinc-50 transition-colors">
            <div className="w-[38px] h-[38px] rounded-xl bg-zinc-100 flex items-center justify-center shrink-0">
              <Scale size={20} className="text-zinc-700" />
            </div>
            <div>
              <p className="text-[13.5px] font-bold whitespace-nowrap">Weigh in</p>
              <p className="font-mono text-[10px] text-zinc-400">
                {weightLoggedToday ? "Logged ✓" : "Not logged yet"}
              </p>
            </div>
          </div>
        </Link>
      </div>

      {/* ── 4. Today · Nutrition ── */}
      <NutritionCard nutrition={nutrition} />

      {/* ── 5. Today's workout ── */}
      <TodayWorkoutCard workout={todayWorkout} />

      {/* ── 6. Coach preview ── */}
      <CoachPreviewCard preview={coachPreview} />

      {/* ── 7. This week progress ── */}
      <ProgressPreviewCard preview={progressPreview} />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Missions strip card
// ---------------------------------------------------------------------------

function MissionsStrip({ missions }: { missions: DailyMissions | null }) {
  if (!missions) return null;

  const allDone = missions.total > 0 && missions.completed === missions.total;
  const preview = missions.tasks.slice(0, 3);
  const remaining = missions.total - 3;

  const r = 52 / 2 - 6 / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(1, Math.max(0, missions.total > 0 ? missions.completed / missions.total : 0));
  const dash = pct * circ;
  const gap = circ - dash;

  return (
    <Link href="/app/missions">
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4 cursor-pointer hover:bg-zinc-50 transition-colors">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
              {allDone ? "All done 🎯" : "Today's Missions"}
            </p>
            <span className="inline-flex items-center gap-1 font-mono text-[10px] font-bold text-orange-600 bg-orange-50 px-1.5 py-0.5 rounded-full">
              <Flame size={9} />
              {missions.streak}d streak
            </span>
          </div>
          <ChevronRight size={15} className="text-zinc-300" />
        </div>

        <div className="flex items-center gap-4">
          {/* Ring */}
          <div className="relative shrink-0" style={{ width: 52, height: 52 }}>
            <svg width={52} height={52} viewBox="0 0 52 52">
              <circle cx={26} cy={26} r={r} fill="none" stroke="#e4e3df" strokeWidth={6} />
              <circle
                cx={26}
                cy={26}
                r={r}
                fill="none"
                stroke={allDone ? "#16a34a" : "#1d1c1a"}
                strokeWidth={6}
                strokeDasharray={`${dash} ${gap}`}
                strokeLinecap="round"
                transform="rotate(-90 26 26)"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-mono text-[11px] font-bold leading-none">
                {missions.completed}/{missions.total}
              </span>
            </div>
          </div>

          {/* Task list */}
          <div className="flex-1 flex flex-col gap-1.5">
            {preview.map((task) => (
              <div key={task.id} className="flex items-center gap-2">
                {task.completed ? (
                  <CheckCircle2 size={13} className="text-green-600 shrink-0" />
                ) : (
                  <Circle size={13} className="text-zinc-300 shrink-0" />
                )}
                <span
                  className={`text-[12px] flex-1 ${task.completed ? "line-through text-zinc-400" : "text-zinc-700"}`}
                >
                  {task.name}
                </span>
              </div>
            ))}
            {remaining > 0 && (
              <p className="font-mono text-[10px] text-zinc-400">+{remaining} more</p>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Nutrition card
// ---------------------------------------------------------------------------

function NutritionCard({ nutrition }: { nutrition: DailyNutrition | null }) {
  const empty = !nutrition || nutrition.meals_count === 0;

  return (
    <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
      <div className="flex items-center justify-between mb-3.5">
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
          Today · Nutrition
        </p>
        {nutrition && (
          <span className="font-mono text-[10.5px] text-zinc-400">
            {nutrition.meals_count} meal{nutrition.meals_count !== 1 ? "s" : ""} logged
          </span>
        )}
      </div>

      <div className="flex items-center gap-3">
        {/* Donut */}
        <DonutStat
          value={nutrition?.calories ?? 0}
          total={nutrition?.target_calories ?? 2000}
          label="kcal"
          size={104}
          stroke={10}
        />

        {/* Macro bars */}
        <div className="flex-1 flex flex-col gap-3">
          <MacroLine
            label="Protein"
            v={nutrition?.protein_g ?? 0}
            t={nutrition?.target_protein_g ?? 150}
          />
          <MacroLine
            label="Carbs"
            v={nutrition?.carbs_g ?? 0}
            t={nutrition?.target_carbs_g ?? 200}
          />
          <MacroLine
            label="Fat"
            v={nutrition?.fat_g ?? 0}
            t={nutrition?.target_fat_g ?? 65}
          />
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

function DonutStat({
  value,
  total,
  label,
  size,
  stroke,
}: {
  value: number;
  total: number;
  label: string;
  size: number;
  stroke: number;
}) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(1, Math.max(0, value / Math.max(1, total)));
  const dash = pct * circ;
  const gap = circ - dash;

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#e4e3df"
          strokeWidth={stroke}
        />
        {/* Progress */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#1d1c1a"
          strokeWidth={stroke}
          strokeDasharray={`${dash} ${gap}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-[14px] font-bold leading-none">
          {value.toLocaleString()}
        </span>
        <span className="font-mono text-[9px] text-zinc-400 mt-0.5">{label}</span>
      </div>
    </div>
  );
}

function MacroLine({ label, v, t }: { label: string; v: number; t: number }) {
  const pct = Math.min(100, Math.max(0, (v / Math.max(1, t)) * 100));
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[12px] font-semibold text-zinc-600">{label}</span>
        <span className="font-mono text-[11px] text-zinc-400">
          <b className="text-zinc-900">{Math.round(v)}</b> / {Math.round(t)}g
        </span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-zinc-100 overflow-hidden">
        <div
          className="h-full rounded-full bg-zinc-900 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Workout card
// ---------------------------------------------------------------------------

function TodayWorkoutCard({
  workout,
}: {
  workout: TodayWorkout | null | "loading";
}) {
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
          <div className="w-[42px] h-[42px] rounded-xl bg-zinc-50 flex items-center justify-center shrink-0">
            <Moon size={18} className="text-zinc-400" />
          </div>
          <p className="text-[15.5px] font-bold text-zinc-900">Rest Day</p>
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
        <div className="w-[42px] h-[42px] rounded-xl bg-zinc-100 flex items-center justify-center shrink-0">
          <Dumbbell size={18} className="text-zinc-700" />
        </div>
        <div>
          <p className="text-[15.5px] font-bold text-zinc-900">{workout.day_name}</p>
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
// Coach preview card (Phase 6)
// ---------------------------------------------------------------------------

function CoachPreviewCard({ preview }: { preview: CoachPreview | null }) {
  if (!preview) return null;

  const lines = preview.summary.split(". ").slice(0, 2).join(". ");
  const display = lines.endsWith(".") ? lines : lines + ".";

  return (
    <Link href="/app/coach">
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4 cursor-pointer hover:bg-zinc-50 transition-colors">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-[30px] h-[30px] rounded-lg bg-zinc-900 flex items-center justify-center shrink-0">
              <Sparkles size={14} color="#fff" />
            </div>
            <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
              AI Coach
            </p>
          </div>
          <ChevronRight size={15} className="text-zinc-300" />
        </div>
        <p className="text-[13px] text-zinc-700 leading-relaxed line-clamp-2">{display}</p>
      </div>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Progress preview card — "This week" (Phase 6)
// ---------------------------------------------------------------------------

function ProgressPreviewCard({ preview }: { preview: ProgressPreview | null }) {
  if (!preview) return null;

  const hasData =
    preview.calorie_avg_7d > 0 ||
    preview.protein_avg_7d > 0 ||
    preview.weight_trend.seven_day_avg != null;

  if (!hasData) return null;

  return (
    <Link href="/app/progress">
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4 cursor-pointer hover:bg-zinc-50 transition-colors">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-[30px] h-[30px] rounded-lg bg-zinc-100 flex items-center justify-center shrink-0">
              <BarChart2 size={14} className="text-zinc-700" />
            </div>
            <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
              This Week
            </p>
          </div>
          <ChevronRight size={15} className="text-zinc-300" />
        </div>
        <div className="grid grid-cols-3 gap-2">
          <MiniStat
            label="7d avg wt"
            value={
              preview.weight_trend.seven_day_avg != null
                ? `${preview.weight_trend.seven_day_avg.toFixed(1)} kg`
                : "—"
            }
          />
          <MiniStat
            label="Avg kcal"
            value={preview.calorie_avg_7d > 0 ? `${Math.round(preview.calorie_avg_7d)}` : "—"}
          />
          <MiniStat
            label="Avg protein"
            value={preview.protein_avg_7d > 0 ? `${Math.round(preview.protein_avg_7d)}g` : "—"}
          />
        </div>
      </div>
    </Link>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-zinc-50 rounded-xl p-2.5">
      <p className="font-mono text-[9px] text-zinc-400 uppercase tracking-wider mb-0.5">{label}</p>
      <p className="font-mono text-[14px] font-bold text-zinc-900 leading-none">{value}</p>
    </div>
  );
}
