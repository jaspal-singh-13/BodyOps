/**
 * Progress page — aggregated analytics across weight, nutrition, workouts, and missions.
 *
 * Cards:
 *   1. Goal projection  — dark callout banner
 *   2. Weight trend     — Recharts LineChart (last 30 entries)
 *   3. Nutrition        — Recharts BarChart calorie + protein (last 7 days) with target reference lines
 *   4. Workouts         — 30-day dot heatmap
 *   5. Missions         — completion rate bar
 */

"use client";

import { useEffect, useState } from "react";
import { Scale, Flame, Dumbbell, CheckSquare, Trophy } from "lucide-react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, ReferenceLine, Cell,
} from "recharts";
import { apiFetch } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface WeightTrendSummary {
  total_loss_kg: number | null;
  projected_goal_date: string | null;
  seven_day_avg: number | null;
}

interface ProgressSummary {
  weight_trend: WeightTrendSummary;
  calorie_avg_7d: number;
  protein_avg_7d: number;
  workout_sessions_30d: number;
  mission_rate_30d: number;
  projected_goal_date: string | null;
}

interface MovingAvgPoint {
  date: string;
  weight_kg: number;
  ma_7: number | null;
}

interface TrendData {
  moving_avg: MovingAvgPoint[];
  total_loss_kg: number | null;
  projected_goal_date: string | null;
}

interface MealHistoryDay {
  date: string;
  display_date: string;
  total_calories: number;
  total_protein_g: number;
}

interface Settings {
  goal_weight_kg: number;
  calorie_target: number;
  protein_target_g: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatGoalDate(iso: string): string {
  try {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "2-digit" });
  } catch { return iso; }
}

