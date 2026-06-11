"use client";

import { useEffect, useState } from "react";
import { ChevronDown, ChevronUp, Check, Dumbbell, Moon, Pencil, Plus, Trash2, X } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useRefresh } from "@/lib/refresh";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ProgressionSuggestion {
  weight_kg: number | null;
  reps: number | null;
  note: string;
}

interface TodayExercise {
  exercise_name: string;
  sets: number;
  rep_min: number;
  rep_max: number;
  order: number;
  last_weight_kg: number | null;
  last_reps: number | null;
  suggestion: ProgressionSuggestion;
  sets_logged_today: number;
}

interface TodayWorkout {
  date: string;
  day_name: string;
  is_rest_day: boolean;
  exercises: TodayExercise[];
  estimated_duration_min: number;
  session_id: string | null;
  is_completed: boolean;
  plan_name: string | null;
}

interface ScheduleExercise {
  exercise_name: string;
  sets: number;
  rep_min: number;
  rep_max: number;
  order: number;
}

interface ScheduleDay {
  weekday: number;
  weekday_name: string;
  day_name: string;
  is_rest: boolean;
  exercises: ScheduleExercise[];
}

interface WorkoutSchedule {
  program_name: string | null;
  days: ScheduleDay[];
}

interface WorkoutPlanSummary {
  plan_id: string;
  plan_name: string;
  is_active: boolean;
  day_count: number;
  exercise_count: number;
  created_at: string;
}

interface WorkoutDaySummary {
  day_name: string;
  exercises: { exercise_name: string; sets: number; rep_min: number; rep_max: number }[];
}

interface ImportResult {
  program_name: string;
  program_days: number;
  rest_days: number;
  total_exercises: number;
  days: WorkoutDaySummary[];
}

interface SetRow {
  weight: string;
  reps: string;
  submitted: boolean;
}

type SessionLog = Record<string, SetRow[]>;

interface SessionHistoryItem {
  session_id: string;
  date: string;
  day_name: string;
  started_at: string;
  completed_at: string;
}

