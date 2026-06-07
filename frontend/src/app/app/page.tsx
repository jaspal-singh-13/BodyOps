/**
 * Dashboard page — landing page after login for authenticated users.
 *
 * Fetches settings, latest weight entry, and projected goal date in parallel.
 * Redirects to `/onboarding` if the settings fetch fails with a 4xx (user has
 * not completed onboarding yet — no settings row exists in the sheet).
 *
 * Weight display priority:
 *   1. Most recent logged entry (`history[0].weight_kg`) if any entries exist
 *   2. `settings.current_weight_kg` as fallback (set during onboarding)
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

interface Settings {
  name: string;
  current_weight_kg: number;
  goal_weight_kg: number;
  calorie_target: number;
  protein_target_g: number;
}

interface HistoryItem {
  date: string;
  weight_kg: number;
  change_kg: number | null;
}

interface TrendData {
  projected_goal_date: string | null;
}

export default function DashboardPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [latestWeight, setLatestWeight] = useState<HistoryItem | null>(null);
  const [projectedDate, setProjectedDate] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Settings>("/settings")
      .then((data) => setSettings(data))
      .catch(() => router.push("/onboarding"))
      .finally(() => setLoading(false));

    // Failures here are non-fatal — stats just won't appear
    apiFetch<HistoryItem[]>("/weight/history")
      .then((h) => { if (h.length > 0) setLatestWeight(h[0]); })
      .catch(() => {});

    apiFetch<TrendData>("/weight/trend")
      .then((t) => setProjectedDate(t.projected_goal_date))
      .catch(() => {});
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400 text-sm">Loading…</p>
      </div>
    );
  }

  if (!settings) return null;

  const displayWeight = latestWeight?.weight_kg ?? settings.current_weight_kg;
  const remaining = displayWeight - settings.goal_weight_kg;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-zinc-900 mb-1">
        Good morning, {settings.name.split(" ")[0]}
      </h1>
      <p className="text-zinc-500 text-sm mb-8">Let&apos;s crush today.</p>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <StatCard label="Current weight" value={`${displayWeight} kg`} />
        <StatCard label="Goal weight" value={`${settings.goal_weight_kg} kg`} />
        <StatCard label="To lose" value={`${remaining.toFixed(1)} kg`} />
        <StatCard label="Calorie target" value={`${settings.calorie_target} kcal`} />
        <StatCard label="Protein target" value={`${settings.protein_target_g} g`} />
        {projectedDate && (
          <StatCard label="Goal by" value={projectedDate} />
        )}
      </div>
    </div>
  );
}

/** Key-value stat tile used in the dashboard grid. */
function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl border border-zinc-100 p-4">
      <p className="text-xs text-zinc-500 mb-1">{label}</p>
      <p className="text-xl font-semibold text-zinc-900">{value}</p>
    </div>
  );
}
