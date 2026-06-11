"use client";

import { useEffect, useState, useCallback } from "react";
import { CheckCircle2, Circle, Flame, Bell, ChevronDown, ChevronUp, Plus, Trash2 } from "lucide-react";
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
  streak: number;
}

interface ReminderConfig {
  enabled: boolean;
  time: string; // HH:MM 24-hour
  label?: string; // only present on custom reminders
}

interface Reminders {
  weigh_in?: ReminderConfig;
  meal_log?: ReminderConfig;
  workout?: ReminderConfig;
  check_in?: ReminderConfig;
  [key: string]: ReminderConfig | undefined;
}

const BUILT_IN_KEYS = ["weigh_in", "meal_log", "workout", "check_in"] as const;
type BuiltInKey = (typeof BUILT_IN_KEYS)[number];

const REMINDER_LABELS: Record<BuiltInKey, string> = {
  weigh_in: "Morning weigh-in",
  meal_log: "Meal logging",
  workout: "Workout reminder",
  check_in: "End-of-day check-in",
};

const DEFAULT_TIMES: Record<BuiltInKey, string> = {
  weigh_in: "07:00",
  meal_log: "12:00",
  workout: "17:00",
  check_in: "20:00",
};

// ---------------------------------------------------------------------------
// Notification helpers
// ---------------------------------------------------------------------------

function getNotifPermission(): NotificationPermission | "unsupported" {
  if (typeof window === "undefined" || !("Notification" in window)) return "unsupported";
  return Notification.permission;
}

async function requestNotifPermission(): Promise<NotificationPermission | "unsupported"> {
  if (typeof window === "undefined" || !("Notification" in window)) return "unsupported";
  if (Notification.permission === "granted") return "granted";
  return await Notification.requestPermission();
}

function scheduleNotification(label: string, timeStr: string) {
  if (typeof window === "undefined" || !("Notification" in window)) return;
  if (Notification.permission !== "granted") return;

  const [h, m] = timeStr.split(":").map(Number);
  const now = new Date();
  const target = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m, 0);
  const delay = target.getTime() - now.getTime();
  if (delay <= 0) return; // Already passed today

  setTimeout(() => {
    new Notification("BodyOps", { body: `Time for: ${label}`, icon: "/icon-192.png" });
  }, delay);
}

function getReminderLabel(key: string, cfg: ReminderConfig): string {
  return REMINDER_LABELS[key as BuiltInKey] ?? cfg.label ?? key;
}