type ActiveTab = "import" | "today" | "log" | "schedule" | "history";

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function WorkoutsPage() {
  const { triggerRefresh } = useRefresh();
  const [activeTab, setActiveTab] = useState<ActiveTab>("today");
  const [loading, setLoading] = useState(true);

  // Import tab state
  const [planText, setPlanText] = useState("");
  const [programName, setProgramName] = useState("");
  const [importLoading, setImportLoading] = useState(false);
  const [importError, setImportError] = useState("");
  const [importResult, setImportResult] = useState<ImportResult | null>(null);

  // Today + Log tab state
  const [todayWorkout, setTodayWorkout] = useState<TodayWorkout | null>(null);
  const [sessionLog, setSessionLog] = useState<SessionLog>({});
  const [completingSession, setCompletingSession] = useState(false);
  const [sessionCompleted, setSessionCompleted] = useState(false);

  // History tab state
  const [history, setHistory] = useState<SessionHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [expandedSession, setExpandedSession] = useState<string | null>(null);

  // Schedule tab state
  const [schedule, setSchedule] = useState<WorkoutSchedule | null>(null);

  // Plans library state
  const [plans, setPlans] = useState<WorkoutPlanSummary[]>([]);
  const [plansLoading, setPlansLoading] = useState(false);
  const [planActionLoading, setPlanActionLoading] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<TodayWorkout>("/workouts/today").catch(() => null),
      apiFetch<{ sessions: SessionHistoryItem[] }>("/workouts/history").catch(() => ({ sessions: [] })),
      apiFetch<WorkoutSchedule>("/workouts/schedule").catch(() => null),
      apiFetch<{ plans: WorkoutPlanSummary[] }>("/workouts/plans").catch(() => ({ plans: [] })),
    ])
      .then(([tw, hist, sched, planData]) => {
        setTodayWorkout(tw);
        setHistory(hist?.sessions ?? []);
        setSchedule(sched);
        setPlans(planData?.plans ?? []);
      })
      .catch(() => {})
      .finally(() => {
        setLoading(false);
        setHistoryLoading(false);
      });
  }, []);

  async function refreshToday() {
    const tw = await apiFetch<TodayWorkout>("/workouts/today").catch(() => null);
    setTodayWorkout(tw);
  }

  async function refreshHistory() {
    const hist = await apiFetch<{ sessions: SessionHistoryItem[] }>("/workouts/history").catch(() => ({ sessions: [] }));
    setHistory(hist?.sessions ?? []);
  }

  async function refreshSchedule() {
    const sched = await apiFetch<WorkoutSchedule>("/workouts/schedule").catch(() => null);
    setSchedule(sched);
  }

  async function refreshPlans() {
    setPlansLoading(true);
    try {
      const data = await apiFetch<{ plans: WorkoutPlanSummary[] }>("/workouts/plans").catch(() => ({ plans: [] }));
      setPlans(data?.plans ?? []);
    } finally {
      setPlansLoading(false);
    }
  }

  async function handleActivatePlan(planId: string) {
    setPlanActionLoading(planId);
    try {
      await apiFetch(`/workouts/plans/${planId}/activate`, { method: "POST" });
      await Promise.all([refreshPlans(), refreshSchedule(), refreshToday()]);
      triggerRefresh();
    } finally {
      setPlanActionLoading(null);
    }
  }

  async function handleDeletePlan(planId: string) {
    setConfirmDeleteId(null);
    setPlanActionLoading(planId);
    try {
      await apiFetch(`/workouts/plans/${planId}`, { method: "DELETE" });
      await Promise.all([refreshPlans(), refreshSchedule(), refreshToday()]);
      triggerRefresh();
    } finally {
      setPlanActionLoading(null);
    }
  }

  async function handleRenamePlan(planId: string, newName: string) {
    await apiFetch(`/workouts/plans/${planId}`, {
      method: "PATCH",
      body: JSON.stringify({ plan_name: newName }),
    });
    await refreshPlans();
  }

  async function handleUpdateDay(planId: string, dayName: string, exercises: ScheduleExercise[]) {
    await apiFetch(`/workouts/plans/${planId}/days/${encodeURIComponent(dayName)}`, {
      method: "PUT",
      body: JSON.stringify({ exercises }),
    });
    await Promise.all([refreshSchedule(), refreshToday()]);
    triggerRefresh();
  }

  async function handleUpdateScheduleWeekday(planId: string, weekday: number, dayName: string) {
    await apiFetch(`/workouts/plans/${planId}/schedule/${weekday}`, {
      method: "PATCH",
      body: JSON.stringify({ day_name: dayName }),
    });
    await Promise.all([refreshSchedule(), refreshToday()]);
    triggerRefresh();
  }

  // ---------------------------------------------------------------------------
  // Import tab handlers
  // ---------------------------------------------------------------------------

  async function handleImport(e: React.FormEvent) {
    e.preventDefault();
    if (!planText.trim() || !programName.trim()) return;
    setImportError("");
    setImportLoading(true);
    try {
      const result = await apiFetch<ImportResult>("/workouts/ai-import", {
        method: "POST",
        body: JSON.stringify({
          raw_text: planText,
          program_name: programName,
        }),
      });
      setImportResult(result);
      await Promise.all([refreshToday(), refreshSchedule(), refreshPlans()]);
      triggerRefresh();
    } catch (err) {
      setImportError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setImportLoading(false);
    }
  }

  // ---------------------------------------------------------------------------
  // Log tab handlers
  // ---------------------------------------------------------------------------

  function initSessionLog() {
    if (!todayWorkout) return;
    const log: SessionLog = {};
    for (const ex of todayWorkout.exercises) {
      log[ex.exercise_name] = [{ weight: "", reps: "", submitted: false }];
    }
    setSessionLog(log);
  }

  function handleStartLogging() {
    initSessionLog();
    setActiveTab("log");
  }

  function addSetRow(exerciseName: string) {
    setSessionLog((prev) => ({
      ...prev,
      [exerciseName]: [...(prev[exerciseName] ?? []), { weight: "", reps: "", submitted: false }],
    }));
  }

  function updateSetRow(exerciseName: string, index: number, field: "weight" | "reps", value: string) {
    setSessionLog((prev) => {
      const rows = [...(prev[exerciseName] ?? [])];
      rows[index] = { ...rows[index], [field]: value };
      return { ...prev, [exerciseName]: rows };
    });
  }

  async function handleLogSet(exerciseName: string, index: number) {
    const row = sessionLog[exerciseName]?.[index];
    if (!row || !row.weight || !row.reps || !todayWorkout) return;

    try {
      await apiFetch("/workouts/log", {
        method: "POST",
        body: JSON.stringify({
          date: todayWorkout.date,
          exercise_name: exerciseName,
          weight_kg: parseFloat(row.weight),
          reps: parseInt(row.reps),
          day_name: todayWorkout.day_name,
        }),
      });
      setSessionLog((prev) => {
        const rows = [...(prev[exerciseName] ?? [])];
        rows[index] = { ...rows[index], submitted: true };
        return { ...prev, [exerciseName]: rows };
      });
      await refreshToday();
      triggerRefresh();
    } catch {
      // Keep row editable on failure
    }
  }

  async function handleCompleteSession() {
    if (!todayWorkout) return;
    setCompletingSession(true);
    try {
      await apiFetch("/workouts/complete", {
        method: "POST",
        body: JSON.stringify({ date: todayWorkout.date }),
      });
      setSessionCompleted(true);
      await refreshHistory();
      triggerRefresh();
    } catch {
      // no-op
    } finally {
      setCompletingSession(false);
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

  const tabs: { id: ActiveTab; label: string }[] = [
    { id: "today", label: "Today" },
    { id: "log", label: "Log" },
    { id: "schedule", label: "Schedule" },
    { id: "history", label: "History" },
    { id: "import", label: "Import" },
  ];

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-zinc-900 mb-4">Workouts</h1>

      {/* Tab bar */}
      <div className="flex gap-1 border-b border-zinc-100 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "text-zinc-900 border-b-2 border-zinc-900 -mb-px"
                : "text-zinc-400 hover:text-zinc-600"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "import" && (
        <ImportTab
          planText={planText}
          programName={programName}
          onPlanTextChange={setPlanText}
          onProgramNameChange={setProgramName}
          onSubmit={handleImport}
          loading={importLoading}
          error={importError}
          result={importResult}
        />
      )}

      {activeTab === "today" && (
        <TodayTab
          workout={todayWorkout}
          onStartLogging={handleStartLogging}
          onGoToImport={() => setActiveTab("import")}
          onGoToSchedule={() => setActiveTab("schedule")}
        />
      )}

      {activeTab === "log" && (
        <LogTab
          workout={todayWorkout}
          sessionLog={sessionLog}
          onAddSet={addSetRow}
          onUpdateSet={updateSetRow}
          onLogSet={handleLogSet}
          onComplete={handleCompleteSession}
          completing={completingSession}
          completed={sessionCompleted}
        />
      )}

      {activeTab === "schedule" && (
        <ScheduleTab
          schedule={schedule}
          plans={plans}
          plansLoading={plansLoading}
          planActionLoading={planActionLoading}
          confirmDeleteId={confirmDeleteId}
          onConfirmDelete={setConfirmDeleteId}
          onActivatePlan={handleActivatePlan}
          onDeletePlan={handleDeletePlan}
          onRenamePlan={handleRenamePlan}
          onUpdateDay={handleUpdateDay}
          onUpdateScheduleWeekday={handleUpdateScheduleWeekday}
          onGoToImport={() => setActiveTab("import")}
        />
      )}

      {activeTab === "history" && (
        <HistoryTab
          sessions={history}
          loading={historyLoading}
          expandedSession={expandedSession}
          onToggleSession={(id) => setExpandedSession((prev) => (prev === id ? null : id))}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Import tab
// ---------------------------------------------------------------------------

function ImportTab({
  planText, programName,
  onPlanTextChange, onProgramNameChange,
  onSubmit, loading, error, result,
}: {
  planText: string; programName: string;
  onPlanTextChange: (v: string) => void;
  onProgramNameChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean; error: string;
  result: ImportResult | null;
}) {
  return (
    <div className="flex flex-col gap-6">
      <section className="bg-white rounded-xl border border-zinc-100 p-4">
        <h2 className="text-sm font-semibold text-zinc-700 mb-1">Import workout plan</h2>
        <p className="text-xs text-zinc-400 mb-4">
          Paste your workout in any format — the AI will convert it automatically. It will be saved as a new plan in your library and made active. Your current plan is kept.
        </p>
        <form onSubmit={onSubmit} className="flex flex-col gap-3">
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Program name</label>
            <input
              type="text"
              value={programName}
              onChange={(e) => onProgramNameChange(e.target.value)}
              placeholder="PPL v1"
              className="input"
            />
          </div>
          <div>
            <label className="text-xs text-zinc-500 block mb-1">Workout plan — any format</label>
            <textarea
              value={planText}
              onChange={(e) => onPlanTextChange(e.target.value)}
              rows={12}
              placeholder={"Monday: Chest day\nBench Press — 4 sets of 8-10 reps\nIncline Dumbbell 3 sets 12 reps\n\nWednesday: Rest\n\nFriday: Leg day\nSquat 4x5, Romanian Deadlift 3x10-12"}
              className="input font-mono text-xs resize-y w-full"
            />
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button
            type="submit"
            disabled={loading || !planText.trim() || !programName.trim()}
            className="btn-primary w-full"
          >
            {loading ? "Importing…" : "Save plan"}
          </button>
        </form>
      </section>

      {result && (
        <section className="bg-white rounded-xl border border-zinc-100 p-4">
          <h2 className="text-sm font-semibold text-zinc-700 mb-3">
            Imported: {result.program_name}
          </h2>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center">
              <p className="text-xl font-bold text-zinc-900">{result.program_days}</p>
              <p className="text-xs text-zinc-500">workout days</p>
            </div>
            <div className="text-center">
              <p className="text-xl font-bold text-zinc-900">{result.rest_days}</p>
              <p className="text-xs text-zinc-500">rest days</p>
            </div>
            <div className="text-center">
              <p className="text-xl font-bold text-zinc-900">{result.total_exercises}</p>
              <p className="text-xs text-zinc-500">exercises</p>
            </div>
          </div>
          <div className="flex flex-col gap-1">
            {result.days
              .filter((d) => d.day_name !== "Rest")
              .map((day) => (
                <div key={day.day_name} className="flex items-center justify-between py-1.5 border-b border-zinc-50 last:border-0">
                  <span className="text-sm font-medium text-zinc-900">{day.day_name}</span>
                  <span className="text-xs text-zinc-500">{day.exercises.length} exercises</span>
                </div>
              ))}
          </div>
        </section>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Today tab
// ---------------------------------------------------------------------------

function TodayTab({
  workout,
  onStartLogging,
  onGoToImport,
  onGoToSchedule,
}: {
  workout: TodayWorkout | null;
  onStartLogging: () => void;
  onGoToImport: () => void;
  onGoToSchedule: () => void;
}) {
  if (!workout || (!workout.is_rest_day && workout.exercises.length === 0)) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
        <Dumbbell className="text-zinc-300" size={40} />
        <p className="text-zinc-500 text-sm">Paste your workout plan to get started</p>
        <button onClick={onGoToImport} className="btn-primary">
          Import plan
        </button>
      </div>
    );
  }

  if (workout.is_rest_day) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
        <Moon className="text-zinc-300" size={40} />
        <p className="text-lg font-semibold text-zinc-900">Rest Day</p>
        <p className="text-sm text-zinc-500">Recovery is part of the program</p>
        {workout.plan_name && (
          <p className="text-xs text-zinc-400">{workout.plan_name}</p>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-zinc-500 uppercase tracking-wide">
            Today{workout.plan_name ? ` · ${workout.plan_name}` : ""}
          </p>
          <p className="text-xl font-bold text-zinc-900">{workout.day_name} Day</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-zinc-400 font-mono">
            {workout.exercises.length} exercises · ~{workout.estimated_duration_min} min
          </p>
          {workout.plan_name && (
            <button
              onClick={onGoToSchedule}
              className="text-xs text-zinc-400 hover:text-zinc-600 underline underline-offset-2 mt-0.5"
            >
              View all plans
            </button>
          )}
        </div>
      </div>

      {workout.exercises.map((ex) => (
        <div key={ex.exercise_name} className="bg-white rounded-xl border border-zinc-100 p-4">
          <div className="flex items-start justify-between mb-2">
            <p className="text-sm font-semibold text-zinc-900">{ex.exercise_name}</p>
            <p className="text-xs text-zinc-500 font-mono">
              {ex.sets} × {ex.rep_min}–{ex.rep_max}
            </p>
          </div>
          <div className="flex items-center gap-4 mt-1">
            <div>
              <p className="text-xs text-zinc-400">Last session</p>
              <p className="text-xs text-zinc-600">
                {ex.last_weight_kg !== null
                  ? `${ex.last_weight_kg} kg × ${ex.last_reps}`
                  : "First session"}
              </p>
            </div>
            {ex.suggestion.note !== "first session" && (
              <div>
                <p className="text-xs text-zinc-400">Suggested</p>
                <p className="text-xs font-medium text-zinc-900">
                  {ex.suggestion.weight_kg} kg × {ex.suggestion.reps}
                </p>
              </div>
            )}
          </div>
        </div>
      ))}

      <button onClick={onStartLogging} className="btn-primary w-full mt-2">
        Start logging
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Log tab
// ---------------------------------------------------------------------------

function LogTab({
  workout, sessionLog,
  onAddSet, onUpdateSet, onLogSet,
  onComplete, completing, completed,
}: {
  workout: TodayWorkout | null;
  sessionLog: SessionLog;
  onAddSet: (name: string) => void;
  onUpdateSet: (name: string, index: number, field: "weight" | "reps", value: string) => void;
  onLogSet: (name: string, index: number) => void;
  onComplete: () => void;
  completing: boolean;
  completed: boolean;
}) {
  if (!workout || workout.is_rest_day || workout.exercises.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
        <p className="text-zinc-500 text-sm">
          Go to the Today tab and tap "Start logging" to begin a session.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-5">
      <div>
        <p className="text-xs text-zinc-500 uppercase tracking-wide">Logging</p>
        <p className="text-xl font-bold text-zinc-900">{workout.day_name} Day</p>
      </div>

      {workout.exercises.map((ex) => {
        const rows = sessionLog[ex.exercise_name] ?? [];
        const repTarget = ex.suggestion.note !== "first session" && ex.suggestion.reps
          ? ex.suggestion.reps
          : Math.round((ex.rep_min + ex.rep_max) / 2);
        const weightSuggestion = ex.suggestion.weight_kg;

        return (
          <section key={ex.exercise_name} className="bg-white rounded-xl border border-zinc-100 p-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-semibold text-zinc-900">{ex.exercise_name}</p>
              <p className="text-xs text-zinc-500 font-mono">
                {ex.sets} sets · {ex.rep_min}–{ex.rep_max} reps
              </p>
            </div>

            {weightSuggestion !== null && (
              <p className="text-xs text-zinc-500 mb-3">
                Suggested:{" "}
                <span className="font-medium text-zinc-700">
                  {weightSuggestion} kg × {repTarget}
                </span>
              </p>
            )}

            <div className="flex flex-col gap-2">
              {rows.map((row, idx) => (
                <div key={idx} className={`flex items-center gap-2 ${row.submitted ? "opacity-50" : ""}`}>
                  <span className="text-xs text-zinc-400 w-5 shrink-0">#{idx + 1}</span>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={row.weight}
                    onChange={(e) => onUpdateSet(ex.exercise_name, idx, "weight", e.target.value)}
                    placeholder={weightSuggestion ? String(weightSuggestion) : "kg"}
                    disabled={row.submitted}
                    className="input w-20 text-sm"
                  />
                  <span className="text-xs text-zinc-400">×</span>
                  <input
                    type="number"
                    min="1"
                    value={row.reps}
                    onChange={(e) => onUpdateSet(ex.exercise_name, idx, "reps", e.target.value)}
                    placeholder={String(repTarget)}
                    disabled={row.submitted}
                    className="input w-16 text-sm"
                  />
                  {row.submitted ? (
                    <Check size={16} className="text-green-600 ml-1" />
                  ) : (
                    <button
                      onClick={() => onLogSet(ex.exercise_name, idx)}
                      disabled={!row.weight || !row.reps}
                      className="btn-outline text-xs px-3 py-1"
                    >
                      Log
                    </button>
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={() => onAddSet(ex.exercise_name)}
              className="mt-3 flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-700"
            >
              <Plus size={12} />
              Add set
            </button>
          </section>
        );
      })}

      {completed ? (
        <p className="text-center text-sm text-green-600 font-medium py-4">
          Session completed!
        </p>
      ) : (
        <button
          onClick={onComplete}
          disabled={completing}
          className="btn-primary w-full mt-2"
        >
          {completing ? "Saving…" : "Complete workout"}
        </button>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Schedule tab
// ---------------------------------------------------------------------------

function ScheduleTab({
  schedule,
  plans,
  plansLoading,
  planActionLoading,
  confirmDeleteId,
  onConfirmDelete,
  onActivatePlan,
  onDeletePlan,
  onRenamePlan,
  onUpdateDay,
  onUpdateScheduleWeekday,
  onGoToImport,
}: {
  schedule: WorkoutSchedule | null;
  plans: WorkoutPlanSummary[];
  plansLoading: boolean;
  planActionLoading: string | null;
  confirmDeleteId: string | null;
  onConfirmDelete: (id: string | null) => void;
  onActivatePlan: (planId: string) => Promise<void>;
  onDeletePlan: (planId: string) => Promise<void>;
  onRenamePlan: (planId: string, newName: string) => Promise<void>;
  onUpdateDay: (planId: string, dayName: string, exercises: ScheduleExercise[]) => Promise<void>;
  onUpdateScheduleWeekday: (planId: string, weekday: number, dayName: string) => Promise<void>;
  onGoToImport: () => void;
}) {
  const todayWeekday = new Date().getDay();
  const todayIndex = todayWeekday === 0 ? 6 : todayWeekday - 1;

  // Inline rename state (local — no API call needed for open/close)
  const [renamingPlanId, setRenamingPlanId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [renameLoading, setRenameLoading] = useState(false);

  // Day edit modal state
  const [editDay, setEditDay] = useState<ScheduleDay | null>(null);

  // Weekday remap loading
  const [remappingWeekday, setRemappingWeekday] = useState<number | null>(null);

  const activePlanId = plans.find((p) => p.is_active)?.plan_id ?? null;
  const availableDayNames = schedule
    ? [...new Set(schedule.days.map((d) => d.day_name))]
    : [];

  const hasSchedule = schedule && schedule.days.length > 0;

  async function saveRename(planId: string) {
    if (!renameValue.trim()) return;
    setRenameLoading(true);
    try {
      await onRenamePlan(planId, renameValue.trim());
      setRenamingPlanId(null);
    } finally {
      setRenameLoading(false);
    }
  }

  async function handleWeekdayRemap(weekday: number, newDayName: string) {
    if (!activePlanId) return;
    setRemappingWeekday(weekday);
    try {
      await onUpdateScheduleWeekday(activePlanId, weekday, newDayName);
    } finally {
      setRemappingWeekday(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Plans library */}
      <section className="bg-white rounded-xl border border-zinc-100 p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-zinc-700">My Plans</h2>
          <button
            onClick={onGoToImport}
            className="text-xs text-zinc-500 hover:text-zinc-700 underline underline-offset-2"
          >
            + Import new
          </button>
        </div>

        {plansLoading && <p className="text-xs text-zinc-400">Loading…</p>}

        {!plansLoading && plans.length === 0 && (
          <div className="flex flex-col items-center py-6 gap-3 text-center">
            <Dumbbell className="text-zinc-300" size={32} />
            <p className="text-sm text-zinc-500">No plans yet</p>
            <button onClick={onGoToImport} className="btn-primary text-sm">
              Import plan
            </button>
          </div>
        )}

        {!plansLoading && plans.length > 0 && (
          <div className="flex flex-col gap-2">
            {plans.map((plan) => {
              const isActive = plan.is_active;
              const isActing = planActionLoading === plan.plan_id;
              const isConfirmingDelete = confirmDeleteId === plan.plan_id;
              const isRenaming = renamingPlanId === plan.plan_id;

              return (
                <div
                  key={plan.plan_id}
                  className={`rounded-lg border p-3 transition-colors ${
                    isActive ? "border-zinc-900 bg-zinc-900" : "border-zinc-100 bg-zinc-50"
                  }`}
                >
                  {/* Name row */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      {isRenaming ? (
                        <div className="flex items-center gap-2">
                          <input
                            autoFocus
                            value={renameValue}
                            onChange={(e) => setRenameValue(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") saveRename(plan.plan_id);
                              if (e.key === "Escape") setRenamingPlanId(null);
                            }}
                            className="input text-sm py-0.5 flex-1"
                            disabled={renameLoading}
                          />
                          <button
                            onClick={() => saveRename(plan.plan_id)}
                            disabled={renameLoading || !renameValue.trim()}
                            className="text-xs font-medium text-green-600 hover:text-green-700 disabled:opacity-40"
                          >
                            {renameLoading ? "…" : "Save"}
                          </button>
                          <button
                            onClick={() => setRenamingPlanId(null)}
                            disabled={renameLoading}
                            className="text-zinc-400 hover:text-zinc-600"
                          >
                            <X size={14} />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5">
                          <p
                            className={`text-sm font-semibold truncate ${
                              isActive ? "text-white" : "text-zinc-900"
                            }`}
                          >
                            {plan.plan_name}
                          </p>
                          {isActive && (
                            <span className="shrink-0 text-xs font-medium bg-white text-zinc-900 px-1.5 py-0.5 rounded-full">
                              Active
                            </span>
                          )}
                          <button
                            onClick={() => {
                              setRenamingPlanId(plan.plan_id);
                              setRenameValue(plan.plan_name);
                              onConfirmDelete(null);
                            }}
                            className={`shrink-0 opacity-0 group-hover:opacity-100 transition-opacity ${
                              isActive
                                ? "text-zinc-500 hover:text-zinc-300"
                                : "text-zinc-400 hover:text-zinc-600"
                            }`}
                            title="Rename"
                          >
                            <Pencil size={12} />
                          </button>
                        </div>
                      )}
                      <p
                        className={`text-xs mt-0.5 ${
                          isActive ? "text-zinc-400" : "text-zinc-500"
                        }`}
                      >
                        {plan.day_count} day{plan.day_count !== 1 ? "s" : ""} ·{" "}
                        {plan.exercise_count} exercises
                      </p>
                    </div>

                    {/* Action buttons */}
                    {!isRenaming && (
                      <div className="flex items-center gap-2 shrink-0">
                        {isConfirmingDelete ? (
                          <>
                            <span
                              className={`text-xs ${
                                isActive ? "text-red-400" : "text-red-500"
                              }`}
                            >
                              {isActive ? "Delete active plan?" : "Delete?"}
                            </span>
                            <button
                              onClick={() => onDeletePlan(plan.plan_id)}
                              disabled={isActing}
                              className="text-xs text-red-600 font-medium hover:text-red-700 disabled:opacity-50"
                            >
                              {isActing ? "…" : "Yes"}
                            </button>
                            <button
                              onClick={() => onConfirmDelete(null)}
                              className="text-zinc-400 hover:text-zinc-600"
                            >
                              <X size={14} />
                            </button>
                          </>
                        ) : (
                          <>
                            {!isActive && (
                              <button
                                onClick={() => onActivatePlan(plan.plan_id)}
                                disabled={isActing}
                                className="text-xs font-medium text-zinc-700 bg-white border border-zinc-200 px-2.5 py-1 rounded-lg hover:bg-zinc-50 disabled:opacity-50"
                              >
                                {isActing ? "Switching…" : "Set active"}
                              </button>
                            )}
                            <button
                              onClick={() => {
                                setRenamingPlanId(null);
                                onConfirmDelete(plan.plan_id);
                              }}
                              disabled={isActing}
                              className={`disabled:opacity-50 ${
                                isActive
                                  ? "text-zinc-500 hover:text-red-400"
                                  : "text-zinc-400 hover:text-red-500"
                              }`}
                              title="Delete plan"
                            >
                              <Trash2 size={14} />
                            </button>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Weekly schedule */}
      {!hasSchedule ? (
        <div className="flex flex-col items-center justify-center py-8 text-center gap-4">
          <p className="text-zinc-500 text-sm">
            No schedule yet — import a plan to see the weekly view
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {schedule.program_name && (
            <p className="text-xs text-zinc-400 uppercase tracking-wide font-medium -mb-1">
              {schedule.program_name} · this week
            </p>
          )}

          {schedule.days.map((day) => {
            const isToday = day.weekday === todayIndex;
            const isRemapping = remappingWeekday === day.weekday;

            return (
              <div
                key={day.weekday}
                className={`rounded-xl border p-4 transition-colors ${
                  isToday ? "bg-zinc-900 border-zinc-900 text-white" : "bg-white border-zinc-100"
                }`}
              >
                {/* Day header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-sm font-semibold ${
                        isToday ? "text-white" : "text-zinc-900"
                      }`}
                    >
                      {day.weekday_name}
                    </span>
                    {isToday && (
                      <span className="text-xs font-medium bg-white text-zinc-900 px-2 py-0.5 rounded-full">
                        Today
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Day type selector */}
                    {activePlanId && availableDayNames.length > 1 ? (
                      <select
                        value={day.day_name}
                        onChange={(e) => handleWeekdayRemap(day.weekday, e.target.value)}
                        disabled={isRemapping}
                        className={`text-xs font-medium px-2 py-0.5 rounded-full border-0 outline-none cursor-pointer appearance-none pr-5 ${
                          day.is_rest
                            ? isToday
                              ? "bg-zinc-700 text-zinc-300"
                              : "bg-zinc-50 text-zinc-400"
                            : isToday
                            ? "bg-zinc-700 text-zinc-100"
                            : "bg-zinc-50 text-zinc-700"
                        } disabled:opacity-60`}
                        style={{ backgroundImage: "none" }}
                        title="Change day type"
                      >
                        {availableDayNames.map((name) => (
                          <option key={name} value={name}>
                            {name}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                          day.is_rest
                            ? isToday
                              ? "bg-zinc-700 text-zinc-300"
                              : "bg-zinc-50 text-zinc-400"
                            : isToday
                            ? "bg-zinc-700 text-zinc-100"
                            : "bg-zinc-50 text-zinc-700"
                        }`}
                      >
                        {day.day_name}
                      </span>
                    )}

                    {/* Edit exercises button (non-rest days only) */}
                    {!day.is_rest && activePlanId && (
                      <button
                        onClick={() => setEditDay(day)}
                        className={`transition-colors ${
                          isToday
                            ? "text-zinc-500 hover:text-zinc-300"
                            : "text-zinc-400 hover:text-zinc-600"
                        }`}
                        title="Edit exercises"
                      >
                        <Pencil size={13} />
                      </button>
                    )}
                  </div>
                </div>

                {/* Day body */}
                {day.is_rest ? (
                  <div className="flex items-center gap-1.5 text-zinc-400">
                    <Moon size={13} />
                    <span className="text-xs">Rest day</span>
                  </div>
                ) : (
                  <div className="flex flex-col gap-1 mt-1">
                    {day.exercises.length === 0 ? (
                      <p
                        className={`text-xs italic ${
                          isToday ? "text-zinc-500" : "text-zinc-400"
                        }`}
                      >
                        No exercises — tap edit to add some
                      </p>
                    ) : (
                      day.exercises.map((ex) => (
                        <div
                          key={ex.exercise_name}
                          className={`flex items-center justify-between text-xs ${
                            isToday ? "text-zinc-300" : "text-zinc-600"
                          }`}
                        >
                          <span>{ex.exercise_name}</span>
                          <span className="font-mono text-zinc-400">
                            {ex.sets}×
                            {ex.rep_min === ex.rep_max
                              ? ex.rep_min
                              : `${ex.rep_min}–${ex.rep_max}`}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Edit day modal */}
      {editDay && activePlanId && (
        <EditDayModal
          day={editDay}
          onSave={async (exercises) => {
            await onUpdateDay(activePlanId, editDay.day_name, exercises);
            setEditDay(null);
          }}
          onClose={() => setEditDay(null)}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Edit day modal
// ---------------------------------------------------------------------------

type EditableExercise = {
  _key: string;
  exercise_name: string;
  sets: number;
  rep_min: number;
  rep_max: number;
};

function EditDayModal({
  day,
  onSave,
  onClose,
}: {
  day: ScheduleDay;
  onSave: (exercises: ScheduleExercise[]) => Promise<void>;
  onClose: () => void;
}) {
  const [exercises, setExercises] = useState<EditableExercise[]>(() =>
    day.exercises.map((ex, i) => ({ ...ex, _key: String(i) }))
  );
  const [newName, setNewName] = useState("");
  const [saving, setSaving] = useState(false);

  function updateExercise(key: string, field: keyof Omit<EditableExercise, "_key">, value: string) {
    setExercises((prev) =>
      prev.map((ex) =>
        ex._key === key
          ? {
              ...ex,
              [field]: field === "exercise_name" ? value : Math.max(1, parseInt(value) || 1),
            }
          : ex
      )
    );
  }

  function removeExercise(key: string) {
    setExercises((prev) => prev.filter((ex) => ex._key !== key));
  }

  function moveExercise(key: string, dir: -1 | 1) {
    setExercises((prev) => {
      const idx = prev.findIndex((ex) => ex._key === key);
      if (idx === -1) return prev;
      const newIdx = idx + dir;
      if (newIdx < 0 || newIdx >= prev.length) return prev;
      const next = [...prev];
      [next[idx], next[newIdx]] = [next[newIdx], next[idx]];
      return next;
    });
  }

  function addExercise() {
    const name = newName.trim();
    if (!name) return;
    setExercises((prev) => [
      ...prev,
      {
        _key: `new-${Date.now()}`,
        exercise_name: name,
        sets: 3,
        rep_min: 8,
        rep_max: 12,
      },
    ]);
    setNewName("");
  }

  async function handleSave() {
    setSaving(true);
    try {
      await onSave(
        exercises.map((ex, i) => ({
          exercise_name: ex.exercise_name,
          sets: ex.sets,
          rep_min: ex.rep_min,
          rep_max: ex.rep_max,
          order: i + 1,
        }))
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end justify-center p-0">
      <div className="bg-white rounded-t-2xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-5 pb-3 border-b border-zinc-100">
          <div>
            <p className="text-xs text-zinc-400 uppercase tracking-wide">Edit exercises</p>
            <p className="text-base font-bold text-zinc-900">{day.day_name} Day</p>
          </div>
          <button onClick={onClose} className="text-zinc-400 hover:text-zinc-600">
            <X size={20} />
          </button>
        </div>

        {/* Exercise list */}
        <div className="flex-1 overflow-y-auto px-5 py-3 flex flex-col gap-2">
          {exercises.length === 0 && (
            <p className="text-sm text-zinc-400 text-center py-4">
              No exercises yet — add one below
            </p>
          )}

          {exercises.map((ex, idx) => (
            <div
              key={ex._key}
              className="flex items-center gap-2 bg-zinc-50 rounded-lg px-3 py-2"
            >
              {/* Reorder */}
              <div className="flex flex-col gap-0.5 shrink-0">
                <button
                  onClick={() => moveExercise(ex._key, -1)}
                  disabled={idx === 0}
                  className="text-zinc-400 hover:text-zinc-700 disabled:opacity-20"
                >
                  <ChevronUp size={14} />
                </button>
                <button
                  onClick={() => moveExercise(ex._key, 1)}
                  disabled={idx === exercises.length - 1}
                  className="text-zinc-400 hover:text-zinc-700 disabled:opacity-20"
                >
                  <ChevronDown size={14} />
                </button>
              </div>

              {/* Name */}
              <input
                value={ex.exercise_name}
                onChange={(e) => updateExercise(ex._key, "exercise_name", e.target.value)}
                className="input text-sm flex-1 min-w-0"
                placeholder="Exercise name"
              />

              {/* Sets */}
              <div className="flex items-center gap-1 shrink-0">
                <span className="text-xs text-zinc-400">sets</span>
                <input
                  type="number"
                  min={1}
                  value={ex.sets}
                  onChange={(e) => updateExercise(ex._key, "sets", e.target.value)}
                  className="input w-12 text-sm text-center"
                />
              </div>

              {/* Rep range */}
              <div className="flex items-center gap-1 shrink-0">
                <input
                  type="number"
                  min={1}
                  value={ex.rep_min}
                  onChange={(e) => updateExercise(ex._key, "rep_min", e.target.value)}
                  className="input w-12 text-sm text-center"
                />
                <span className="text-xs text-zinc-400">–</span>
                <input
                  type="number"
                  min={1}
                  value={ex.rep_max}
                  onChange={(e) => updateExercise(ex._key, "rep_max", e.target.value)}
                  className="input w-12 text-sm text-center"
                />
              </div>

              {/* Remove */}
              <button
                onClick={() => removeExercise(ex._key)}
                className="text-zinc-300 hover:text-red-500 shrink-0"
              >
                <X size={14} />
              </button>
            </div>
          ))}

          {/* Add exercise row */}
          <div className="flex items-center gap-2 mt-1">
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addExercise()}
              placeholder="New exercise name…"
              className="input text-sm flex-1"
            />
            <button
              onClick={addExercise}
              disabled={!newName.trim()}
              className="flex items-center gap-1 text-xs font-medium text-zinc-600 bg-zinc-100 hover:bg-zinc-200 px-3 py-1.5 rounded-lg disabled:opacity-40"
            >
              <Plus size={13} />
              Add
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 px-5 py-4 border-t border-zinc-100">
          <button
            onClick={onClose}
            className="flex-1 btn-outline"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 btn-primary"
          >
            {saving ? "Saving…" : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// History tab
// ---------------------------------------------------------------------------

function HistoryTab({
  sessions, loading, expandedSession, onToggleSession,
}: {
  sessions: SessionHistoryItem[];
  loading: boolean;
  expandedSession: string | null;
  onToggleSession: (id: string) => void;
}) {
  if (loading) {
    return <p className="text-sm text-zinc-400">Loading history…</p>;
  }

  if (sessions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
        <p className="text-zinc-500 text-sm">No sessions yet. Log a workout to see your history.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {sessions.map((session) => (
        <div
          key={session.session_id}
          className="bg-white rounded-xl border border-zinc-100 overflow-hidden"
        >
          <button
            className="w-full flex items-center justify-between p-4 text-left"
            onClick={() => onToggleSession(session.session_id)}
          >
            <div>
              <p className="text-sm font-semibold text-zinc-900">
                {session.day_name} Day
              </p>
              <p className="text-xs text-zinc-500">{session.date}</p>
            </div>
            {session.completed_at ? (
              <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                Completed
              </span>
            ) : (
              <span className="text-xs font-medium text-zinc-400 bg-zinc-50 px-2 py-0.5 rounded-full">
                In progress
              </span>
            )}
          </button>

          {expandedSession === session.session_id && (
            <div className="border-t border-zinc-50 px-4 pb-4 pt-3">
              <p className="text-xs text-zinc-500">
                Started: {new Date(session.started_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </p>
              {session.completed_at && (
                <p className="text-xs text-zinc-500">
                  Finished: {new Date(session.completed_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
