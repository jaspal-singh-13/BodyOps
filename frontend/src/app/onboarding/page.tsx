/**
 * 3-step onboarding wizard — collects user profile, targets, and preferences,
 * then saves them via `POST /settings` and redirects to `/app`.
 *
 * Step 1 — Profile: name, sex, current weight, goal weight, height, age, start date
 * Step 2 — Targets: daily calorie and protein targets (auto-calculated, editable)
 * Step 3 — Schedule: wake-up time for daily mission notifications
 *
 * `calcTargets` derives default values using:
 *   Mifflin-St Jeor BMR  = 10w + 6.25h − 5a + (5 for male | −161 for female)
 *   Calorie target       = BMR × 1.55 (moderate activity) − 500 kcal (deficit)
 *   Protein target       = body_weight_kg × 1.8 g
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

interface Step1 {
  name: string;
  sex: "male" | "female";
  current_weight_kg: string;
  height_cm: string;
  age: string;
  goal_weight_kg: string;
  start_date: string;
}

interface Step2 {
  calorie_target: string;
  protein_target_g: string;
  carb_target_g: string;
  fat_target_g: string;
}

interface Step3 {
  wake_up_time: string;
}

/**
 * Calculate calorie and protein targets from Step 1 profile data.
 *
 * Uses Mifflin-St Jeor BMR with a 1.55 moderate-activity multiplier and a
 * 500 kcal deficit for fat loss. Protein is set to 1.8 g per kg of body weight,
 * which is at the high end for muscle retention during a cut.
 */
