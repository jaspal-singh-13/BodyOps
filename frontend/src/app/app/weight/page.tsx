/**
 * Weight tracking page — log daily weight and visualise the 30-day trend.
 *
 * On mount, fetches history, trend (moving average + projection), and settings
 * in parallel. If today already has an entry, the weight input is pre-filled
 * with that value so it reads as "Update today" rather than a new log.
 *
 * The chart shows two lines:
 *   - `weight_kg` — raw logged weight (solid black)
 *   - `ma_7`      — 7-day moving average (dashed grey), gaps where < 7 days exist
 *
 * Trend data is re-fetched after every successful POST so the projection and
 * chart update immediately without a page reload.
 */

"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
  Legend,
} from "recharts";
import { apiFetch } from "@/lib/api";
import { useRefresh } from "@/lib/refresh";

interface HistoryItem {
  date: string;
  time: string;
  weight_kg: number;
  change_kg: number | null;
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

interface Settings {
  goal_weight_kg: number;
}

/** Return today's date as a YYYY-MM-DD string in local time. */
function todayISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** Return the current local time as HH:MM. */
function nowHHMM(): string {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

export default function WeightPage() {
  const { triggerRefresh } = useRefresh();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [trend, setTrend] = useState<TrendData | null>(null);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [date, setDate] = useState<string>(todayISO());
  const [timeInput, setTimeInput] = useState<string>(nowHHMM());
  const [weightInput, setWeightInput] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState<7 | 30 | 90 | "all">(30);

  useEffect(() => {
    Promise.all([
      apiFetch<HistoryItem[]>("/weight/history"),
      // Trend may not exist yet (fewer than 2 entries) — treat failure as null
      apiFetch<TrendData>("/weight/trend").catch(() => null),
      apiFetch<Settings>("/settings"),
    ])
      .then(([h, t, s]) => {
        setHistory(h);
        setTrend(t);
        setSettings(s);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!weightInput) return;
    setError("");
    setSubmitting(true);
    try {
      await apiFetch("/weight", {
        method: "POST",
        body: JSON.stringify({ date, time: timeInput, weight_kg: parseFloat(weightInput) }),
      });
      // Refresh both history and trend so chart and stats reflect the new entry
      const [h, t] = await Promise.all([
        apiFetch<HistoryItem[]>("/weight/history"),
        apiFetch<TrendData>("/weight/trend").catch(() => null),
      ]);
      setHistory(h);
      setTrend(t);
      triggerRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSubmitting(false);
    }
  }

  const allChartData = trend?.moving_avg ?? [];
  const chartData =
    range === "all"
      ? allChartData
      : allChartData.slice(-range);
  const currentWeight = history.length > 0 ? history[0].weight_kg : null;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400 text-sm">Loading…</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-zinc-900 mb-6">Weight</h1>

      {history.length === 0 && (
        <p className="text-zinc-400 text-sm mb-6">
          Log your first weight to start tracking your trend.
        </p>
      )}

      {/* Log form */}
      <section className="bg-white rounded-xl border border-zinc-100 p-4 mb-6">
        <h2 className="text-sm font-semibold text-zinc-700 mb-3">Log weight</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-xs text-zinc-500 block mb-1">Date</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="text-xs text-zinc-500 block mb-1">Time</label>
              <input
                type="time"
                value={timeInput}
                onChange={(e) => setTimeInput(e.target.value)}
                className="input"
              />
            </div>
            <div>
              <label className="text-xs text-zinc-500 block mb-1">
                Weight (kg)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={weightInput}
                onChange={(e) => setWeightInput(e.target.value)}
                placeholder="85.0"
                className="input"
              />
            </div>
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button
            type="submit"
            disabled={submitting || !weightInput}
            className="btn-primary w-full"
          >
            {submitting ? "Saving…" : "Log weight"}
          </button>
        </form>
      </section>

      {/* Stats row */}
      {currentWeight !== null && settings && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
          <StatCard label="Current" value={`${currentWeight} kg`} />
          <StatCard label="Goal" value={`${settings.goal_weight_kg} kg`} />
          <StatCard
            label="Remaining"
            value={`${(currentWeight - settings.goal_weight_kg).toFixed(1)} kg`}
          />
          <StatCard
            label="Projected"
            value={trend?.projected_goal_date ?? "—"}
          />
        </div>
      )}

      {/* Trend chart */}
      {allChartData.length > 0 && (
        <section className="bg-white rounded-xl border border-zinc-100 p-4 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-zinc-700">Trend</h2>
            <div className="flex gap-1">
              {([7, 30, 90, "all"] as const).map((r) => (
                <button
                  key={r}
                  onClick={() => setRange(r)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                    range === r
                      ? "bg-zinc-900 text-white"
                      : "bg-zinc-100 text-zinc-500 hover:bg-zinc-200"
                  }`}
                >
                  {r === "all" ? "All" : `${r}d`}
                </button>
              ))}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f4f4f5" vertical={false} />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10, fill: "#a1a1aa" }}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => String(v).slice(5)}
                interval="preserveStartEnd"
              />
              <YAxis
                domain={["auto", "auto"]}
                tick={{ fontSize: 10, fill: "#a1a1aa" }}
                tickLine={false}
                axisLine={false}
                width={36}
                tickFormatter={(v) => `${v}`}
              />
              <Tooltip
                contentStyle={{
                  background: "#18181b",
                  border: "none",
                  borderRadius: 8,
                  padding: "8px 12px",
                }}
                labelStyle={{ color: "#a1a1aa", fontSize: 11, marginBottom: 4 }}
                itemStyle={{ color: "#fff", fontSize: 12 }}
                formatter={(value, name) => [
                  value != null ? `${value} kg` : "—",
                  name === "weight_kg" ? "Weight" : "7-day avg",
                ]}
                labelFormatter={(label) => label}
              />
              <Legend
                iconType="line"
                iconSize={14}
                wrapperStyle={{ fontSize: 11, paddingTop: 10 }}
                formatter={(value) => (value === "weight_kg" ? "Weight" : "7-day avg")}
              />
              {settings && (
                <ReferenceLine
                  y={settings.goal_weight_kg}
                  stroke="#22c55e"
                  strokeDasharray="5 3"
                  strokeWidth={1.5}
                  label={{
                    value: "Goal",
                    position: "insideTopRight",
                    fill: "#22c55e",
                    fontSize: 10,
                    fontWeight: 600,
                  }}
                />
              )}
              <Line
                type="monotone"
                dataKey="weight_kg"
                stroke="#18181b"
                dot={false}
                name="weight_kg"
                strokeWidth={2}
                activeDot={{ r: 4, strokeWidth: 0, fill: "#18181b" }}
                isAnimationActive={true}
                animationDuration={600}
                animationEasing="ease-out"
              />
              <Line
                type="monotone"
                dataKey="ma_7"
                stroke="#a1a1aa"
                dot={false}
                name="ma_7"
                strokeDasharray="5 3"
                strokeWidth={1.5}
                connectNulls={false}
                isAnimationActive={true}
                animationDuration={600}
                animationEasing="ease-out"
              />
            </LineChart>
          </ResponsiveContainer>
        </section>
      )}

      {/* History list */}
      {history.length > 0 && (
        <section className="bg-white rounded-xl border border-zinc-100 p-4">
          <h2 className="text-sm font-semibold text-zinc-700 mb-3">History</h2>
          <div className="flex flex-col gap-2">
            {history.map((entry) => (
              <div
                key={`${entry.date}-${entry.time}`}
                className="flex items-center justify-between py-2 border-b border-zinc-50 last:border-0"
              >
                <div className="flex flex-col">
                  <span className="text-sm text-zinc-600">{entry.date}</span>
                  {entry.time && (
                    <span className="text-xs text-zinc-400">{entry.time}</span>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-zinc-900">
                    {entry.weight_kg} kg
                  </span>
                  {entry.change_kg !== null && (
                    <span
                      className={`text-xs font-medium ${
                        entry.change_kg <= 0
                          ? "text-green-600"
                          : "text-red-500"
                      }`}
                    >
                      {entry.change_kg > 0 ? "+" : ""}
                      {entry.change_kg} kg
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

/** Key-value stat tile used in the stats row. */
function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl border border-zinc-100 p-4">
      <p className="text-xs text-zinc-500 mb-1">{label}</p>
      <p className="text-xl font-semibold text-zinc-900">{value}</p>
    </div>
  );
}
