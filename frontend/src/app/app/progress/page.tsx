/**
 * Progress page — aggregated analytics across weight, nutrition, workouts, and missions.
 *
 * Cards:
 *   1. Weight trend  — total loss, 7d MA, goal projection
 *   2. Nutrition     — 7d calorie + protein bar charts
 *   3. Workouts      — 30d session count + daily heatmap dots
 *   4. Missions      — 30d completion rate progress bar
 *   5. Goal          — projected goal date callout (if available)
 */

"use client";

import { useEffect, useState } from "react";
import { Scale, Flame, Dumbbell, CheckSquare, Trophy } from "lucide-react";
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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatGoalDate(iso: string): string {
  try {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "2-digit",
    });
  } catch {
    return iso;
  }
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function ProgressPage() {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const [summary, setSummary] = useState<ProgressSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<ProgressSummary>("/progress/summary", {
      headers: { "X-Timezone": tz },
    })
      .then(setSummary)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tz]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400 text-sm">Loading progress…</p>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-lg mx-auto flex flex-col gap-3">
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

      {/* Weight Trend Card */}
      <MetricCard
        icon={<Scale size={16} className="text-zinc-600" />}
        title="Weight"
        subtitle="7-day average + total loss"
      >
        <div className="grid grid-cols-2 gap-3 mt-3">
          <StatBox
            label="Total lost"
            value={
              summary?.weight_trend.total_loss_kg != null
                ? `${summary.weight_trend.total_loss_kg.toFixed(1)} kg`
                : "—"
            }
          />
          <StatBox
            label="7d avg"
            value={
              summary?.weight_trend.seven_day_avg != null
                ? `${summary.weight_trend.seven_day_avg.toFixed(1)} kg`
                : "—"
            }
          />
        </div>
      </MetricCard>

      {/* Nutrition Card */}
      <MetricCard
        icon={<Flame size={16} className="text-zinc-600" />}
        title="Nutrition"
        subtitle="7-day daily averages"
      >
        <div className="flex flex-col gap-3 mt-3">
          <NutrientBar
            label="Calories"
            value={summary?.calorie_avg_7d ?? 0}
            unit="kcal"
            max={2500}
            color="#1d1c1a"
          />
          <NutrientBar
            label="Protein"
            value={summary?.protein_avg_7d ?? 0}
            unit="g"
            max={200}
            color="#1d1c1a"
          />
        </div>
      </MetricCard>

      {/* Workouts Card */}
      <MetricCard
        icon={<Dumbbell size={16} className="text-zinc-600" />}
        title="Workouts"
        subtitle="Sessions in the last 30 days"
      >
        <div className="mt-3 flex items-center gap-3">
          <span className="font-mono text-[36px] font-bold text-zinc-900 leading-none">
            {summary?.workout_sessions_30d ?? 0}
          </span>
          <div>
            <p className="text-[12px] font-medium text-zinc-600">sessions</p>
            <p className="font-mono text-[10px] text-zinc-400">last 30 days</p>
          </div>
        </div>
        {(summary?.workout_sessions_30d ?? 0) > 0 && (
          <p className="mt-2 font-mono text-[10.5px] text-zinc-400">
            ~{((summary!.workout_sessions_30d / 30) * 7).toFixed(1)}× per week average
          </p>
        )}
      </MetricCard>

      {/* Missions Card */}
      <MetricCard
        icon={<CheckSquare size={16} className="text-zinc-600" />}
        title="Missions"
        subtitle="Completion rate — last 30 days"
      >
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
        <div>
          <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
            {title}
          </p>
        </div>
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

function NutrientBar({
  label,
  value,
  unit,
  max,
  color,
}: {
  label: string;
  value: number;
  unit: string;
  max: number;
  color: string;
}) {
  const pct = Math.min(100, Math.max(0, (value / Math.max(1, max)) * 100));
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[12px] font-semibold text-zinc-600">{label}</span>
        <span className="font-mono text-[11px] text-zinc-400">
          <b className="text-zinc-900">{Math.round(value)}</b> {unit}/day avg
        </span>
      </div>
      <div className="h-2 w-full rounded-full bg-zinc-100 overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  );
}
