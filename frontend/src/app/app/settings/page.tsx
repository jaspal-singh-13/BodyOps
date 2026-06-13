/**
 * Settings page — edit profile, goals, targets, reminders, and account.
 *
 * Pre-loads GET /settings and GET /settings/reminders on mount.
 * Each section saves independently to avoid full-form resubmits.
 *
 * Sections:
 *   Profile    — name, sex, age, height
 *   Goals      — goal weight, current weight, start date
 *   Targets    — calorie + protein + carb + fat targets (auto-recalculate button)
 *   Schedule   — wake-up time
 *   Reminders  — notification toggles + time pickers (moved from Missions)
 *   Account    — sign out
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  User, Target, Calendar, Bell, LogOut, ChevronDown, ChevronUp,
  RefreshCw, Plus, Trash2, Check,
} from "lucide-react";
import { apiFetch, clearToken } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Settings {
  name: string;
  current_weight_kg: number;
  height_cm: number;
  age: number;
  goal_weight_kg: number;
  start_date: string;
  calorie_target: number;
  protein_target_g: number;
  carb_target_g: number;
  fat_target_g: number;
  wake_up_time: string;
  unit_preference: string;
  reminders_json: string;
}

interface ReminderConfig {
  enabled: boolean;
  time: string;
  label?: string;
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
  if (delay <= 0) return;
  setTimeout(() => {
    new Notification("BodyOps", { body: `Time for: ${label}`, icon: "/icon-192.png" });
  }, delay);
}

function scheduleAllReminders(reminders: Reminders) {
  for (const [key, cfg] of Object.entries(reminders)) {
    if (cfg?.enabled) {
      const label = REMINDER_LABELS[key as BuiltInKey] ?? cfg.label ?? key;
      scheduleNotification(label, cfg.time);
    }
  }
}

// ---------------------------------------------------------------------------
// Mifflin-St Jeor auto-calc
// ---------------------------------------------------------------------------

function calcTargets(
  weightKg: number,
  heightCm: number,
  age: number,
  sex: string,
): { calories: number; protein: number; carbs: number; fat: number } {
  const offset = sex === "female" ? -161 : 5;
  const bmr = 10 * weightKg + 6.25 * heightCm - 5 * age + offset;
  const calories = Math.max(1200, Math.round(bmr * 1.55 - 500));
  const protein = Math.round(weightKg * 1.8);
  const proteinKcal = protein * 4;
  const remaining = Math.max(0, calories - proteinKcal);
  const carbs = Math.round((remaining * 0.55) / 4);
  const fat = Math.round((remaining * 0.45) / 9);
  return { calories, protein, carbs, fat };
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SectionCard({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 rounded-lg bg-zinc-100 flex items-center justify-center shrink-0">
          {icon}
        </div>
        <h2 className="text-[14px] font-bold text-zinc-900">{title}</h2>
      </div>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-zinc-500">{label}</label>
      {children}
    </div>
  );
}

function SavedBadge({ show }: { show: boolean }) {
  if (!show) return null;
  return (
    <span className="inline-flex items-center gap-1 font-mono text-[10px] font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
      <Check size={10} />
      Saved
    </span>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function SettingsPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);

  // Section-level save state
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);
  const [goalsSaving, setGoalsSaving] = useState(false);
  const [goalsSaved, setGoalsSaved] = useState(false);
  const [targetsSaving, setTargetsSaving] = useState(false);
  const [targetsSaved, setTargetsSaved] = useState(false);
  const [scheduleSaving, setScheduleSaving] = useState(false);
  const [scheduleSaved, setScheduleSaved] = useState(false);

  // Form state mirrors settings fields
  const [name, setName] = useState("");
  const [sex, setSex] = useState("male");
  const [age, setAge] = useState("");
  const [heightCm, setHeightCm] = useState("");

  const [goalWeight, setGoalWeight] = useState("");
  const [currentWeight, setCurrentWeight] = useState("");
  const [startDate, setStartDate] = useState("");

  const [calorieTarget, setCalorieTarget] = useState("");
  const [proteinTarget, setProteinTarget] = useState("");
  const [carbTarget, setCarbTarget] = useState("");
  const [fatTarget, setFatTarget] = useState("");

  const [wakeUpTime, setWakeUpTime] = useState("07:00");

  // Reminders
  const [reminders, setReminders] = useState<Reminders>({});
  const [remindersOpen, setRemindersOpen] = useState(false);
  const [notifPermission, setNotifPermission] = useState<NotificationPermission | "unsupported">("default");
  const [savingReminders, setSavingReminders] = useState(false);
  const [remindersSaved, setRemindersSaved] = useState(false);
  const [addingNew, setAddingNew] = useState(false);
  const [newLabel, setNewLabel] = useState("");
  const [newTime, setNewTime] = useState("08:00");

  const loadSettings = useCallback(async () => {
    try {
      const data = await apiFetch<Settings>("/settings");
      setSettings(data);
      setName(data.name);
      setSex("male"); // sex not stored in settings yet, default to male
      setAge(String(data.age));
      setHeightCm(String(data.height_cm));
      setGoalWeight(String(data.goal_weight_kg));
      setCurrentWeight(String(data.current_weight_kg));
      setStartDate(data.start_date);
      setCalorieTarget(String(data.calorie_target));
      setProteinTarget(String(data.protein_target_g));
      setCarbTarget(String(data.carb_target_g || ""));
      setFatTarget(String(data.fat_target_g || ""));
      setWakeUpTime(data.wake_up_time || "07:00");
    } catch {
      router.push("/onboarding");
    } finally {
      setLoading(false);
    }
  }, [router]);

  const loadReminders = useCallback(async () => {
    try {
      const data = await apiFetch<Reminders>("/settings/reminders");
      setReminders(data ?? {});
      scheduleAllReminders(data ?? {});
    } catch {
      // silent
    }
  }, []);

  useEffect(() => {
    loadSettings();
    loadReminders();
    setNotifPermission(getNotifPermission());
  }, [loadSettings, loadReminders]);

  function patchSettings(extra: Partial<Settings>) {
    if (!settings) return Promise.resolve();
    return apiFetch<Settings>("/settings", {
      method: "POST",
      body: JSON.stringify({
        name: settings.name,
        current_weight_kg: settings.current_weight_kg,
        height_cm: settings.height_cm,
        age: settings.age,
        goal_weight_kg: settings.goal_weight_kg,
        start_date: settings.start_date,
        calorie_target: settings.calorie_target,
        protein_target_g: settings.protein_target_g,
        carb_target_g: settings.carb_target_g,
        fat_target_g: settings.fat_target_g,
        wake_up_time: settings.wake_up_time,
        unit_preference: settings.unit_preference || "metric",
        ...extra,
      }),
    }).then((updated) => setSettings(updated));
  }

  async function saveProfile() {
    setProfileSaving(true);
    try {
      await patchSettings({
        name,
        height_cm: parseFloat(heightCm) || 0,
        age: parseInt(age) || 0,
      });
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 2500);
    } finally {
      setProfileSaving(false);
    }
  }

  async function saveGoals() {
    setGoalsSaving(true);
    try {
      await patchSettings({
        goal_weight_kg: parseFloat(goalWeight) || 0,
        current_weight_kg: parseFloat(currentWeight) || 0,
        start_date: startDate,
      });
      setGoalsSaved(true);
      setTimeout(() => setGoalsSaved(false), 2500);
    } finally {
      setGoalsSaving(false);
    }
  }

  async function saveTargets() {
    setTargetsSaving(true);
    try {
      await patchSettings({
        calorie_target: parseInt(calorieTarget) || 0,
        protein_target_g: parseInt(proteinTarget) || 0,
        carb_target_g: parseInt(carbTarget) || 0,
        fat_target_g: parseInt(fatTarget) || 0,
      });
      setTargetsSaved(true);
      setTimeout(() => setTargetsSaved(false), 2500);
    } finally {
      setTargetsSaving(false);
    }
  }

  async function saveSchedule() {
    setScheduleSaving(true);
    try {
      await patchSettings({ wake_up_time: wakeUpTime });
      setScheduleSaved(true);
      setTimeout(() => setScheduleSaved(false), 2500);
    } finally {
      setScheduleSaving(false);
    }
  }

  function autoRecalculate() {
    const w = parseFloat(currentWeight) || 0;
    const h = parseFloat(heightCm) || 0;
    const a = parseInt(age) || 0;
    if (!w || !h || !a) return;
    const { calories, protein, carbs, fat } = calcTargets(w, h, a, sex);
    setCalorieTarget(String(calories));
    setProteinTarget(String(protein));
    setCarbTarget(String(carbs));
    setFatTarget(String(fat));
  }

  // Reminders
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

  function setReminderTime(key: string, time: string) {
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
      setRemindersSaved(true);
      setTimeout(() => setRemindersSaved(false), 2500);
    } finally {
      setSavingReminders(false);
    }
  }

  async function handleEnableNotifications() {
    const perm = await requestNotifPermission();
    setNotifPermission(perm);
    if (perm === "granted") scheduleAllReminders(reminders);
  }

  function signOut() {
    clearToken();
    router.push("/login");
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400 text-sm">Loading…</p>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-lg mx-auto flex flex-col gap-4 pb-10">
      {/* Header */}
      <div className="pt-2 pb-1">
        <h1 className="text-xl font-extrabold text-zinc-900 tracking-tight">Settings</h1>
        <p className="text-zinc-500 text-sm mt-0.5">Manage your profile, goals and preferences.</p>
      </div>

      {/* Profile */}
      <SectionCard icon={<User size={14} className="text-zinc-600" />} title="Profile">
        <div className="flex flex-col gap-3">
          <Field label="Name">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input"
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Age">
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                className="input"
              />
            </Field>
            <Field label="Height (cm)">
              <input
                type="number"
                value={heightCm}
                onChange={(e) => setHeightCm(e.target.value)}
                className="input"
              />
            </Field>
          </div>
          <div className="flex items-center justify-between mt-1">
            <SavedBadge show={profileSaved} />
            <button
              onClick={saveProfile}
              disabled={profileSaving}
              className="btn-primary text-sm px-4 py-2 ml-auto disabled:opacity-60"
            >
              {profileSaving ? "Saving…" : "Save profile"}
            </button>
          </div>
        </div>
      </SectionCard>

      {/* Goals */}
      <SectionCard icon={<Target size={14} className="text-zinc-600" />} title="Goals">
        <div className="flex flex-col gap-3">
          <div className="grid grid-cols-2 gap-3">
            <Field label="Current weight (kg)">
              <input
                type="number"
                step="0.1"
                value={currentWeight}
                onChange={(e) => setCurrentWeight(e.target.value)}
                className="input"
              />
            </Field>
            <Field label="Goal weight (kg)">
              <input
                type="number"
                step="0.1"
                value={goalWeight}
                onChange={(e) => setGoalWeight(e.target.value)}
                className="input"
              />
            </Field>
          </div>
          <Field label="Start date">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="input"
            />
          </Field>
          <div className="flex items-center justify-between mt-1">
            <SavedBadge show={goalsSaved} />
            <button
              onClick={saveGoals}
              disabled={goalsSaving}
              className="btn-primary text-sm px-4 py-2 ml-auto disabled:opacity-60"
            >
              {goalsSaving ? "Saving…" : "Save goals"}
            </button>
          </div>
        </div>
      </SectionCard>

      {/* Targets */}
      <SectionCard icon={<RefreshCw size={14} className="text-zinc-600" />} title="Daily Targets">
        <div className="flex flex-col gap-3">
          <div className="grid grid-cols-2 gap-3">
            <Field label="Calories (kcal)">
              <input
                type="number"
                value={calorieTarget}
                onChange={(e) => setCalorieTarget(e.target.value)}
                className="input"
              />
            </Field>
            <Field label="Protein (g)">
              <input
                type="number"
                value={proteinTarget}
                onChange={(e) => setProteinTarget(e.target.value)}
                className="input"
              />
            </Field>
            <Field label="Carbs (g)">
              <input
                type="number"
                value={carbTarget}
                onChange={(e) => setCarbTarget(e.target.value)}
                className="input"
              />
            </Field>
            <Field label="Fat (g)">
              <input
                type="number"
                value={fatTarget}
                onChange={(e) => setFatTarget(e.target.value)}
                className="input"
              />
            </Field>
          </div>
          <button
            onClick={autoRecalculate}
            className="text-xs font-mono font-semibold text-zinc-500 hover:text-zinc-800 self-start flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw size={11} />
            Auto-recalculate from Mifflin-St Jeor
          </button>
          <div className="flex items-center justify-between mt-1">
            <SavedBadge show={targetsSaved} />
            <button
              onClick={saveTargets}
              disabled={targetsSaving}
              className="btn-primary text-sm px-4 py-2 ml-auto disabled:opacity-60"
            >
              {targetsSaving ? "Saving…" : "Save targets"}
            </button>
          </div>
        </div>
      </SectionCard>

      {/* Schedule */}
      <SectionCard icon={<Calendar size={14} className="text-zinc-600" />} title="Schedule">
        <div className="flex flex-col gap-3">
          <Field label="Wake-up time">
            <input
              type="time"
              value={wakeUpTime}
              onChange={(e) => setWakeUpTime(e.target.value)}
              className="input"
            />
          </Field>
          <p className="font-mono text-[10.5px] text-zinc-400">
            Used to schedule your daily missions and morning reminders.
          </p>
          <div className="flex items-center justify-between mt-1">
            <SavedBadge show={scheduleSaved} />
            <button
              onClick={saveSchedule}
              disabled={scheduleSaving}
              className="btn-primary text-sm px-4 py-2 ml-auto disabled:opacity-60"
            >
              {scheduleSaving ? "Saving…" : "Save schedule"}
            </button>
          </div>
        </div>
      </SectionCard>

      {/* Reminders */}
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm overflow-hidden">
        <button
          onClick={() => setRemindersOpen((o) => !o)}
          className="w-full flex items-center justify-between p-4 hover:bg-zinc-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-zinc-100 flex items-center justify-center shrink-0">
              <Bell size={14} className="text-zinc-600" />
            </div>
            <span className="text-[14px] font-bold text-zinc-900">Reminders</span>
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
          {remindersOpen ? <ChevronUp size={15} className="text-zinc-400" /> : <ChevronDown size={15} className="text-zinc-400" />}
        </button>

        {remindersOpen && (
          <div className="border-t border-zinc-100 p-4 flex flex-col gap-4">
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
                Notifications are blocked. Enable them in your browser settings.
              </p>
            )}

            <div className="flex flex-col gap-3">
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
                      onChange={(e) => setReminderTime(key, e.target.value)}
                      className="font-mono text-[12px] text-zinc-600 bg-zinc-50 border border-zinc-200 rounded-lg px-2 py-1 disabled:opacity-40"
                    />
                  </div>
                );
              })}

              {Object.entries(reminders)
                .filter(([key]) => !BUILT_IN_KEYS.includes(key as BuiltInKey))
                .map(([key, cfg]) => {
                  if (!cfg) return null;
                  return (
                    <div key={key} className="flex items-center gap-3">
                      <button
                        onClick={() => toggleReminder(key)}
                        className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors ${
                          cfg.enabled ? "bg-zinc-900" : "bg-zinc-200"
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 mt-0.5 rounded-full bg-white shadow transition-transform ${
                            cfg.enabled ? "translate-x-4" : "translate-x-0.5"
                          }`}
                        />
                      </button>
                      <span className="flex-1 text-[13px] font-medium text-zinc-800">
                        {cfg.label ?? key}
                      </span>
                      <input
                        type="time"
                        value={cfg.time}
                        disabled={!cfg.enabled}
                        onChange={(e) => setReminderTime(key, e.target.value)}
                        className="font-mono text-[12px] text-zinc-600 bg-zinc-50 border border-zinc-200 rounded-lg px-2 py-1 disabled:opacity-40"
                      />
                      <button
                        onClick={() => removeReminder(key)}
                        className="text-zinc-400 hover:text-red-500 transition-colors shrink-0"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  );
                })}
            </div>

            {addingNew ? (
              <div className="flex flex-col gap-2 rounded-xl border border-zinc-200 bg-zinc-50 p-3">
                <input
                  type="text"
                  placeholder="Reminder name…"
                  value={newLabel}
                  onChange={(e) => setNewLabel(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") addCustomReminder();
                    if (e.key === "Escape") setAddingNew(false);
                  }}
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

            <div className="flex items-center gap-3">
              <button
                onClick={saveReminders}
                disabled={savingReminders}
                className="btn-primary text-sm py-2.5 flex-1 disabled:opacity-60"
              >
                {savingReminders ? "Saving…" : "Save reminders"}
              </button>
              <SavedBadge show={remindersSaved} />
            </div>
          </div>
        )}
      </div>

      {/* Account */}
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-7 h-7 rounded-lg bg-zinc-100 flex items-center justify-center shrink-0">
            <LogOut size={14} className="text-zinc-600" />
          </div>
          <h2 className="text-[14px] font-bold text-zinc-900">Account</h2>
        </div>
        <button
          onClick={signOut}
          className="flex items-center gap-2 text-sm font-semibold text-red-600 hover:text-red-700 transition-colors"
        >
          <LogOut size={15} />
          Sign out
        </button>
      </div>
    </div>
  );
}
