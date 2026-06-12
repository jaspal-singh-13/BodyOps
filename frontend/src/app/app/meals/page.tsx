"use client";

/**
 * Meals page — meal photo logging flow.
 *
 * 5 screens managed via local state, mirroring design/app/m-meals.jsx:
 *   list      — today's meals + nutrition summary + history
 *   camera    — full-bleed dark capture UI (file input → analyzing)
 *   analyzing — loading state while POST /meals/analyze runs
 *   analysis  — review / edit detected items, confirm
 *   detail    — single meal detail view
 */

import { Suspense, useEffect, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Camera,
  CameraOff,
  ImageUp,
  X,
  ChevronLeft,
  Check,
  Plus,
  Edit,
  Info,
  ChevronRight,
  Zap,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useRefresh } from "@/lib/refresh";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type Confidence = "high" | "med" | "low";
type MealType = "Breakfast" | "Lunch" | "Dinner" | "Snack";

interface DetectedItem {
  name: string;
  quantity: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  confidence: Confidence;
}

interface MacroTotal {
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

interface AnalyzeResponse {
  title: string;
  confidence: Confidence;
  detected: DetectedItem[];
  total: MacroTotal;
  drive_url: string;
}

interface SavedMealResponse {
  meal_id: string;
  meal_type: MealType;
  date: string;
  total: MacroTotal;
  daily_nutrition: DailyNutrition;
}

interface DailyNutrition {
  date: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  target_calories: number;
  target_protein_g: number;
  target_carbs_g: number;
  target_fat_g: number;
  meals_count: number;
}

interface MealHistoryDay {
  date: string;
  display_date: string;
  meals_count: number;
  total_calories: number;
  total_protein_g: number;
}

type Screen = "list" | "camera" | "analyzing" | "analysis" | "detail";

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function MealsPage() {
  return (
    <Suspense>
      <MealsPageInner />
    </Suspense>
  );
}

function MealsPageInner() {
  const { triggerRefresh } = useRefresh();
  const searchParams = useSearchParams();
  const router = useRouter();

  const [screen, setScreen] = useState<Screen>(
    searchParams.get("mode") === "camera" ? "camera" : "list"
  );

  // List screen data
  const [nutrition, setNutrition] = useState<DailyNutrition | null>(null);
  const [history, setHistory] = useState<MealHistoryDay[]>([]);
  const [nutritionLoading, setNutritionLoading] = useState(true);

  // Camera / analyzing
  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const [capturedPreviewUrl, setCapturedPreviewUrl] = useState<string | null>(null);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  // Analysis screen
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResponse | null>(null);
  const [editedItems, setEditedItems] = useState<DetectedItem[]>([]);
  const [mealType, setMealType] = useState<MealType>("Lunch");
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    fetchNutrition();
    fetchHistory();
  }, []);

  function fetchNutrition() {
    setNutritionLoading(true);
    apiFetch<DailyNutrition>("/meals/today")
      .then(setNutrition)
      .catch(() => {})
      .finally(() => setNutritionLoading(false));
  }

  function fetchHistory() {
    apiFetch<MealHistoryDay[]>("/meals/history")
      .then(setHistory)
      .catch(() => {});
  }

  // ---------- Camera / capture ----------

  function handleFileCapture(file: File) {
    setCapturedFile(file);
    setCapturedPreviewUrl(URL.createObjectURL(file));
    setAnalyzeError(null);
    setScreen("analyzing");
  }

  async function runAnalysis(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await apiFetch<AnalyzeResponse>("/meals/analyze", {
        method: "POST",
        body: formData,
      });
      setAnalysisResult(res);
      setEditedItems([...res.detected]);
      setScreen("analysis");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Analysis failed";
      setAnalyzeError(msg);
      setScreen("camera");
    }
  }

  async function confirmMeal() {
    if (!analysisResult) return;
    setConfirming(true);
    try {
      // Use local calendar date so meals are filed under the correct day for
      // users east/west of UTC (toISOString() returns UTC which can be wrong).
      const d = new Date();
      const localToday = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
      await apiFetch<SavedMealResponse>("/meals", {
        method: "POST",
        body: JSON.stringify({
          meal_type: mealType,
          items: editedItems,
          drive_url: analysisResult.drive_url,
          date: localToday,
        }),
      });
      fetchNutrition();
      fetchHistory();
      triggerRefresh();
      setScreen("list");
    } catch {
      // stay on analysis screen; user can retry
    } finally {
      setConfirming(false);
    }
  }

  // ---------- Screen renders ----------

  if (screen === "camera") {
    return <CameraScreen
      onClose={() => setScreen("list")}
      onFileCapture={handleFileCapture}
      error={analyzeError}
    />;
  }

  if (screen === "analyzing" && capturedFile) {
    return <AnalyzingScreen
      previewUrl={capturedPreviewUrl}
      file={capturedFile}
      onComplete={runAnalysis}
    />;
  }

  if (screen === "analysis" && analysisResult) {
    return <AnalysisScreen
      result={analysisResult}
      previewUrl={capturedPreviewUrl}
      items={editedItems}
      mealType={mealType}
      confirming={confirming}
      onRetake={() => setScreen("camera")}
      onItemsChange={setEditedItems}
      onMealTypeChange={setMealType}
      onConfirm={confirmMeal}
      onBack={() => setScreen("list")}
    />;
  }

  // Default: list screen
  return <ListScreen
    nutrition={nutrition}
    history={history}
    nutritionLoading={nutritionLoading}
    onCameraClick={() => setScreen("camera")}
  />;
}

