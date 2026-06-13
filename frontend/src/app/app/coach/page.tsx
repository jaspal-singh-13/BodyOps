/**
 * Coach page — AI-generated daily summary + weekly review.
 *
 * Layout:
 *   1. Daily coaching card — summary, wins, focus, next step + refresh button
 *   2. Weekly review card  — collapsible, same structure
 *
 * The refresh button is rate-limited to once per hour in the backend; the UI
 * shows the last generated_at time and disables refresh if within the window.
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import { RefreshCw, ChevronDown, ChevronUp, Trophy, Target, ArrowRight, Sparkles } from "lucide-react";
import { apiFetch } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CoachingResponse {
  date: string;
  summary: string;
  wins: string[];
  focus: string[];
  next_step: string;
  generated_at: string;
  cached: boolean;
}

interface WeeklyReviewResponse {
  week_start: string;
  week_end: string;
  summary: string;
  wins: string[];
  focus: string[];
  next_step: string;
  generated_at: string;
  cached: boolean;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function minutesSince(isoTs: string): number {
  try {
    return (Date.now() - new Date(isoTs).getTime()) / 60_000;
  } catch {
    return Infinity;
  }
}

function formatTs(isoTs: string): string {
  try {
    const d = new Date(isoTs);
    const now = new Date();
    const diffMin = Math.round((now.getTime() - d.getTime()) / 60_000);
    if (diffMin < 1) return "just now";
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffMin < 1440) return `${Math.round(diffMin / 60)}h ago`;
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
  } catch {
    return "";
  }
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function CoachPage() {
  const [tz, setTz] = useState("UTC");
  const [mounted, setMounted] = useState(false);

  const [daily, setDaily] = useState<CoachingResponse | null>(null);
  const [weekly, setWeekly] = useState<WeeklyReviewResponse | null>(null);
  const [dailyLoading, setDailyLoading] = useState(true);
  const [weeklyLoading, setWeeklyLoading] = useState(false);
  const [dailyError, setDailyError] = useState<string | null>(null);
  const [weeklyOpen, setWeeklyOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDaily = useCallback(async () => {
    setDailyLoading(true);
    setDailyError(null);
    try {
      const data = await apiFetch<CoachingResponse>("/coach/daily", {
        headers: { "X-Timezone": tz },
      });
      setDaily(data);
    } catch {
      setDailyError("Could not load coaching. Try again.");
    } finally {
      setDailyLoading(false);
    }
  }, [tz]);

  const fetchWeekly = useCallback(async () => {
    setWeeklyLoading(true);
    try {
      const data = await apiFetch<WeeklyReviewResponse>("/coach/weekly", {
        headers: { "X-Timezone": tz },
      });
      setWeekly(data);
    } catch {
      // silent — weekly is optional
    } finally {
      setWeeklyLoading(false);
    }
  }, [tz]);

  useEffect(() => {
    setTz(Intl.DateTimeFormat().resolvedOptions().timeZone);
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) fetchDaily();
  }, [mounted, fetchDaily]);

  useEffect(() => {
    if (weeklyOpen && !weekly && !weeklyLoading) {
      fetchWeekly();
    }
  }, [weeklyOpen, weekly, weeklyLoading, fetchWeekly]);

  async function handleRefresh() {
    if (refreshing) return;
    setRefreshing(true);
    setDailyError(null);
    try {
      const data = await apiFetch<CoachingResponse>("/coach/daily", {
        headers: { "X-Timezone": tz },
      });
      setDaily(data);
    } catch {
      setDailyError("Refresh failed. Try again later.");
    } finally {
      setRefreshing(false);
    }
  }

  const canRefresh = !daily || minutesSince(daily.generated_at) >= 60;

  return (
    <div className="p-4 max-w-lg mx-auto flex flex-col gap-3">
      {/* Header */}
      <div className="pt-2 pb-1">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-zinc-700" />
          <h1 className="text-xl font-extrabold text-zinc-900 tracking-tight">AI Coach</h1>
        </div>
        <p className="text-zinc-500 text-sm mt-0.5">Personalised insights from your data.</p>
      </div>

      {/* Daily Coaching Card */}
      <div className="bg-zinc-900 rounded-2xl p-4 shadow-md">
        <div className="flex items-center justify-between mb-3">
          <p className="font-mono text-[10.5px] font-semibold tracking-widest uppercase"
            style={{ color: "rgba(255,255,255,0.55)" }}>
            Today&apos;s Coaching
          </p>
          <div className="flex items-center gap-2">
            {daily && mounted && (
              <span className="font-mono text-[10px]" style={{ color: "rgba(255,255,255,0.4)" }}>
                {formatTs(daily.generated_at)}{daily.cached ? " · cached" : ""}
              </span>
            )}
            <button
              onClick={handleRefresh}
              disabled={!canRefresh || refreshing || dailyLoading}
              title={canRefresh ? "Refresh coaching" : "Available in < 1h"}
              className={`p-1.5 rounded-lg transition-colors ${
                canRefresh && !refreshing
                  ? "bg-white/10 hover:bg-white/20 cursor-pointer"
                  : "bg-white/5 cursor-not-allowed opacity-40"
              }`}
            >
              <RefreshCw
                size={14}
                color="rgba(255,255,255,0.7)"
                className={refreshing ? "animate-spin" : ""}
              />
            </button>
          </div>
        </div>

        {dailyLoading ? (
          <div className="py-8 flex items-center justify-center">
            <p className="font-mono text-[12px]" style={{ color: "rgba(255,255,255,0.4)" }}>
              Generating…
            </p>
          </div>
        ) : dailyError ? (
          <div className="py-4">
            <p className="text-[13px]" style={{ color: "rgba(255,255,255,0.6)" }}>{dailyError}</p>
            <button
              onClick={fetchDaily}
              className="mt-2 font-mono text-[11px] text-white underline"
            >
              Retry
            </button>
          </div>
        ) : daily ? (
          <CoachingContent coaching={daily} dark />
        ) : (
          <p className="font-mono text-[12px] text-center py-6" style={{ color: "rgba(255,255,255,0.45)" }}>
            Complete your first mission to unlock daily coaching.
          </p>
        )}
      </div>

      {/* Weekly Review Card */}
      <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm overflow-hidden">
        <button
          onClick={() => setWeeklyOpen(!weeklyOpen)}
          className="w-full p-4 flex items-center justify-between hover:bg-zinc-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
              This Week&apos;s Review
            </p>
            {weekly && (
              <span className="font-mono text-[9.5px] text-zinc-300">
                · {weekly.week_start}
              </span>
            )}
          </div>
          {weeklyOpen ? (
            <ChevronUp size={15} className="text-zinc-300" />
          ) : (
            <ChevronDown size={15} className="text-zinc-300" />
          )}
        </button>

        {weeklyOpen && (
          <div className="px-4 pb-4 border-t border-zinc-50">
            {weeklyLoading ? (
              <div className="py-6 flex items-center justify-center">
                <p className="font-mono text-[12px] text-zinc-400">Generating weekly review…</p>
              </div>
            ) : weekly ? (
              <div className="pt-3">
                <div className="flex items-start justify-between mb-1">
                  <span />
                  {weekly && (
                    <span className="font-mono text-[9.5px] text-zinc-300">
                      {weekly.week_start} – {weekly.week_end}
                    </span>
                  )}
                </div>
                <CoachingContent coaching={weekly} dark={false} />
              </div>
            ) : (
              <p className="py-4 font-mono text-[12px] text-zinc-400">No review available yet.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Shared coaching content block
// ---------------------------------------------------------------------------

function CoachingContent({
  coaching,
  dark,
}: {
  coaching: CoachingResponse | WeeklyReviewResponse;
  dark: boolean;
}) {
  const text = dark ? "text-white" : "text-zinc-800";
  const sub = dark ? "rgba(255,255,255,0.7)" : "rgb(63,63,70)";
  const chip = dark ? "bg-white/10 text-white" : "bg-zinc-100 text-zinc-700";
  const divider = dark ? "border-white/10" : "border-zinc-100";

  return (
    <div className="flex flex-col gap-3">
      {/* Summary */}
      <p className={`text-[14px] leading-relaxed font-medium ${text}`}>{coaching.summary}</p>

      {/* Wins */}
      {coaching.wins.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 mb-1.5">
            <Trophy size={11} style={{ color: sub }} />
            <span className="font-mono text-[10px] font-semibold uppercase tracking-wider" style={{ color: sub }}>
              Wins
            </span>
          </div>
          <div className="flex flex-col gap-1">
            {coaching.wins.map((w, i) => (
              <span key={i} className={`text-[12px] px-2.5 py-1 rounded-full inline-block ${chip}`}>
                {w}
              </span>
            ))}
          </div>
        </div>
      )}

      {coaching.wins.length > 0 && coaching.focus.length > 0 && (
        <div className={`border-t ${divider}`} />
      )}

      {/* Focus */}
      {coaching.focus.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 mb-1.5">
            <Target size={11} style={{ color: sub }} />
            <span className="font-mono text-[10px] font-semibold uppercase tracking-wider" style={{ color: sub }}>
              Focus
            </span>
          </div>
          <div className="flex flex-col gap-1">
            {coaching.focus.map((f, i) => (
              <span key={i} className={`text-[12px] px-2.5 py-1 rounded-full inline-block ${chip}`}>
                {f}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Next step */}
      {coaching.next_step && (
        <div className={`mt-1 flex items-start gap-2 rounded-xl p-3 ${dark ? "bg-white/10" : "bg-zinc-50"}`}>
          <ArrowRight size={14} className="mt-0.5 shrink-0" style={{ color: sub }} />
          <p className="text-[12.5px] font-semibold" style={{ color: sub }}>
            {coaching.next_step}
          </p>
        </div>
      )}
    </div>
  );
}