function calcTargets(s1: Step1): { calories: number; protein: number; carbs: number; fat: number } {
  const w = parseFloat(s1.current_weight_kg) || 0;
  const h = parseFloat(s1.height_cm) || 0;
  const a = parseInt(s1.age) || 0;
  const offset = s1.sex === "male" ? 5 : -161;
  const bmr = 10 * w + 6.25 * h - 5 * a + offset;
  const calories = Math.max(1200, Math.round(bmr * 1.55 - 500));
  const protein = Math.round(w * 1.8);
  const proteinKcal = protein * 4;
  const remaining = Math.max(0, calories - proteinKcal);
  const carbs = Math.round((remaining * 0.55) / 4);
  const fat = Math.round((remaining * 0.45) / 9);
  return { calories, protein, carbs, fat };
}

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Local calendar date — toISOString() would give the UTC date, which is
  // yesterday for timezones ahead of UTC during the early morning.
  const today = (() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  })();

  const [step1, setStep1] = useState<Step1>({
    name: "",
    sex: "male",
    current_weight_kg: "",
    height_cm: "",
    age: "",
    goal_weight_kg: "",
    start_date: today,
  });

  const [step2, setStep2] = useState<Step2>({
    calorie_target: "",
    protein_target_g: "",
    carb_target_g: "",
    fat_target_g: "",
  });

  const [step3, setStep3] = useState<Step3>({ wake_up_time: "07:00" });

  /** Pre-populate Step 2 targets from the Step 1 profile before advancing. */
  function goToStep2() {
    const { calories, protein, carbs, fat } = calcTargets(step1);
    setStep2({
      calorie_target: calories > 0 ? String(calories) : "",
      protein_target_g: protein > 0 ? String(protein) : "",
      carb_target_g: carbs > 0 ? String(carbs) : "",
      fat_target_g: fat > 0 ? String(fat) : "",
    });
    setStep(2);
  }

  async function submit() {
    setError("");
    setLoading(true);
    try {
      await apiFetch("/settings", {
        method: "POST",
        body: JSON.stringify({
          name: step1.name,
          current_weight_kg: parseFloat(step1.current_weight_kg),
          height_cm: parseFloat(step1.height_cm),
          age: parseInt(step1.age),
          goal_weight_kg: parseFloat(step1.goal_weight_kg),
          start_date: step1.start_date,
          calorie_target: parseInt(step2.calorie_target),
          protein_target_g: parseInt(step2.protein_target_g),
          carb_target_g: parseInt(step2.carb_target_g) || 0,
          fat_target_g: parseInt(step2.fat_target_g) || 0,
          wake_up_time: step3.wake_up_time,
        }),
      });
      router.push("/app");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to save. Try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-zinc-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl border border-zinc-100 shadow-sm p-8">
        {/* Progress indicator — filled segments show completed steps */}
        <div className="flex items-center gap-2 mb-6">
          {[1, 2, 3].map((n) => (
            <div
              key={n}
              className={`h-1.5 flex-1 rounded-full transition-colors ${
                n <= step ? "bg-zinc-900" : "bg-zinc-100"
              }`}
            />
          ))}
        </div>

        {step === 1 && (
          <div>
            <h2 className="text-xl font-bold text-zinc-900 mb-1">Your profile</h2>
            <p className="text-zinc-500 text-sm mb-6">Tell us about yourself</p>
            <div className="flex flex-col gap-4">
              <Field label="Name">
                <input
                  type="text"
                  value={step1.name}
                  onChange={(e) => setStep1({ ...step1, name: e.target.value })}
                  className="input"
                  placeholder="Jaspal Singh"
                  required
                />
              </Field>
              <Field label="Sex">
                <select
                  value={step1.sex}
                  onChange={(e) =>
                    setStep1({ ...step1, sex: e.target.value as "male" | "female" })
                  }
                  className="input"
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
              </Field>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Current weight (kg)">
                  <input
                    type="number"
                    step="0.1"
                    value={step1.current_weight_kg}
                    onChange={(e) =>
                      setStep1({ ...step1, current_weight_kg: e.target.value })
                    }
                    className="input"
                    placeholder="107"
                    required
                  />
                </Field>
                <Field label="Goal weight (kg)">
                  <input
                    type="number"
                    step="0.1"
                    value={step1.goal_weight_kg}
                    onChange={(e) =>
                      setStep1({ ...step1, goal_weight_kg: e.target.value })
                    }
                    className="input"
                    placeholder="77"
                    required
                  />
                </Field>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Field label="Height (cm)">
                  <input
                    type="number"
                    value={step1.height_cm}
                    onChange={(e) => setStep1({ ...step1, height_cm: e.target.value })}
                    className="input"
                    placeholder="175"
                    required
                  />
                </Field>
                <Field label="Age">
                  <input
                    type="number"
                    value={step1.age}
                    onChange={(e) => setStep1({ ...step1, age: e.target.value })}
                    className="input"
                    placeholder="25"
                    required
                  />
                </Field>
              </div>
              <Field label="Start date">
                <input
                  type="date"
                  value={step1.start_date}
                  onChange={(e) => setStep1({ ...step1, start_date: e.target.value })}
                  className="input"
                  required
                />
              </Field>
              <button
                onClick={goToStep2}
                disabled={
                  !step1.name ||
                  !step1.current_weight_kg ||
                  !step1.height_cm ||
                  !step1.age ||
                  !step1.goal_weight_kg
                }
                className="btn-primary"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-xl font-bold text-zinc-900 mb-1">Your targets</h2>
            <p className="text-zinc-500 text-sm mb-6">
              Calculated from your profile — adjust if needed
            </p>
            <div className="flex flex-col gap-4">
              <Field label="Daily calorie target (kcal)">
                <input
                  type="number"
                  value={step2.calorie_target}
                  onChange={(e) =>
                    setStep2({ ...step2, calorie_target: e.target.value })
                  }
                  className="input"
                  required
                />
              </Field>
              <Field label="Daily protein target (g)">
                <input
                  type="number"
                  value={step2.protein_target_g}
                  onChange={(e) =>
                    setStep2({ ...step2, protein_target_g: e.target.value })
                  }
                  className="input"
                  required
                />
              </Field>
              <Field label="Daily carbs target (g)">
                <input
                  type="number"
                  value={step2.carb_target_g}
                  onChange={(e) =>
                    setStep2({ ...step2, carb_target_g: e.target.value })
                  }
                  className="input"
                />
              </Field>
              <Field label="Daily fat target (g)">
                <input
                  type="number"
                  value={step2.fat_target_g}
                  onChange={(e) =>
                    setStep2({ ...step2, fat_target_g: e.target.value })
                  }
                  className="input"
                />
              </Field>
              <p className="text-xs text-zinc-400">
                Mifflin-St Jeor BMR × 1.55 activity factor − 500 kcal deficit.
                Protein: {step1.current_weight_kg} kg × 1.8 g.
              </p>
              <div className="flex gap-3">
                <button onClick={() => setStep(1)} className="btn-outline flex-1">
                  Back
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={!step2.calorie_target || !step2.protein_target_g}                  className="btn-primary flex-1"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="text-xl font-bold text-zinc-900 mb-1">Wake-up time</h2>
            <p className="text-zinc-500 text-sm mb-6">
              Used to schedule your daily missions
            </p>
            <div className="flex flex-col gap-4">
              <Field label="Wake-up time">
                <input
                  type="time"
                  value={step3.wake_up_time}
                  onChange={(e) => setStep3({ wake_up_time: e.target.value })}
                  className="input"
                  required
                />
              </Field>
              {error && <p className="text-sm text-red-500">{error}</p>}
              <div className="flex gap-3">
                <button onClick={() => setStep(2)} className="btn-outline flex-1">
                  Back
                </button>
                <button
                  onClick={submit}
                  disabled={loading || !step3.wake_up_time}
                  className="btn-primary flex-1"
                >
                  {loading ? "Saving…" : "Get started"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/** Labelled form field wrapper. */
function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-zinc-700">{label}</label>
      {children}
    </div>
  );
}