function scheduleAllReminders(reminders: Reminders) {
  for (const [key, cfg] of Object.entries(reminders)) {
    if (cfg?.enabled) {
      scheduleNotification(getReminderLabel(key, cfg), cfg.time);
    }
  }
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function MissionsPage() {
  const { triggerRefresh } = useRefresh();
  const [missions, setMissions] = useState<DailyMissions | null>(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState<string | null>(null);

  const [reminders, setReminders] = useState<Reminders>({});
  const [remindersOpen, setRemindersOpen] = useState(false);
  const [notifPermission, setNotifPermission] = useState<NotificationPermission | "unsupported">("default");
  const [savingReminders, setSavingReminders] = useState(false);
  const [addingNew, setAddingNew] = useState(false);
  const [newLabel, setNewLabel] = useState("");
  const [newTime, setNewTime] = useState("08:00");

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

  const fetchReminders = useCallback(async () => {
    try {
      const data = await apiFetch<Reminders>("/settings/reminders");
      setReminders(data ?? {});
      scheduleAllReminders(data ?? {});
    } catch {
      // silent
    }
  }, []);

  useEffect(() => {
    fetchMissions();
    fetchReminders();
    setNotifPermission(getNotifPermission());
  }, [fetchMissions, fetchReminders]);

  async function handleComplete(taskId: string, date: string) {
    if (completing) return;
    setCompleting(taskId);
    try {
      const updated = await apiFetch<DailyMissions>("/tasks/complete", {
        method: "POST",
        body: JSON.stringify({ task_id: taskId, date }),
      });
      setMissions(updated);
      triggerRefresh();
    } catch {
      // silent
    } finally {
      setCompleting(null);
    }
  }

  async function handleEnableNotifications() {
    const perm = await requestNotifPermission();
    setNotifPermission(perm);
    if (perm === "granted") scheduleAllReminders(reminders);
  }

  function toggleReminder(key: string) {
    setReminders((prev) => ({
      ...prev,
      [key]: {
        ...prev[key],
        enabled: !prev[key]?.enabled,
        time: prev[key]?.time ?? DEFAULT_TIMES[key as BuiltInKey] ?? "08:00",
      },
    }));
  }

  function setTime(key: string, time: string) {
    setReminders((prev) => ({
      ...prev,
      [key]: { ...prev[key], enabled: prev[key]?.enabled ?? false, time },
    }));
  }

  function addCustomReminder() {
    if (!newLabel.trim()) return;
    const key = `custom_${Date.now()}`;
    setReminders((prev) => ({
      ...prev,
      [key]: { enabled: true, time: newTime, label: newLabel.trim() },
    }));
    setNewLabel("");
    setNewTime("08:00");
    setAddingNew(false);
  }

  function removeReminder(key: string) {
    setReminders((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  async function saveReminders() {
    setSavingReminders(true);
    try {
      await apiFetch("/settings/reminders", {
        method: "POST",
        body: JSON.stringify(reminders),
      });
      if (notifPermission === "granted") scheduleAllReminders(reminders);
    } catch {
      // silent
    } finally {
      setSavingReminders(false);
    }
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

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
  const streak = missions?.streak ?? 0;

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
          <p className="text-[13.5px] font-bold text-zinc-900">
            {streak === 0 ? "No streak yet" : `${streak}-day streak`}
          </p>
          <p className="font-mono text-[10.5px] text-zinc-400">
            {streak === 0
              ? "Complete all missions to start your streak"
              : `${streak} consecutive day${streak === 1 ? "" : "s"} fully complete`}
          </p>
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

      {/* Reminders section */}
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm overflow-hidden">
        {/* Collapsible header */}
        <button
          onClick={() => setRemindersOpen((o) => !o)}
          className="w-full flex items-center justify-between p-4 hover:bg-zinc-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Bell size={15} className="text-zinc-500" />
            <span className="text-[13.5px] font-semibold text-zinc-900">Reminders</span>
            <span
              className={`font-mono text-[10px] px-1.5 py-0.5 rounded-full ${
                notifPermission === "granted"
                  ? "bg-green-50 text-green-600"
                  : notifPermission === "denied"
                  ? "bg-red-50 text-red-500"
                  : "bg-zinc-100 text-zinc-400"
              }`}
            >
              {notifPermission === "granted"
                ? "On"
                : notifPermission === "denied"
                ? "Blocked"
                : notifPermission === "unsupported"
                ? "Unsupported"
                : "Off"}
            </span>
          </div>
          {remindersOpen ? (
            <ChevronUp size={15} className="text-zinc-400" />
          ) : (
            <ChevronDown size={15} className="text-zinc-400" />
          )}
        </button>

        {remindersOpen && (
          <div className="border-t border-zinc-100 p-4 flex flex-col gap-4">
            {/* Permission button */}
            {notifPermission !== "granted" && notifPermission !== "unsupported" && (
              <button
                onClick={handleEnableNotifications}
                disabled={notifPermission === "denied"}
                className="flex items-center gap-2 text-sm font-semibold text-white bg-zinc-900 rounded-xl px-4 py-2.5 hover:bg-zinc-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Bell size={14} />
                {notifPermission === "denied" ? "Notifications blocked in browser" : "Enable Notifications"}
              </button>
            )}
            {notifPermission === "denied" && (
              <p className="font-mono text-[10.5px] text-red-500">
                Notifications are blocked. Enable them in your browser settings to use reminders.
              </p>
            )}

            {/* Reminder toggles */}
            <div className="flex flex-col gap-3">
              {/* Built-in reminders */}
              {BUILT_IN_KEYS.map((key) => {
                const cfg = reminders[key];
                const enabled = cfg?.enabled ?? false;
                const time = cfg?.time ?? DEFAULT_TIMES[key];
                return (
                  <div key={key} className="flex items-center gap-3">
                    <button
                      onClick={() => toggleReminder(key)}
                      className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors ${
                        enabled ? "bg-zinc-900" : "bg-zinc-200"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 mt-0.5 rounded-full bg-white shadow transition-transform ${
                          enabled ? "translate-x-4" : "translate-x-0.5"
                        }`}
                      />
                    </button>
                    <span className="flex-1 text-[13px] font-medium text-zinc-800">
                      {REMINDER_LABELS[key]}
                    </span>
                    <input
                      type="time"
                      value={time}
                      disabled={!enabled}
                      onChange={(e) => setTime(key, e.target.value)}
                      className="font-mono text-[12px] text-zinc-600 bg-zinc-50 border border-zinc-200 rounded-lg px-2 py-1 disabled:opacity-40"
                    />
                  </div>
                );
              })}

              {/* Custom reminders */}
              {Object.entries(reminders)
                .filter(([key]) => !BUILT_IN_KEYS.includes(key as BuiltInKey))
                .map(([key, cfg]) => {
                  if (!cfg) return null;
                  const enabled = cfg.enabled ?? false;
                  return (
                    <div key={key} className="flex items-center gap-3">
                      <button
                        onClick={() => toggleReminder(key)}
                        className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors ${
                          enabled ? "bg-zinc-900" : "bg-zinc-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 mt-0.5 rounded-full bg-white shadow transition-transform ${
                            enabled ? "translate-x-4" : "translate-x-0.5"
                          }`}
                        />
                      </button>
                      <span className="flex-1 text-[13px] font-medium text-zinc-800">
                        {cfg.label ?? key}
                      </span>
                      <input
                        type="time"
                        value={cfg.time}
                        disabled={!enabled}
                        onChange={(e) => setTime(key, e.target.value)}
                        className="font-mono text-[12px] text-zinc-600 bg-zinc-50 border border-zinc-200 rounded-lg px-2 py-1 disabled:opacity-40"
                      />
                      <button
                        onClick={() => removeReminder(key)}
                        className="text-zinc-400 hover:text-red-500 transition-colors shrink-0"
                        aria-label="Remove reminder"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  );
                })}
            </div>

            {/* Add new reminder */}
            {addingNew ? (
              <div className="flex flex-col gap-2 rounded-xl border border-zinc-200 bg-zinc-50 p-3">
                <input
                  type="text"
                  placeholder="Reminder name…"
                  value={newLabel}
                  onChange={(e) => setNewLabel(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") addCustomReminder(); if (e.key === "Escape") setAddingNew(false); }}
                  autoFocus
                  className="text-[13px] font-medium text-zinc-900 bg-white border border-zinc-200 rounded-lg px-3 py-1.5 outline-none focus:border-zinc-400"
                />
                <div className="flex items-center gap-2">
                  <input
                    type="time"
                    value={newTime}
                    onChange={(e) => setNewTime(e.target.value)}
                    className="font-mono text-[12px] text-zinc-600 bg-white border border-zinc-200 rounded-lg px-2 py-1"
                  />
                  <button
                    onClick={addCustomReminder}
                    disabled={!newLabel.trim()}
                    className="flex-1 text-[12px] font-semibold text-white bg-zinc-900 rounded-lg px-3 py-1.5 hover:bg-zinc-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    Add
                  </button>
                  <button
                    onClick={() => { setAddingNew(false); setNewLabel(""); setNewTime("08:00"); }}
                    className="text-[12px] font-medium text-zinc-500 hover:text-zinc-800 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setAddingNew(true)}
                className="flex items-center gap-1.5 text-[12px] font-medium text-zinc-500 hover:text-zinc-800 transition-colors self-start"
              >
                <Plus size={13} />
                Add reminder
              </button>
            )}

            <button
              onClick={saveReminders}
              disabled={savingReminders}
              className="btn-primary text-sm py-2.5 disabled:opacity-60"
            >
              {savingReminders ? "Saving…" : "Save reminders"}
            </button>
          </div>
        )}
      </div>
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