function shortDate(iso: string): string {
  try { return iso.slice(5); } catch { return iso; }
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function ProgressPage() {
  const [summary, setSummary] = useState<ProgressSummary | null>(null);
  const [trend, setTrend] = useState<TrendData | null>(null);
  const [mealHistory, setMealHistory] = useState<MealHistoryDay[]>([]);
  const [workoutDates, setWorkoutDates] = useState<Set<string>>(new Set());
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    Promise.all([
      apiFetch<ProgressSummary>("/progress/summary", { headers: { "X-Timezone": tz } }),
      apiFetch<TrendData>("/weight/trend").catch(() => null),
      apiFetch<MealHistoryDay[]>("/meals/history").catch(() => []),
      apiFetch<{ sessions: { date: string }[] }>("/workouts/history").catch(() => ({ sessions: [] })),
      apiFetch<Settings>("/settings").catch(() => null),
    ])
      .then(([s, t, mh, wh, sets]) => {
        setSummary(s);
        setTrend(t ?? null);
        setMealHistory((mh ?? []).slice(0, 7).reverse());
        const dates = new Set<string>((wh?.sessions ?? []).map((sess) => sess.date));
        setWorkoutDates(dates);
        setSettings(sets ?? null);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400 text-sm">Loading progress…</p>
      </div>
    );
  }

  // Build last 30 days for heatmap
  const heatmapDays: { date: string; active: boolean }[] = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const iso = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    heatmapDays.push({ date: iso, active: workoutDates.has(iso) });
  }

  const weightChartData = (trend?.moving_avg ?? []).slice(-30);
  const calorieTarget = settings?.calorie_target ?? 2000;
  const proteinTarget = settings?.protein_target_g ?? 150;

  return (
    <div className="p-4 max-w-lg mx-auto flex flex-col gap-3 pb-10">
      {/* Header */}
      <div className="pt-2 pb-1">
        <h1 className="text-xl font-extrabold text-zinc-900 tracking-tight">Progress</h1>
        <p className="text-zinc-500 text-sm mt-0.5">Your trends over the last 7–30 days.</p>
      </div>

      {/* Goal projection callout */}
      {summary?.projected_goal_date && (
        <div className="bg-zinc-900 rounded-2xl p-4 flex items-center gap-3">
          <Trophy size={20} color="rgba(255,255,255,0.8)" />
          <div>
            <p className="font-mono text-[10px] font-semibold uppercase tracking-widest"
              style={{ color: "rgba(255,255,255,0.55)" }}>
              Goal Projection
            </p>
            <p className="text-[15px] font-bold text-white mt-0.5">
              On pace for <span className="text-white">{formatGoalDate(summary.projected_goal_date)}</span>
            </p>
          </div>
        </div>
      )}

      {/* Weight trend chart */}
      <MetricCard icon={<Scale size={16} className="text-zinc-600" />} title="Weight" subtitle="Last 30 days">
        {weightChartData.length >= 2 ? (
          <div className="mt-3">
            <div className="grid grid-cols-2 gap-2 mb-3">
              <StatBox
                label={
                  summary?.weight_trend.total_loss_kg != null
                    ? summary.weight_trend.total_loss_kg >= 0 ? "Total lost" : "Total gained"
                    : "Total change"
                }
                value={
                  summary?.weight_trend.total_loss_kg != null
                    ? `${Math.abs(summary.weight_trend.total_loss_kg).toFixed(1)} kg`
                    : "—"
                }
              />
              <StatBox
                label="7d avg"
                value={summary?.weight_trend.seven_day_avg != null ? `${summary.weight_trend.seven_day_avg.toFixed(1)} kg` : "—"}
              />
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={weightChartData} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f4f4f5" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 9, fill: "#a1a1aa" }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={shortDate}
                  interval="preserveStartEnd"
                />
                <YAxis
                  domain={["auto", "auto"]}
                  tick={{ fontSize: 9, fill: "#a1a1aa" }}
                  tickLine={false}
                  axisLine={false}
                  width={32}
                />
                <Tooltip
                  contentStyle={{ background: "#18181b", border: "none", borderRadius: 8, padding: "8px 12px" }}
                  labelStyle={{ color: "#a1a1aa", fontSize: 11 }}
                  itemStyle={{ color: "#fff", fontSize: 12 }}
                  formatter={(v: unknown) => [`${v} kg`, ""]}
                />
                {settings && (
                  <ReferenceLine
                    y={settings.goal_weight_kg}
                    stroke="#22c55e"
                    strokeDasharray="5 3"
                    strokeWidth={1.5}
                    label={{ value: "Goal", position: "insideTopRight", fill: "#22c55e", fontSize: 9 }}
                  />
                )}
                <Line type="monotone" dataKey="weight_kg" stroke="#1d1c1a" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="ma_7" stroke="#a1a1aa" dot={false} strokeDasharray="4 2" strokeWidth={1.5} connectNulls={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="mt-3 font-mono text-[11px] text-zinc-400">Log at least 2 weight entries to see the trend chart.</p>
        )}
      </MetricCard>

      {/* Calorie bar chart */}
      {mealHistory.length > 0 && (
        <MetricCard icon={<Flame size={16} className="text-zinc-600" />} title="Calories" subtitle="Last 7 days">
          <ResponsiveContainer width="100%" height={160} className="mt-3">
            <BarChart data={mealHistory} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f4f4f5" vertical={false} />
              <XAxis dataKey="display_date" tick={{ fontSize: 9, fill: "#a1a1aa" }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 9, fill: "#a1a1aa" }} tickLine={false} axisLine={false} width={36} />
              <Tooltip
                contentStyle={{ background: "#18181b", border: "none", borderRadius: 8, padding: "8px 12px" }}
                labelStyle={{ color: "#a1a1aa", fontSize: 11 }}
                itemStyle={{ color: "#fff", fontSize: 12 }}
                formatter={(v: unknown) => [`${Math.round(Number(v))} kcal`, "Calories"]}
              />
              <ReferenceLine
                y={calorieTarget}
                stroke="#22c55e"
                strokeDasharray="5 3"
                strokeWidth={1.5}
                label={{ value: "Target", position: "insideTopRight", fill: "#22c55e", fontSize: 9 }}
              />
              <Bar dataKey="total_calories" radius={[4, 4, 0, 0]} maxBarSize={28}>
                {mealHistory.map((entry) => (
                  <Cell
                    key={entry.date}
                    fill={entry.total_calories >= calorieTarget ? "#f87171" : "#1d1c1a"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </MetricCard>
      )}

      {/* Protein bar chart */}
      {mealHistory.length > 0 && (
        <MetricCard icon={<Flame size={16} className="text-zinc-600" />} title="Protein" subtitle="Last 7 days">
          <ResponsiveContainer width="100%" height={160} className="mt-3">
            <BarChart data={mealHistory} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f4f4f5" vertical={false} />
              <XAxis dataKey="display_date" tick={{ fontSize: 9, fill: "#a1a1aa" }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 9, fill: "#a1a1aa" }} tickLine={false} axisLine={false} width={36} />
              <Tooltip
                contentStyle={{ background: "#18181b", border: "none", borderRadius: 8, padding: "8px 12px" }}
                labelStyle={{ color: "#a1a1aa", fontSize: 11 }}
                itemStyle={{ color: "#fff", fontSize: 12 }}
                formatter={(v: unknown) => [`${Math.round(Number(v))}g`, "Protein"]}
              />
              <ReferenceLine
                y={proteinTarget}
                stroke="#22c55e"
                strokeDasharray="5 3"
                strokeWidth={1.5}
                label={{ value: "Target", position: "insideTopRight", fill: "#22c55e", fontSize: 9 }}
              />
              <Bar dataKey="total_protein_g" radius={[4, 4, 0, 0]} maxBarSize={28}>
                {mealHistory.map((entry) => (
                  <Cell
                    key={entry.date}
                    fill={entry.total_protein_g >= proteinTarget ? "#22c55e" : "#1d1c1a"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </MetricCard>
      )}

      {/* Workouts heatmap */}
      <MetricCard icon={<Dumbbell size={16} className="text-zinc-600" />} title="Workouts" subtitle="30-day activity">
        <div className="mt-3">
          <div className="flex items-center gap-2 mb-3">
            <span className="font-mono text-[30px] font-bold text-zinc-900 leading-none">
              {summary?.workout_sessions_30d ?? 0}
            </span>
            <div>
              <p className="text-[12px] font-medium text-zinc-600">sessions</p>
              <p className="font-mono text-[10px] text-zinc-400">last 30 days</p>
            </div>
          </div>
          {/* 5×6 dot grid (30 days) */}
          <div className="grid gap-1.5" style={{ gridTemplateColumns: "repeat(10, 1fr)" }}>
            {heatmapDays.map(({ date, active }) => (
              <div
                key={date}
                title={date}
                className={`aspect-square rounded-[3px] ${
                  active
                    ? "bg-zinc-900"
                    : "bg-zinc-100 border border-zinc-200"
                }`}
              />
            ))}
          </div>
          <p className="font-mono text-[9.5px] text-zinc-400 mt-1.5">Each dot = 1 calendar day (filled = session logged)</p>
        </div>
      </MetricCard>

      {/* Missions Card */}
      <MetricCard icon={<CheckSquare size={16} className="text-zinc-600" />} title="Missions" subtitle="Completion rate — 30 days">
        <div className="mt-3">
          <div className="flex items-center justify-between mb-2">
            <span className="font-mono text-[28px] font-bold text-zinc-900 leading-none">
              {(summary?.mission_rate_30d ?? 0).toFixed(0)}%
            </span>
            <span className="font-mono text-[10.5px] text-zinc-400">
              {summary?.mission_rate_30d != null
                ? summary.mission_rate_30d >= 80
                  ? "🔥 Great streak!"
                  : summary.mission_rate_30d >= 50
                    ? "Keep going"
                    : "Room to grow"
                : "No data"}
            </span>
          </div>
          <div className="h-3 w-full rounded-full bg-zinc-100 overflow-hidden">
            <div
              className="h-full rounded-full bg-zinc-900 transition-all"
              style={{ width: `${Math.min(100, summary?.mission_rate_30d ?? 0)}%` }}
            />
          </div>
        </div>
      </MetricCard>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function MetricCard({
  icon,
  title,
  subtitle,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
      <div className="flex items-center gap-2">
        {icon}
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
          {title}
        </p>
        <span className="ml-auto font-mono text-[10px] text-zinc-300">{subtitle}</span>
      </div>
      {children}
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-zinc-50 rounded-xl p-3">
      <p className="font-mono text-[9.5px] text-zinc-400 uppercase tracking-wider mb-1">{label}</p>
      <p className="font-mono text-[20px] font-bold text-zinc-900 leading-none">{value}</p>
    </div>
  );
}
