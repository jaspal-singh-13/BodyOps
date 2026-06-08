"use client";

import { useEffect, useState } from "react";
import { Dumbbell, Moon, Plus, Check } from "lucide-react";
import { apiFetch } from "@/lib/api";

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

  useEffect(() => {
    Promise.all([
      apiFetch<TodayWorkout>("/workouts/today").catch(() => null),
      apiFetch<{ sessions: SessionHistoryItem[] }>("/workouts/history").catch(() => ({ sessions: [] })),
      apiFetch<WorkoutSchedule>("/workouts/schedule").catch(() => null),
    ])
      .then(([tw, hist, sched]) => {
        setTodayWorkout(tw);
        setHistory(hist?.sessions ?? []);
        setSchedule(sched);
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
      await Promise.all([refreshToday(), refreshSchedule()]);
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
          Paste your workout in any format — the AI will convert it automatically.
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
}: {
  workout: TodayWorkout | null;
  onStartLogging: () => void;
  onGoToImport: () => void;
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
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-zinc-500 uppercase tracking-wide">Today</p>
          <p className="text-xl font-bold text-zinc-900">{workout.day_name} Day</p>
        </div>
        <p className="text-xs text-zinc-400 font-mono">
          {workout.exercises.length} exercises · ~{workout.estimated_duration_min} min
        </p>
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
  onGoToImport,
}: {
  schedule: WorkoutSchedule | null;
  onGoToImport: () => void;
}) {
  const todayWeekday = new Date().getDay(); // 0=Sun in JS
  // Convert JS Sunday-first (0=Sun) to Python Monday-first (0=Mon)
  const todayIndex = todayWeekday === 0 ? 6 : todayWeekday - 1;

  if (!schedule || schedule.days.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center gap-4">
        <Dumbbell className="text-zinc-300" size={40} />
        <p className="text-zinc-500 text-sm">No schedule imported yet</p>
        <button onClick={onGoToImport} className="btn-primary">
          Import plan
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {schedule.program_name && (
        <p className="text-xs text-zinc-400 uppercase tracking-wide font-medium mb-1">
          {schedule.program_name}
        </p>
      )}

      {schedule.days.map((day) => {
        const isToday = day.weekday === todayIndex;

        return (
          <div
            key={day.weekday}
            className={`rounded-xl border p-4 transition-colors ${
              isToday
                ? "bg-zinc-900 border-zinc-900 text-white"
                : "bg-white border-zinc-100"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className={`text-sm font-semibold ${isToday ? "text-white" : "text-zinc-900"}`}>
                  {day.weekday_name}
                </span>
                {isToday && (
                  <span className="text-xs font-medium bg-white text-zinc-900 px-2 py-0.5 rounded-full">
                    Today
                  </span>
                )}
              </div>
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
            </div>

            {day.is_rest ? (
              <div className={`flex items-center gap-1.5 ${isToday ? "text-zinc-400" : "text-zinc-400"}`}>
                <Moon size={13} />
                <span className="text-xs">Rest day</span>
              </div>
            ) : (
              <div className="flex flex-col gap-1 mt-1">
                {day.exercises.map((ex) => (
                  <div
                    key={ex.exercise_name}
                    className={`flex items-center justify-between text-xs ${
                      isToday ? "text-zinc-300" : "text-zinc-600"
                    }`}
                  >
                    <span>{ex.exercise_name}</span>
                    <span className={`font-mono ${isToday ? "text-zinc-400" : "text-zinc-400"}`}>
                      {ex.sets}×{ex.rep_min === ex.rep_max ? ex.rep_min : `${ex.rep_min}–${ex.rep_max}`}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
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
