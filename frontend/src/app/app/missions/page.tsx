"use client";

import { useEffect, useState, useCallback } from "react";
import { CheckCircle2, Circle, Flame } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useRefresh } from "@/lib/refresh";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

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
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function MissionsPage() {
  const { notifyRefresh } = useRefresh();
  const [missions, setMissions] = useState<DailyMissions | null>(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState<string | null>(null);

  const fetchMissions = useCallback(async () => {
    try {
      const data = await apiFetch<DailyMissions>("/tasks/today");
      setMissions(data);
    } catch {
      // silent — empty state renders
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMissions();
  }, [fetchMissions]);

  async function handleComplete(taskId: string, date: string) {
    if (completing) return;
    setCompleting(taskId);
    try {
      const updated = await apiFetch<DailyMissions>("/tasks/complete", {
        method: "POST",
        body: JSON.stringify({ task_id: taskId, date }),
      });
      setMissions(updated);
      notifyRefresh();
    } catch {
      // silent
    } finally {
      setCompleting(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400 text-sm">Loading…</p>
      </div>
    );
  }

  const today = new Date().toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  const allDone = missions ? missions.total > 0 && missions.completed === missions.total : false;

  return (
    <div className="p-4 max-w-lg mx-auto flex flex-col gap-4">
      {/* Header */}
      <div className="pt-2">
        <h1 className="text-xl font-extrabold text-zinc-900 tracking-tight">Today&apos;s Missions</h1>
        <p className="text-zinc-500 text-sm mt-0.5">{today}</p>
      </div>

      {/* Progress summary */}
      {missions && (
        <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[22px] font-extrabold text-zinc-900">
                {missions.completed}
                <span className="text-zinc-400 font-normal text-base">/{missions.total}</span>
              </p>
              <p className="text-zinc-500 text-sm">missions complete</p>
            </div>

            {/* Progress ring */}
            <ProgressRing pct={missions.percentage} allDone={allDone} />
          </div>

          {allDone && (
            <div className="mt-3 pt-3 border-t border-zinc-100 text-center">
              <p className="text-[14px] font-bold text-green-600">All missions complete! Great work today.</p>
            </div>
          )}
        </div>
      )}

      {/* Streak card */}
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-orange-50 flex items-center justify-center shrink-0">
          <Flame size={18} className="text-orange-500" />
        </div>
        <div>
          <p className="text-[13.5px] font-bold text-zinc-900">0-day streak</p>
          <p className="font-mono text-[10.5px] text-zinc-400">Complete all missions to build your streak</p>
        </div>
      </div>

      {/* Task list */}
      {!missions || missions.tasks.length === 0 ? (
        <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-6 text-center">
          <p className="text-zinc-400 text-sm">No missions found. Make sure your profile is set up.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {missions.tasks.map((task) => (
            <button
              key={task.id}
              disabled={task.completed || completing === task.id}
              onClick={() => handleComplete(task.id, missions.date)}
              className={`w-full text-left bg-white rounded-2xl border border-zinc-100 shadow-sm p-4 flex items-center gap-3 transition-colors ${
                task.completed
                  ? "opacity-70 cursor-default"
                  : "hover:bg-zinc-50 cursor-pointer active:scale-[0.99]"
              }`}
            >
              {task.completed ? (
                <CheckCircle2 size={22} className="text-green-600 shrink-0" />
              ) : completing === task.id ? (
                <div className="w-[22px] h-[22px] rounded-full border-2 border-zinc-300 border-t-zinc-700 animate-spin shrink-0" />
              ) : (
                <Circle size={22} className="text-zinc-300 shrink-0" />
              )}

              <div className="flex-1 min-w-0">
                <p
                  className={`text-[14px] font-semibold ${
                    task.completed ? "line-through text-zinc-400" : "text-zinc-900"
                  }`}
                >
                  {task.name}
                </p>
                <p className="font-mono text-[10.5px] text-zinc-400 mt-0.5">{task.description}</p>
              </div>

              {task.completed && task.completed_at && (
                <span className="font-mono text-[10px] text-green-600 shrink-0">
                  {new Date(task.completed_at).toLocaleTimeString("en-GB", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Progress ring
// ---------------------------------------------------------------------------

function ProgressRing({ pct, allDone }: { pct: number; allDone: boolean }) {
  const size = 64;
  const stroke = 7;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const fraction = Math.min(100, Math.max(0, pct)) / 100;
  const dash = fraction * circ;
  const gap = circ - dash;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e4e3df" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={allDone ? "#16a34a" : "#1d1c1a"}
          strokeWidth={stroke}
          strokeDasharray={`${dash} ${gap}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="font-mono text-[13px] font-bold text-zinc-900">{Math.round(pct)}%</span>
      </div>
    </div>
  );
}
