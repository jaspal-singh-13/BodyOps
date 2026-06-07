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

export default function DashboardPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<Settings>("/settings")
      .then((data) => setSettings(data))
      .catch(() => router.push("/onboarding"))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-zinc-400 text-sm">Loading…</p>
      </div>
    );
  }

  if (!settings) return null;

  const remaining = settings.current_weight_kg - settings.goal_weight_kg;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-zinc-900 mb-1">
        Good morning, {settings.name.split(" ")[0]}
      </h1>
      <p className="text-zinc-500 text-sm mb-8">Let&apos;s crush today.</p>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <StatCard label="Current weight" value={`${settings.current_weight_kg} kg`} />
        <StatCard label="Goal weight" value={`${settings.goal_weight_kg} kg`} />
        <StatCard label="To lose" value={`${remaining.toFixed(1)} kg`} />
        <StatCard label="Calorie target" value={`${settings.calorie_target} kcal`} />
        <StatCard label="Protein target" value={`${settings.protein_target_g} g`} />
      </div>
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
