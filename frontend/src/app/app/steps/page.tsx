"use client";

import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useRefresh } from "@/lib/refresh";

const DAILY_GOAL = 10_000;

interface StepsHistoryItem {
  date: string;
  time: string;
  steps: number;
  change_steps: number | null;
}

function todayISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function fmtDate(iso: string) {
  return new Date(iso + "T00:00:00").toLocaleDateString("en-GB", {
    weekday: "short", day: "numeric", month: "short",
  });
}

export default function StepsPage() {
  const { triggerRefresh } = useRefresh();
  const [history, setHistory] = useState<StepsHistoryItem[]>([]);
  const [date, setDate] = useState(todayISO());
  const [stepsInput, setStepsInput] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchHistory = () =>
    apiFetch<StepsHistoryItem[]>("/steps/history")
      .then(setHistory)
      .catch(() => {})
      .finally(() => setLoading(false));

  useEffect(() => { fetchHistory(); }, []);

  // Pre-fill if today already logged
  useEffect(() => {
    if (history.length > 0 && history[0].date === todayISO()) {
      setStepsInput(String(history[0].steps));
    }
  }, [history]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const steps = parseInt(stepsInput, 10);
    if (isNaN(steps) || steps < 0) { setError("Enter a valid step count"); return; }
    setSubmitting(true);
    setError("");
    try {
      await apiFetch("/steps", {
        method: "POST",
        body: JSON.stringify({ date, steps }),
      });
      await fetchHistory();
      triggerRefresh();
    } catch {
      setError("Failed to save. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(item: StepsHistoryItem) {
    try {
      await apiFetch(`/steps/${item.date}/${encodeURIComponent(item.time)}`, { method: "DELETE" });
      await fetchHistory();
      triggerRefresh();
    } catch {
      // silent — entry may already be gone
    }
  }

  const today = todayISO();
  const todayEntry = history.find((h) => h.date === today);
  const todaySteps = todayEntry?.steps ?? 0;
  const pct = Math.min(100, (todaySteps / DAILY_GOAL) * 100);

  // ring geometry
  const R = 76;
  const circ = 2 * Math.PI * R;
  const fill = (pct / 100) * circ;

  // calorie estimate: steps × 0.04 kcal (simple approximation)
  const kcal = Math.round(todaySteps * 0.04);
  const km = (todaySteps * 0.000762).toFixed(1);

  // 7-day bar chart data (newest first → reverse for chart)
  const bar7 = history.slice(0, 7).reverse();
  const maxSteps = Math.max(...bar7.map((h) => h.steps), DAILY_GOAL);

  const QUICK_PICKS = [5000, 8000, 10000, 12000];

  return (
    <div className="p-4 md:p-6 flex flex-col gap-4 min-h-full">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-zinc-900 tracking-tight">Steps</h1>
        <p className="font-mono text-[11px] text-zinc-500 uppercase tracking-widest mt-0.5">
          {new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
        </p>
      </div>

      {/* Hero ring card */}
      <div className="bg-zinc-900 rounded-2xl p-5 shadow-md">
        <p className="font-mono text-[10px] tracking-widest font-semibold uppercase text-white/50 mb-4">
          Today · Steps
        </p>
        <div className="flex flex-col items-center">
          <div className="relative" style={{ width: 180, height: 180 }}>
            <svg width={180} height={180} viewBox="0 0 180 180" style={{ transform: "rotate(-90deg)" }}>
              <circle cx={90} cy={90} r={R} fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth={14} />
              <circle
                cx={90} cy={90} r={R} fill="none" stroke="#fff" strokeWidth={14}
                strokeDasharray={`${fill} ${circ - fill}`} strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-mono text-[38px] font-bold text-white leading-none">
                {todaySteps.toLocaleString()}
              </span>
              <span className="font-mono text-[11px] text-white/45 uppercase tracking-wider mt-1">steps</span>
            </div>
          </div>

          {/* meta row */}
          <div className="flex gap-8 mt-4">
            {[
              { value: km, label: "km" },
              { value: kcal.toLocaleString(), label: "kcal" },
              { value: `${Math.round(pct)}%`, label: "of goal" },
            ].map(({ value, label }) => (
              <div key={label} className="text-center">
                <div className="font-mono text-[18px] font-bold text-white leading-none">{value}</div>
                <div className="font-mono text-[9px] uppercase tracking-wider text-white/45 mt-1">{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* progress bar */}
        <div className="mt-5 pt-4 border-t border-white/10">
          <div className="h-1.5 rounded-full overflow-hidden bg-white/15">
            <div className="h-full bg-white rounded-full transition-all" style={{ width: `${pct}%` }} />
          </div>
          <div className="flex justify-between mt-1.5 font-mono text-[10px] text-white/40">
            <span>0</span>
            <span>{todaySteps.toLocaleString()} / {DAILY_GOAL.toLocaleString()} goal</span>
          </div>
        </div>
      </div>

      {/* Log form */}
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase mb-3">
          Log steps
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <div className="flex gap-3">
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="h-10 px-3 rounded-xl border border-zinc-200 text-sm font-mono text-zinc-700 bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-zinc-300"
            />
            <input
              type="number"
              min={0}
              step={100}
              placeholder="Steps"
              value={stepsInput}
              onChange={(e) => setStepsInput(e.target.value)}
              className="flex-1 h-10 px-3 rounded-xl border border-zinc-200 text-sm font-mono text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-300"
            />
          </div>

          {/* Quick picks */}
          <div className="flex gap-2">
            {QUICK_PICKS.map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => setStepsInput(String(n))}
                className="flex-1 h-9 rounded-xl bg-zinc-100 text-[12.5px] font-semibold text-zinc-700 hover:bg-zinc-200 transition-colors"
              >
                {(n / 1000).toFixed(0)}k
              </button>
            ))}
          </div>

          {error && <p className="text-[12px] text-red-500">{error}</p>}

          <button
            type="submit"
            disabled={submitting || stepsInput === ""}
            className="h-10 rounded-xl bg-zinc-900 text-[13px] font-semibold text-white hover:bg-zinc-800 transition-colors disabled:opacity-40"
          >
            {submitting ? "Saving…" : todayEntry ? "Update today" : "Save steps"}
          </button>
        </form>
      </div>

      {/* 7-day bar chart */}
      {bar7.length > 0 && (
        <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
          <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase mb-4">
            Last 7 days
          </p>
          <div className="flex items-end gap-2 h-20">
            {bar7.map((item) => {
              const h = Math.round((item.steps / maxSteps) * 72);
              const isToday = item.date === today;
              const hitGoal = item.steps >= DAILY_GOAL;
              return (
                <div key={item.date} className="flex-1 flex flex-col items-center gap-1.5 justify-end h-full">
                  <div
                    className={`w-full rounded-t-md transition-all ${
                      isToday ? "bg-zinc-900" : hitGoal ? "bg-green-500" : "bg-zinc-200"
                    }`}
                    style={{ height: h }}
                  />
                  <span className={`font-mono text-[9px] ${isToday ? "font-bold text-zinc-900" : "text-zinc-400"}`}>
                    {isToday ? "Today" : fmtDate(item.date).slice(0, 3)}
                  </span>
                </div>
              );
            })}
          </div>
          {/* weekly stats */}
          {bar7.length >= 2 && (
            <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-zinc-100">
              <div className="bg-zinc-50 rounded-xl p-2.5">
                <p className="font-mono text-[9px] text-zinc-400 uppercase tracking-wider mb-0.5">7-day avg</p>
                <p className="font-mono text-[15px] font-bold text-zinc-900">
                  {Math.round(bar7.reduce((s, h) => s + h.steps, 0) / bar7.length).toLocaleString()}
                </p>
              </div>
              <div className={`rounded-xl p-2.5 ${
                bar7.filter((h) => h.steps >= DAILY_GOAL).length >= 4 ? "bg-green-50" : "bg-zinc-50"
              }`}>
                <p className="font-mono text-[9px] text-zinc-400 uppercase tracking-wider mb-0.5">Goal hit</p>
                <p className={`font-mono text-[15px] font-bold ${
                  bar7.filter((h) => h.steps >= DAILY_GOAL).length >= 4 ? "text-green-700" : "text-zinc-900"
                }`}>
                  {bar7.filter((h) => h.steps >= DAILY_GOAL).length}/{bar7.length} days
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* History list */}
      {!loading && history.length > 0 && (
        <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
          <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase mb-3">
            History
          </p>
          <div className="flex flex-col divide-y divide-zinc-100">
            {history.map((item) => (
              <div key={`${item.date}-${item.time}`} className="flex items-center py-2.5 gap-3">
                <div className="flex-1">
                  <p className="text-[13px] font-semibold text-zinc-900">
                    {fmtDate(item.date)}
                    {item.date === today && (
                      <span className="ml-1.5 font-mono text-[10px] text-zinc-400">today</span>
                    )}
                  </p>
                  <p className="font-mono text-[11px] text-zinc-400 mt-0.5">{item.time}</p>
                </div>
                <div className="text-right">
                  <p className="font-mono text-[15px] font-bold text-zinc-900">
                    {item.steps.toLocaleString()}
                  </p>
                  {item.change_steps != null && (
                    <p className={`font-mono text-[10px] ${
                      item.change_steps >= 0 ? "text-green-600" : "text-zinc-400"
                    }`}>
                      {item.change_steps >= 0 ? "+" : ""}{item.change_steps.toLocaleString()}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(item)}
                  className="ml-1 p-1.5 rounded-lg text-zinc-300 hover:text-red-400 hover:bg-red-50 transition-colors"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && history.length === 0 && (
        <p className="font-mono text-[11px] text-zinc-400 text-center py-8">
          No steps logged yet. Enter your count above.
        </p>
      )}
    </div>
  );
}