// ---------------------------------------------------------------------------
// List screen
// ---------------------------------------------------------------------------

function ListScreen({
  nutrition,
  history,
  nutritionLoading,
  onCameraClick,
}: {
  nutrition: DailyNutrition | null;
  history: MealHistoryDay[];
  nutritionLoading: boolean;
  onCameraClick: () => void;
}) {
  const d = new Date();
  const localToday = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const today = history[0]?.date === localToday ? history[0] : null;
  const earlier = today ? history.slice(1) : history;

  return (
    <div className="flex flex-col min-h-screen bg-zinc-50">
      {/* Header */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2 bg-zinc-50">
        <div>
          <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
            Nutrition
          </p>
          <h1 className="text-[21px] font-extrabold tracking-tight mt-0.5">Meals</h1>
        </div>
        <button
          onClick={onCameraClick}
          className="w-[42px] h-[42px] rounded-xl bg-zinc-900 flex items-center justify-center"
        >
          <Camera size={21} color="#fff" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-6 flex flex-col gap-3 pt-2">
        {/* Today's intake summary */}
        <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
          <div className="flex items-center justify-between">
            <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
              Today&apos;s intake
            </p>
            {nutrition && (
              <span className="bg-zinc-100 text-zinc-600 text-[11px] font-mono px-2 py-0.5 rounded-full">
                {nutrition.target_calories - nutrition.calories} kcal left
              </span>
            )}
          </div>

          {nutritionLoading ? (
            <div className="h-10 bg-zinc-100 rounded animate-pulse mt-3" />
          ) : nutrition ? (
            <>
              <div className="mt-3">
                <div className="flex items-baseline gap-1.5">
                  <span className="font-mono text-[26px] font-bold">
                    {nutrition.calories.toLocaleString()}
                  </span>
                  <span className="font-mono text-[12px] text-zinc-400">
                    / {nutrition.target_calories.toLocaleString()} kcal
                  </span>
                </div>
                <ProgressBar
                  value={(nutrition.calories / nutrition.target_calories) * 100}
                  className="mt-2"
                />
              </div>
              <div className="flex gap-2 mt-3">
                {(
                  [
                    ["Protein", nutrition.protein_g, nutrition.target_protein_g],
                    ["Carbs", nutrition.carbs_g, nutrition.target_carbs_g],
                    ["Fat", nutrition.fat_g, nutrition.target_fat_g],
                  ] as [string, number, number][]
                ).map(([label, v, t]) => (
                  <div
                    key={label}
                    className="flex-1 bg-zinc-50 border border-zinc-200 rounded-lg px-2.5 py-2"
                  >
                    <p className="font-mono text-[9.5px] text-zinc-400 uppercase tracking-wider">
                      {label}
                    </p>
                    <p className="font-mono text-[14px] font-bold mt-0.5">
                      {Math.round(v)}
                      <span className="text-[10px] text-zinc-400 font-medium">
                        /{Math.round(t)}g
                      </span>
                    </p>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-sm text-zinc-400 mt-3">
              Log your first meal to start tracking.
            </p>
          )}
        </div>

        {/* Today's meals */}
        {today && today.meals_count > 0 && (
          <>
            <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase pl-1">
              Today · {today.meals_count} logged
            </p>
            <div className="flex flex-col gap-2">
              {/* Placeholder rows — real detail requires fetching meal records */}
              <PlaceholderMealCard
                label={today.display_date}
                kcal={today.total_calories}
                protein={today.total_protein_g}
                count={today.meals_count}
              />
            </div>
          </>
        )}

        {/* Empty state */}
        {(!nutrition || nutrition.meals_count === 0) && !nutritionLoading && (
          <div className="flex flex-col items-center justify-center py-12 gap-4">
            <div className="w-16 h-16 rounded-2xl bg-zinc-100 flex items-center justify-center">
              <Camera size={28} className="text-zinc-400" />
            </div>
            <p className="text-sm text-zinc-400 text-center">
              Tap the camera to log your first meal
            </p>
            <button
              onClick={onCameraClick}
              className="btn-primary px-6 py-2.5 text-sm"
            >
              Log a meal
            </button>
          </div>
        )}

        {/* Earlier days */}
        {earlier.length > 0 && (
          <>
            <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase pl-1 mt-1">
              Earlier
            </p>
            <div className="flex flex-col gap-2">
              {earlier.map((d) => (
                <div
                  key={d.date}
                  className="bg-white rounded-xl border border-zinc-100 p-3.5 flex items-center justify-between"
                >
                  <div>
                    <p className="text-[13.5px] font-semibold">{d.display_date}</p>
                    <p className="font-mono text-[10.5px] text-zinc-400 mt-0.5">
                      {d.meals_count} meals
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-[15px] font-bold">
                      {d.total_calories.toLocaleString()}
                      <span className="text-[11px] text-zinc-400"> kcal</span>
                    </p>
                    <p className="font-mono text-[10.5px] text-zinc-400 mt-0.5">
                      {Math.round(d.total_protein_g)}g protein
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function PlaceholderMealCard({
  label,
  kcal,
  protein,
  count,
}: {
  label: string;
  kcal: number;
  protein: number;
  count: number;
}) {
  return (
    <div className="bg-white rounded-xl border border-zinc-100 p-3.5 flex items-center justify-between">
      <div>
        <p className="text-[13.5px] font-semibold">{label}</p>
        <p className="font-mono text-[10.5px] text-zinc-400 mt-0.5">{count} meals</p>
      </div>
      <div className="text-right">
        <p className="font-mono text-[15px] font-bold">
          {kcal.toLocaleString()}
          <span className="text-[11px] text-zinc-400"> kcal</span>
        </p>
        <p className="font-mono text-[10.5px] text-zinc-400 mt-0.5">
          {Math.round(protein)}g protein
        </p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Camera screen — real getUserMedia live preview
// ---------------------------------------------------------------------------

function CameraScreen({
  onClose,
  onFileCapture,
  error,
}: {
  onClose: () => void;
  onFileCapture: (file: File) => void;
  error: string | null;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const uploadInputRef = useRef<HTMLInputElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [cameraUnavailable, setCameraUnavailable] = useState(false);

  useEffect(() => {
    let active = true;

    async function startCamera() {
      if (!navigator.mediaDevices?.getUserMedia) {
        setCameraUnavailable(true);
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: { ideal: 1920 }, height: { ideal: 1080 } },
        });
        if (!active) { stream.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        if (!active) return;
        if (err instanceof DOMException && err.name === "NotAllowedError") {
          setPermissionDenied(true);
        } else {
          setCameraUnavailable(true);
        }
      }
    }

    startCamera();

    return () => {
      active = false;
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    };
  }, []);

  function handleShutter() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !cameraReady) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d")?.drawImage(video, 0, 0);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        const file = new File([blob], `meal-${Date.now()}.jpg`, { type: "image/jpeg" });
        onFileCapture(file);
      },
      "image/jpeg",
      0.92
    );
  }

  function handleUploadChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    onFileCapture(file);
  }

  const showError = permissionDenied || cameraUnavailable;

  return (
    /* fixed inset-0 = covers full viewport, escaping the layout's main/sidebar */
    <div
      className="fixed inset-0 z-50 flex flex-col overflow-hidden"
      style={{ background: "#1a1917" }}
    >
      {/* Hidden gallery upload input — no capture attribute so it opens files/photos */}
      <input
        ref={uploadInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleUploadChange}
      />
      {/* Off-screen canvas used for frame capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Top bar */}
      <div className="flex items-center justify-between px-4 pt-safe pt-4 pb-2 relative z-10 shrink-0">
        <button
          onClick={onClose}
          className="w-[38px] h-[38px] rounded-full flex items-center justify-center"
          style={{ background: "rgba(255,255,255,0.12)" }}
        >
          <X size={18} color="#fff" />
        </button>
        <span
          className="font-mono text-[11.5px] font-semibold tracking-widest"
          style={{ color: "rgba(255,255,255,0.7)" }}
        >
          SNAP YOUR MEAL
        </span>
        <div
          className="w-[38px] h-[38px] rounded-full flex items-center justify-center"
          style={{ background: "rgba(255,255,255,0.12)" }}
        >
          <Zap size={18} color="rgba(255,255,255,0.7)" />
        </div>
      </div>

      {/* Viewfinder — full-width, flex-1 to fill remaining height */}
      <div className="flex-1 relative overflow-hidden">
        {showError ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 px-8 text-center">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center"
              style={{ background: "rgba(255,255,255,0.08)" }}
            >
              <CameraOff size={30} color="rgba(255,255,255,0.6)" />
            </div>
            <p className="font-mono text-[13px] font-semibold" style={{ color: "rgba(255,255,255,0.85)" }}>
              {permissionDenied ? "Camera access denied" : "Camera not available"}
            </p>
            <p className="font-mono text-[11px] leading-relaxed" style={{ color: "rgba(255,255,255,0.45)" }}>
              {permissionDenied
                ? "Allow camera access in your browser or OS settings, then refresh. You can still upload a photo below."
                : "Your device or browser doesn't support live camera. Use the upload button below to pick a photo."}
            </p>
          </div>
        ) : (
          <>
            {/* Live video — cover entire viewfinder area */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              onLoadedMetadata={() => setCameraReady(true)}
              onCanPlay={() => setCameraReady(true)}
              className="absolute inset-0 w-full h-full object-cover"
            />
            {/* Loading overlay while stream initialises */}
            {!cameraReady && (
              <div
                className="absolute inset-0 flex items-center justify-center"
                style={{ background: "#26241f" }}
              >
                <span
                  className="font-mono text-[11px] uppercase tracking-wider px-2.5 py-1.5 rounded"
                  style={{ background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.18)", color: "rgba(255,255,255,0.7)" }}
                >
                  Starting camera…
                </span>
              </div>
            )}
            {/* Corner guides */}
            {(["tl", "tr", "bl", "br"] as const).map((pos) => (
              <div
                key={pos}
                style={{
                  position: "absolute",
                  width: 26, height: 26,
                  ...(pos[0] === "t" ? { top: 14 } : { bottom: 14 }),
                  ...(pos[1] === "l" ? { left: 14 } : { right: 14 }),
                  borderColor: "rgba(255,255,255,0.85)",
                  borderStyle: "solid",
                  borderWidth: 0,
                  ...(pos[0] === "t" ? { borderTopWidth: 3 } : { borderBottomWidth: 3 }),
                  ...(pos[1] === "l" ? { borderLeftWidth: 3 } : { borderRightWidth: 3 }),
                  borderRadius: pos === "tl" ? "10px 0 0 0" : pos === "tr" ? "0 10px 0 0" : pos === "bl" ? "0 0 0 10px" : "0 0 10px 0",
                  zIndex: 10,
                }}
              />
            ))}
            <p
              className="absolute bottom-4 left-0 right-0 text-center font-mono text-[11px] z-10"
              style={{ color: "rgba(255,255,255,0.55)" }}
            >
              Center your plate in the frame
            </p>
          </>
        )}
      </div>

      {/* Analysis error feedback */}
      {error && (
        <p className="text-red-400 text-xs font-mono text-center px-4 pt-2 shrink-0">{error}</p>
      )}

      {/* Controls — safe-area padding so it clears home indicators on iOS/Android */}
      <div
        className="px-4 pt-5 flex items-center justify-between shrink-0"
        style={{ paddingBottom: "max(2rem, env(safe-area-inset-bottom, 2rem))" }}
      >
        {/* Upload from gallery */}
        <button
          onClick={() => uploadInputRef.current?.click()}
          className="w-14 h-14 rounded-xl flex flex-col items-center justify-center gap-1"
          style={{ background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.16)" }}
          aria-label="Upload photo from gallery"
        >
          <ImageUp size={20} color="rgba(255,255,255,0.85)" />
          <span className="font-mono text-[7px] font-bold" style={{ color: "rgba(255,255,255,0.6)" }}>
            UPLOAD
          </span>
        </button>

        {/* Shutter — always visible; pulses while camera warms up */}
        <button
          onClick={handleShutter}
          disabled={!cameraReady}
          className="w-[74px] h-[74px] rounded-full flex items-center justify-center"
          style={{
            background: "transparent",
            border: "4px solid rgba(255,255,255,0.9)",
          }}
          aria-label="Take photo"
        >
          {cameraReady ? (
            <div className="w-[58px] h-[58px] rounded-full bg-white" />
          ) : (
            <div
              className="w-[58px] h-[58px] rounded-full"
              style={{
                background: "rgba(255,255,255,0.25)",
                animation: "boPulse 1.2s ease-in-out infinite",
              }}
            />
          )}
        </button>
        <style>{`@keyframes boPulse { 0%,100%{opacity:.25} 50%{opacity:.6} }`}</style>

        {/* Manual / upload alias */}
        <button
          onClick={() => uploadInputRef.current?.click()}
          className="w-14 h-14 rounded-xl flex flex-col items-center justify-center gap-0.5"
          style={{ background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.16)" }}
          aria-label="Manual entry"
        >
          <Edit size={17} color="rgba(255,255,255,0.85)" />
          <span className="font-mono text-[7.5px] font-bold" style={{ color: "rgba(255,255,255,0.7)" }}>
            MANUAL
          </span>
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Analyzing screen
// ---------------------------------------------------------------------------

function AnalyzingScreen({
  previewUrl,
  file,
  onComplete,
}: {
  previewUrl: string | null;
  file: File;
  onComplete: (file: File) => Promise<void>;
}) {
  const [step, setStep] = useState(0);
  const steps = ["Detecting food items", "Estimating portions", "Calculating macros"];
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const interval = setInterval(
      () => setStep((s) => Math.min(s + 1, steps.length - 1)),
      700
    );
    onComplete(file).finally(() => clearInterval(interval));
    return () => clearInterval(interval);
  }, [file, onComplete, steps.length]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-zinc-50 p-7 gap-6">
      {/* Meal photo with scan animation */}
      <div className="relative w-[200px] h-[200px]">
        {previewUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={previewUrl}
            alt="Meal"
            className="w-full h-full object-cover rounded-2xl"
          />
        ) : (
          <div className="w-full h-full rounded-2xl bg-zinc-200" />
        )}
        {/* Scan line */}
        <div
          className="absolute inset-0 rounded-2xl overflow-hidden"
          aria-hidden
        >
          <div
            className="absolute left-0 right-0 h-[3px] bg-zinc-900"
            style={{
              boxShadow: "0 0 12px 2px rgba(29,28,26,0.4)",
              animation: "boScan 1.1s ease-in-out infinite alternate",
            }}
          />
        </div>
        <span className="absolute top-2.5 left-2.5 font-mono text-[9px] font-bold bg-zinc-900 text-white px-1.5 py-1 rounded">
          AI · ANALYZING
        </span>
        <style>{`@keyframes boScan { 0%{top:4%} 100%{top:96%} }`}</style>
      </div>

      <div className="text-center">
        <p className="text-[17px] font-bold">Reading your plate…</p>
        <p className="font-mono text-[12px] text-zinc-500 mt-2.5 h-5">{steps[step]}…</p>
      </div>

      {/* Step dots */}
      <div className="flex gap-1.5">
        {steps.map((_, i) => (
          <div
            key={i}
            className="h-1.5 rounded-full bg-zinc-300 transition-all duration-300"
            style={{
              width: i === step ? 22 : 6,
              background: i <= step ? "#1d1c1a" : "#d1d0cc",
            }}
          />
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Analysis screen — review & confirm
// ---------------------------------------------------------------------------

function AnalysisScreen({
  result,
  previewUrl,
  items,
  mealType,
  confirming,
  onRetake,
  onItemsChange,
  onMealTypeChange,
  onConfirm,
  onBack,
}: {
  result: AnalyzeResponse;
  previewUrl: string | null;
  items: DetectedItem[];
  mealType: MealType;
  confirming: boolean;
  onRetake: () => void;
  onItemsChange: (items: DetectedItem[]) => void;
  onMealTypeChange: (t: MealType) => void;
  onConfirm: () => void;
  onBack: () => void;
}) {
  const totals = items.reduce(
    (acc, it) => ({
      kcal: acc.kcal + it.calories,
      p: acc.p + it.protein_g,
      c: acc.c + it.carbs_g,
      f: acc.f + it.fat_g,
    }),
    { kcal: 0, p: 0, c: 0, f: 0 }
  );

  function removeItem(idx: number) {
    onItemsChange(items.filter((_, i) => i !== idx));
  }

  return (
    <div className="flex flex-col min-h-screen bg-zinc-50">
      {/* Top bar */}
      <div className="flex items-center gap-3 px-4 pt-4 pb-2 bg-zinc-50">
        <button onClick={onBack} className="p-1">
          <ChevronLeft size={22} className="text-zinc-700" />
        </button>
        <div className="flex-1">
          <p className="text-[16px] font-bold leading-tight">Review meal</p>
          <p className="font-mono text-[10.5px] text-zinc-400">AI detected · tap to edit</p>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto px-4 pb-36 flex flex-col gap-3">
        {/* Photo */}
        <div className="relative rounded-2xl overflow-hidden">
          {previewUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={previewUrl}
              alt="Meal"
              className="w-full object-cover"
              style={{ height: 150 }}
            />
          ) : (
            <div
              className="w-full rounded-2xl bg-zinc-200 flex items-center justify-center"
              style={{ height: 150 }}
            >
              <Camera size={28} className="text-zinc-400" />
            </div>
          )}
          <span className="absolute top-2.5 left-2.5 font-mono text-[9.5px] font-bold bg-zinc-900 text-white px-2 py-1 rounded flex items-center gap-1">
            ✦ {items.length} items found
          </span>
          <button
            onClick={onRetake}
            className="absolute bottom-2.5 right-2.5 h-[30px] px-2.5 rounded-full bg-white/90 border border-zinc-200 font-mono text-[10.5px] font-bold flex items-center gap-1.5"
          >
            <Camera size={13} /> Retake
          </button>
        </div>

        {/* Totals card */}
        <div className="bg-white rounded-2xl border border-zinc-100 shadow-sm p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-[15px] font-bold">{result.title}</p>
              <div className="flex items-center gap-1.5 mt-1">
                <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase">
                  Overall confidence
                </p>
                <ConfidenceBadge level={result.confidence} />
              </div>
            </div>
            <div className="text-right">
              <p className="font-mono text-[24px] font-bold">{Math.round(totals.kcal)}</p>
              <p className="font-mono text-[10px] text-zinc-400">kcal total</p>
            </div>
          </div>
          <div className="flex gap-2 mt-3">
            {(
              [
                ["P", totals.p],
                ["C", totals.c],
                ["F", totals.f],
              ] as [string, number][]
            ).map(([l, v]) => (
              <div
                key={l}
                className="flex-1 bg-zinc-50 border border-zinc-200 rounded-lg px-2 py-2 text-center"
              >
                <p className="font-mono text-[16px] font-bold">{Math.round(v)}g</p>
                <p className="font-mono text-[9px] text-zinc-400">
                  {l === "P" ? "PROTEIN" : l === "C" ? "CARBS" : "FAT"}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Items */}
        <p className="font-mono text-[10.5px] font-semibold tracking-widest text-zinc-400 uppercase pl-1">
          Detected items · tap to adjust
        </p>
        <div className="flex flex-col gap-2">
          {items.map((it, i) => (
            <div
              key={i}
              className={`bg-white rounded-xl border p-3 ${
                it.confidence === "low" ? "border-zinc-300" : "border-zinc-200"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-[13.5px] font-semibold">{it.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="font-mono text-[11px] text-zinc-500">{it.quantity}</span>
                    <span className="font-mono text-[11px] text-zinc-400">
                      · {it.calories} kcal · P{Math.round(it.protein_g)}
                    </span>
                  </div>
                  {it.confidence === "low" && (
                    <div className="mt-1.5 flex items-center gap-1.5 bg-zinc-50 px-2 py-1 rounded text-[10px] font-mono text-zinc-500 inline-flex">
                      <Info size={12} />
                      Low confidence — confirm portion
                    </div>
                  )}
                </div>
                <div className="flex flex-col items-end gap-2 shrink-0 ml-2">
                  <ConfidenceBadge level={it.confidence} />
                  <button
                    onClick={() => removeItem(i)}
                    className="w-[26px] h-[26px] rounded-lg border border-zinc-200 bg-white flex items-center justify-center"
                  >
                    <X size={13} className="text-zinc-400" />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {/* Add item button */}
          <button className="h-11 rounded-xl border-2 border-dashed border-zinc-200 bg-transparent text-[13.5px] font-semibold text-zinc-500 flex items-center justify-center gap-2">
            <Plus size={16} />
            Add an item
          </button>
        </div>
      </div>

      {/* Sticky confirm bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-zinc-200 px-4 pt-3 pb-5 flex gap-2.5 md:relative md:bottom-auto md:border-none">
        <select
          value={mealType}
          onChange={(e) => onMealTypeChange(e.target.value as MealType)}
          className="h-12 rounded-xl border border-zinc-200 bg-white font-mono text-[12.5px] font-semibold px-3 text-zinc-800"
        >
          <option>Breakfast</option>
          <option>Lunch</option>
          <option>Dinner</option>
          <option>Snack</option>
        </select>
        <button
          onClick={onConfirm}
          disabled={confirming || items.length === 0}
          className="flex-1 h-12 btn-primary rounded-xl flex items-center justify-center gap-2 text-[16px]"
        >
          {confirming ? (
            <span className="font-mono text-[12px]">Saving…</span>
          ) : (
            <>
              <Check size={18} />
              Confirm &amp; log
            </>
          )}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Shared sub-components
// ---------------------------------------------------------------------------

function ProgressBar({ value, className = "" }: { value: number; className?: string }) {
  const pct = Math.min(100, Math.max(0, value));
  return (
    <div className={`h-1.5 w-full rounded-full bg-zinc-100 overflow-hidden ${className}`}>
      <div
        className="h-full rounded-full bg-zinc-900 transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

function ConfidenceBadge({ level }: { level: Confidence }) {
  const map: Record<Confidence, { label: string; class: string }> = {
    high: { label: "High", class: "bg-zinc-900 text-white" },
    med: { label: "Med", class: "bg-zinc-200 text-zinc-700" },
    low: { label: "Low", class: "bg-zinc-100 text-zinc-500" },
  };
  const { label, class: cls } = map[level];
  return (
    <span className={`font-mono text-[9px] font-bold px-1.5 py-0.5 rounded ${cls}`}>
      {label}
    </span>
  );
}
