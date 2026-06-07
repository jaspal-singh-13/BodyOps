"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { apiFetch } from "@/lib/api";

interface HistoryItem {
  date: string;
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

function todayISO(): string {
  return new Date().toISOString().split("T")[0];
}

export default function WeightPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [trend, setTrend] = useState<TrendData | null>(null);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [date, setDate] = useState<string>(todayISO());
  const [weightInput, setWeightInput] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<HistoryItem[]>("/weight/history"),
      apiFetch<TrendData>("/weight/trend").catch(() => null),
      apiFetch<Settings>("/settings"),
    ])
      .then(([h, t, s]) => {
        setHistory(h);
        setTrend(t);
        setSettings(s);
        const todayEntry = h.find((e) => e.date === todayISO());
        if (todayEntry) setWeightInput(String(todayEntry.weight_kg));
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
        body: JSON.stringify({ date, weight_kg: parseFloat(weightInput) }),
      });
      const [h, t] = await Promise.all([
        apiFetch<HistoryItem[]>("/weight/history"),
        apiFetch<TrendData>("/weight/trend").catch(() => null),
      ]);
      setHistory(h);
      setTrend(t);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSubmitting(false);
    }
  }

  const chartData = trend?.moving_avg.slice(-30) ?? [];
  const todayEntry = history.find((e) => e.date === todayISO());
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
        <h2 className="text-sm font-semibold text-zinc-700 mb-3">
          {todayEntry ? "Update today" : "Log weight"}
        </h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div className="grid grid-cols-2 gap-3">
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
            {submitting ? "Saving…" : todayEntry ? "Update" : "Log weight"}
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

      {/* 30-day chart */}
      {chartData.length > 0 && (
        <section className="bg-white rounded-xl border border-zinc-100 p-4 mb-6">
          <h2 className="text-sm font-semibold text-zinc-700 mb-3">
            30-day trend
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                tickFormatter={(v: string) => v.slice(5)}
              />
              <YAxis domain={["auto", "auto"]} tick={{ fontSize: 10 }} width={36} />
              <Tooltip
                formatter={(value: number) => [`${value} kg`]}
                labelFormatter={(label: string) => label}
              />
              <Line
                type="monotone"
                dataKey="weight_kg"
                stroke="#18181b"
                dot={false}
                name="Weight"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="ma_7"
                stroke="#a1a1aa"
                dot={false}
                name="7-day avg"
                strokeDasharray="4 2"
                connectNulls={false}
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
                key={entry.date}
                className="flex items-center justify-between py-2 border-b border-zinc-50 last:border-0"
              >
                <span className="text-sm text-zinc-600">{entry.date}</span>
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

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl border border-zinc-100 p-4">
      <p className="text-xs text-zinc-500 mb-1">{label}</p>
      <p className="text-xl font-semibold text-zinc-900">{value}</p>
    </div>
  );
}
