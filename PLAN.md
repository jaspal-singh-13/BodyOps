# BodyOps — Implementation Plan

> Generated: 2026-06-07
> Status: Active
> Stack: Next.js 14 (UI shell) · FastAPI + Pydantic AI (backend) · TypeScript · Tailwind · Shadcn UI · Google Sheets API · Google Drive API · Azure OpenAI · Vercel + Hugging Face Spaces

---

## PRD Review: What is Missing or Underspecified

The following gaps should be resolved before or during implementation. They are not blockers to starting but will cause rework if left undefined too long.

### Critical Gaps

| # | Gap | Risk |
|---|-----|------|
| 1 | **Calorie / macro targets not defined** — no formula for TDEE, deficit size, or protein target (e.g., 1.8 g/kg) | Coaching logic has no ground truth |
| 2 | **Timezone handling absent** — daily missions, reminders, and weight logging are date-sensitive; midnight rollover must be scoped | Wrong day logged, missions reset at wrong time |
| 3 | **Auth mechanism unspecified** — "simple single-user auth" is vague; needs a concrete approach (NextAuth magic-link, hardcoded secret, or token) | Security hole or blocked on setup |
| 4 | **Google Sheets bootstrap process missing** — no spreadsheet ID strategy, service-account setup steps, or initial sheet creation logic | First-run experience is broken |
| 5 | **Telegram bot config missing** — webhook vs polling, bot token storage, how reminders trigger | Reminders cannot be built without this |
| 6 | **Agent conversation state not defined** — is chat history persisted? Where? Per-session or full history? | Agent loses context between messages |
| 7 | **Onboarding flow absent** — user needs to set goal weight, calorie target, start date, protein target, and workout schedule before anything works | App is unusable on first load |

### Important Gaps

| # | Gap | Risk |
|---|-----|------|
| 8 | **Unit preference (kg vs lbs)** not in Settings data model | Confusing for future users; metric locked in |
| 9 | **Image size / compression policy** missing — no limit on Drive uploads | Storage costs grow unbounded |
| 10 | **OpenAI cost guardrails** absent — no daily call cap or caching strategy for coaching | Unexpected API bills |
| 11 | **Error states in UI** not specified — empty states are defined but not API failure, timeout, or parse error states | Confusing UX on failure |
| 12 | **Progressive overload formula** is only illustrated, not fully defined — what happens on first log? What if the user fails reps? | Wrong suggestions |
| 13 | **Workout session continuity** — no spec for interrupted sessions (user closes app mid-workout) | Lost data |
| 14 | **PWA manifest / service worker** scope not defined — offline behavior unknown | Broken install experience |
| 15 | **Data export / backup** not mentioned | User can't recover if Sheets is corrupted |

### Minor Gaps

- No loading state design (skeleton screens, spinners)
- No spec for how Today's Workout is determined when schedule has gaps (user skipped a day)
- No max rep/set/weight validation boundaries defined
- Multi-device behavior not specified (two phones logging simultaneously)

---

## Architecture Decisions (Locked for V1)

### Service Split

```
┌─────────────────────────────┐        ┌──────────────────────────────────┐
│  Next.js (Vercel)           │  HTTP  │  FastAPI (HF Spaces)             │
│  - UI shell only            │◄──────►│  - All API routes                │
│  - Pages + components       │        │  - Pydantic AI agent + tools     │
│  - Tailwind + Shadcn UI     │        │  - Google Sheets / Drive access  │
│  - Fetches FastAPI directly │        │  - OpenAI calls                  │
│  - Stores JWT in httpOnly   │        │  - JWT auth (issues tokens)      │
│    cookie                   │        │  - Chat history management       │
└─────────────────────────────┘        └──────────────────────────────────┘
```

- **Frontend**: Next.js 14 App Router, TypeScript, Tailwind, Shadcn UI — thin UI shell only, no API routes, no server actions for data
- **Backend**: FastAPI (Python 3.12) — all business logic, data access, agent
- **Agent**: Pydantic AI with OpenAI `gpt-4o` — tool-calling agent, typed tool inputs/outputs via Pydantic models
- **Auth**: FastAPI issues JWT (python-jose). Login endpoint reads plain-text credentials from Auth Sheet. Next.js stores JWT in httpOnly cookie, sends it on every API request. No NextAuth.
- **Storage**: 3 Google Spreadsheets (see below)
- **AI**: Azure OpenAI `gpt-4o` deployment for meal vision + coaching, accessed via Pydantic AI using the `AzureOpenAIModel`
- **Notifications**: Browser Notification API only
- **Hosting**: Vercel (Next.js) + Hugging Face Spaces (FastAPI — free Docker hosting, sleeps after 48h inactivity)
- **Timezone**: Dates stored as `YYYY-MM-DD` strings. Client sends `X-Timezone` header; FastAPI uses `zoneinfo` to resolve "today".
- **Chat history**: In-memory in FastAPI process during session, flushed to Chat History Sheet on session end / 30 min idle. `DELETE /agent/history` resets both.

### Google Spreadsheet Layout (3 sheets total)

| Sheet | Shared With | Purpose |
|-------|-------------|---------|
| **Main Data Sheet** | Service account | All app tables: WeightLogs, Meals, MealItems, WorkoutPrograms, WorkoutSchedules, WorkoutSessions, WorkoutSets, Tasks, DailyTaskStatus, CoachInsights, Settings |
| **Auth Sheet** | Owner only (not service account) | Single row: `email`, `password` (plain text). Owner edits in Google Sheets UI. |
| **Chat History Sheet** | Service account | Columns: `session_id`, `date`, `role`, `content`, `tool_calls_json` |

---

## Phase Overview

```
Phase 0 — Project Setup & Infrastructure        (Day 0)
Phase 1 — Onboarding + Auth + Shell             (Day 1, morning)
Phase 2 — Weight Tracking                       (Day 1, morning)
Phase 3 — Workout System                        (Day 1, afternoon)
Phase 4 — Meal Tracking + AI Vision             (Day 2, morning)
Phase 5 — Daily Missions + Reminders            (Day 2, morning)
Phase 6 — AI Coach + Progress Analytics         (Day 2, afternoon)
Phase 7 — PWA Polish + Deployment               (Day 2, afternoon)
```

---

## Phase 0 — Project Setup & Infrastructure

### Goal
Runnable Next.js app with Google Sheets connected, environment wired, and CI/CD configured.

### TODOs

**Frontend (Next.js)**
- [ ] `npx create-next-app@latest frontend --typescript --tailwind --app --src-dir`
- [ ] Install frontend dependencies: `shadcn/ui`, `zod`, `date-fns`, `recharts`, `next-pwa`
- [ ] Create `frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Write `frontend/lib/api.ts` — typed fetch wrapper that attaches JWT from cookie to every request, handles 401 redirect to `/login`

**Backend (FastAPI)**
- [ ] Init Python project: `pyproject.toml` already exists — add dependencies (see list below)
- [ ] Create project structure:
  ```
  api/
    main.py          # FastAPI app, CORS, router registration
    auth.py          # /auth/login, JWT issue/verify
    routers/         # weight.py, meals.py, workouts.py, tasks.py, coach.py, settings.py, agent.py
    services/        # business logic (weight_service.py, meal_service.py, etc.)
    sheets/          # sheets_client.py, sheets_repo.py, auth_sheet.py
    agent/           # pydantic_agent.py, tools.py
    models/          # pydantic request/response models
  scripts/
    setup.py         # sheet bootstrap service
  ```
- [ ] Install Python dependencies (add to `pyproject.toml`):
  ```
  fastapi, uvicorn, pydantic-ai[openai], python-jose[cryptography], gspread,
  google-auth, google-api-python-client, openai, python-multipart,
  httpx, pytest, pytest-asyncio
  ```
  Note: `zoneinfo` is stdlib in Python 3.9+, no install needed
- [ ] Write `api/sheets/sheets_client.py` — `gspread` service account client (singleton)
- [ ] Write `api/sheets/sheets_repo.py` — `read_rows`, `append_row`, `update_row`, `find_row` using gspread
- [ ] Write `api/sheets/auth_sheet.py` — reads Auth Sheet via separate Google Sheets API call using owner's API key (not service account)
- [ ] Write `api/auth.py` — `POST /auth/login`: read from Auth Sheet, compare password, return JWT
- [ ] Write `api/main.py` — FastAPI app with CORS configured for Vercel frontend domain

**Google Sheets Setup**
- [ ] Create Google Cloud project, enable Sheets API + Drive API
- [ ] Create service account, download JSON credentials
- [ ] Create 3 Google Spreadsheets manually; record IDs in env
- [ ] Share **Main Data Sheet** and **Chat History Sheet** with service account email
- [ ] Share **Auth Sheet** with owner only — NOT the service account
- [ ] Manually enter `email` and `password` in row 2 of Auth Sheet (row 1 = headers)

### Setup Service (`python scripts/setup.py` / `make setup`)

Run once after cloning. Idempotent — safe to run multiple times.

What it does:
1. Validates all required env vars, prints missing ones and exits code 1 if any absent
2. Connects to Main Data Sheet via service account
3. Creates any missing tabs with correct header rows (does not modify existing tabs)
4. Connects to Chat History Sheet, creates `ChatHistory` tab with headers if missing
5. Prints checklist: ✓ exists / ✓ created / ✗ failed per tab
6. Auth Sheet is NOT touched — owner manages it manually

Tabs created in Main Data Sheet:
`WeightLogs`, `Meals`, `MealItems`, `WorkoutPrograms`, `WorkoutSchedules`, `WorkoutSessions`, `WorkoutSets`, `Tasks`, `DailyTaskStatus`, `CoachInsights`, `Settings`

### Required Environment Variables

**Backend (`api/.env`)**
```env
GOOGLE_SERVICE_ACCOUNT_JSON=    # full JSON as string, or path to file
GOOGLE_SPREADSHEET_ID=          # Main Data Sheet
GOOGLE_CHAT_HISTORY_SHEET_ID=   # Chat History Sheet
GOOGLE_AUTH_SHEET_ID=           # Auth Sheet ID (read via Sheets API v4 with API key)
GOOGLE_SHEETS_API_KEY=          # for reading Auth Sheet without service account
GOOGLE_DRIVE_FOLDER_ID=         # Drive folder for meal images
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=          # https://<your-resource>.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=        # your gpt-4o deployment name
AZURE_OPENAI_API_VERSION=2024-08-01-preview
JWT_SECRET=
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080         # 7 days
```

**Frontend (`frontend/.env.local`)**
```env
NEXT_PUBLIC_API_URL=https://<username>-bodyops-api.hf.space
```

### Acceptance Criteria

- [ ] `uvicorn api.main:app --reload` starts without errors
- [ ] `npm run dev` (frontend) starts without errors and proxies API calls correctly
- [ ] `python scripts/setup.py` creates all missing tabs and exits with code 0
- [ ] `python scripts/setup.py` run a second time makes no changes and still exits code 0
- [ ] `GET /health` returns `{ "ok": true, "sheets": true, "drive": true }`
- [ ] Write `api/Dockerfile` — python:3.12-slim base, expose port 7860, health check on `/health`
- [ ] Write `api/README.md` with HF Spaces config frontmatter (`sdk: docker`, `app_port: 7860`)
- [ ] `git subtree push --prefix=api hf main` succeeds and app is reachable at `https://<username>-bodyops-api.hf.space`
- [ ] Vercel deployment of Next.js is live and `NEXT_PUBLIC_API_URL` points to HF Spaces URL

---

## Phase 1 — Onboarding + Auth + Shell

### Goal
User can sign in. First-time users complete onboarding to set their profile. App shell (sidebar + bottom nav) renders.

### TODOs

**Auth (FastAPI)**
- [ ] `POST /auth/login` — read credentials from Auth Sheet, compare plain-text password, return `{ access_token, token_type: "bearer" }`
- [ ] `api/auth.py` — `create_jwt(email)`, `verify_jwt(token)` using `python-jose`
- [ ] FastAPI dependency `get_current_user` — extract + verify JWT from `Authorization: Bearer` header, used on all protected routes
- [ ] Note: no sign-up, no password reset endpoint — owner changes password directly in Auth Sheet

**Auth (Next.js)**
- [ ] Build `/login` page: email + password form, calls `POST /auth/login` on FastAPI, stores returned JWT in httpOnly cookie
- [ ] Next.js middleware: check for JWT cookie on all `/app/*` routes, redirect to `/login` if absent
- [ ] `frontend/lib/api.ts` — fetch wrapper that reads JWT from cookie and sets `Authorization` header on every request

**Onboarding**
- [ ] Build `/onboarding` multi-step form (redirect here after first login if `Settings` tab in Main Data Sheet has no row):
  - Step 1: Name, current weight (kg), height (cm), age, goal weight (kg), start date
  - Step 2: Auto-calculate calorie target (Mifflin-St Jeor BMR × 1.55 activity − 500 kcal deficit) and protein target (`body_weight_kg × 1.8 g`) — show values, let user override
  - Step 3: Preferred wake-up time (used for daily mission generation timing)
- [ ] `POST /api/settings` — save onboarding data to `Settings` tab
- [ ] `GET /api/settings` — load current settings row

**App Shell**
- [ ] Build mobile shell: bottom nav with icons — Home, Meals, Workouts, Progress, Coach
- [ ] Build desktop shell: persistent left sidebar with same items
- [ ] Active route highlighting
- [ ] User avatar / sign out in header

### Acceptance Criteria

- [ ] Unauthenticated access to `/app/*` redirects to `/login`
- [ ] Successful login redirects to `/app` (dashboard)
- [ ] First login with empty settings redirects to `/onboarding`
- [ ] Completing onboarding saves all fields to Settings sheet and redirects to dashboard
- [ ] Nav renders correctly on mobile (bottom) and desktop (sidebar)
- [ ] Sign out clears session and redirects to `/login`

---

## Phase 2 — Weight Tracking

### Goal
User can log daily weight, view history, and see their trend.

### TODOs

**API**
- [ ] `POST /api/weight` — validate body `{ date, weight_kg }`, append to `WeightLogs` sheet, return saved record
- [ ] `GET /api/weight/history` — return last 90 days of entries sorted descending
- [ ] `GET /api/weight/trend` — compute 7-day moving average, total loss, projected goal date (linear regression on last 14 days)

**UI — Weight Page (`/app/weight`)**
- [ ] Weight log form: date picker (default today), numeric weight input, submit button
- [ ] Show today's entry if already logged (edit mode vs add mode)
- [ ] Weight history list: date, weight, change from previous
- [ ] 30-day line chart (Recharts): raw weight + 7-day moving average overlay
- [ ] Stats row: current, goal, remaining, projected date
- [ ] Empty state: "Log your first weight to start tracking your trend"

**Dashboard integration**
- [ ] Dashboard shows current weight, goal weight, weight remaining
- [ ] Dashboard shows projected goal date

### Acceptance Criteria

- [ ] Logging weight appends a row to `WeightLogs` sheet
- [ ] Logging the same date twice updates (not duplicates) the existing entry
- [ ] History shows entries sorted newest first
- [ ] Chart renders 7-day moving average correctly
- [ ] Projected date uses linear regression on last 14 weigh-ins (or all entries if fewer than 14)
- [ ] Empty state renders when no entries exist

---

## Phase 3 — Workout System

### Goal
User can import a workout plan by pasting text, see today's workout, log sets, and get progressive overload suggestions.

### TODOs

**Workout Import Parser (`lib/workout-parser.ts`)**
- [ ] Parse day headers: `Push:`, `Pull:`, `Legs:`, `Upper:`, `Lower:`, `Rest`
- [ ] Parse exercise lines: `Exercise Name NxM-P` (sets × rep range)
- [ ] Detect and flag invalid lines with line number
- [ ] Return structured `WorkoutDay[]` or `ValidationError[]`
- [ ] Write unit tests for: valid PPL, Upper/Lower, rest days, invalid format, partial valid

**Workout Schedule Parser (`lib/schedule-parser.ts`)**
- [ ] Parse `Mon - Push`, `Tue - Rest`, etc. into weekday→workout-day mapping
- [ ] Fall back to auto-assign cycle if no schedule is given (Day 1, Day 2, Day 3… in order)

**API**
- [ ] `POST /api/workouts/import` — runs parser, validates, writes to `WorkoutPrograms` and `WorkoutSchedules` sheets, returns confirmation summary
- [ ] `GET /api/workouts/today` — determines today's workout day from schedule + current date, returns exercises with previous bests and suggested targets
- [ ] `POST /api/workouts/log` — saves a set to `WorkoutSets`, updates session in `WorkoutSessions`
- [ ] `GET /api/workouts/progression` — returns last 5 sessions per exercise with trend
- [ ] `GET /api/workouts/history` — returns past sessions list

**Progressive Overload Logic (`lib/progression.ts`)**
- [ ] If last set hit upper rep range: suggest +2.5 kg same reps
- [ ] If last set hit middle of range: suggest same weight +1 rep
- [ ] If last set was below lower range: suggest -2.5 kg
- [ ] No prior data: return `null` suggestion (show "first session" state)

**Agent — Workout Import (`/api/agent/import-workout`)**
- [ ] Accept natural-language paste
- [ ] Call parser, return structured confirmation
- [ ] If parser fails, return specific lines that failed with guidance

**UI — Workouts Page (`/app/workouts`)**
- [ ] Import tab: textarea for pasting plan + schedule, submit, show confirmation card
- [ ] Today tab: show today's day name, exercise list, sets/reps target, suggested weight
- [ ] Log tab: for each exercise, add set rows (weight, reps), mark complete
- [ ] History tab: past sessions list, tap to expand set details
- [ ] Empty state: "Paste your workout plan to get started"

### Acceptance Criteria

- [ ] Parser correctly handles PPL format with rest days
- [ ] Parser returns line-level error for invalid input
- [ ] Import writes correct rows to `WorkoutPrograms` sheet (one row per exercise)
- [ ] `GET /api/workouts/today` returns correct day based on weekday schedule
- [ ] On rest day, returns `{ rest: true }`
- [ ] Logging a set persists to `WorkoutSets` sheet
- [ ] Progressive overload suggestion is correct for hit/miss/new scenarios
- [ ] Confirmation card shows: program name, workout days count, rest days count, total exercises

---

## Phase 4 — Meal Tracking + AI Vision

### Goal
User can photograph a meal, get AI-estimated calories and macros, confirm, and save. Daily nutrition totals update.

### TODOs

**Meal Vision Service (`lib/meal-vision.ts`)**
- [ ] Accept base64 image or URL
- [ ] Call `gpt-4o` vision with structured prompt requesting JSON: `{ items: [{ name, quantity, unit, calories, protein_g, carbs_g, fat_g }], total: { calories, protein_g, carbs_g, fat_g } }`
- [ ] Validate response shape with Zod
- [ ] Return parsed result or throw structured error

**Drive Upload (`lib/drive.ts`)**
- [ ] `uploadMealImage(base64, mimeType)` — upload to Drive folder, return public URL
- [ ] Set file permission to public read so URL works without auth

**API**
- [ ] `POST /api/meals/analyze` — accept multipart form with image, upload to Drive, call vision, return analysis + drive URL (do NOT save yet — wait for confirm)
- [ ] `POST /api/meals` — accept confirmed meal payload, save to `Meals` + `MealItems` sheets
- [ ] `GET /api/meals/today` — return all meals for today with totals
- [ ] `GET /api/meals/history` — return meal list for last 30 days

**UI — Meals Page (`/app/meals`)**
- [ ] Camera button: triggers file input (accept image/*, capture=camera on mobile)
- [ ] After capture: show preview + spinner while analyzing
- [ ] Analysis result: food item list with editable calories/macros per item
- [ ] Confirm / Edit / Retake actions
- [ ] Meal type selector: Breakfast, Lunch, Dinner, Snack
- [ ] Today's meals list: meal cards with photo thumbnail, type, total cals/protein
- [ ] Daily summary bar: consumed / target for calories and protein
- [ ] Empty state: "Tap the camera to log your first meal"

**Dashboard integration**
- [ ] Calories consumed today
- [ ] Protein consumed today
- [ ] Remaining calories

### Acceptance Criteria

- [ ] Image upload stores file in Google Drive and returns a working URL
- [ ] Vision API returns parseable JSON with all required fields
- [ ] Zod validation rejects malformed OpenAI responses
- [ ] Confirmed meal saves one row to `Meals` and N rows to `MealItems`
- [ ] `GET /api/meals/today` correctly sums all meals logged today
- [ ] Editing a meal item before confirming updates totals in real time
- [ ] Calories and protein appear on dashboard after logging

---

## Phase 5 — Daily Missions + Reminders

### Goal
User sees a daily checklist. System sends browser notifications as reminders.

### TODOs

**Daily Mission Engine (`lib/missions.ts`)**
- [ ] `generateDailyTasks(date, settings)` — produce task list based on current settings:
  - Log weight (daily)
  - Hit protein target
  - Stay under calorie target
  - Complete workout (only on workout days per schedule)
  - Drink water (if enabled in settings)
- [ ] Store generated tasks in `DailyTaskStatus` tab (one row per task per day)
- [ ] Idempotent — calling twice for same date does not duplicate rows

**API**
- [ ] `GET /api/tasks/today` — return today's task list with completion status
- [ ] `POST /api/tasks/complete` — mark task as complete, timestamp completion
- [ ] `GET /api/tasks/status` — summary: total, completed, percentage

**Auto-completion hooks**
- [ ] Mark "Log weight" complete when `POST /api/weight` succeeds for today
- [ ] Mark "Hit protein target" complete when daily protein ≥ target (check on every `POST /api/meals`)
- [ ] Mark "Complete workout" complete when workout session is finished for today

**Reminders (browser-only)**
- [ ] `POST /api/reminders` — save reminder config (type, time, enabled) to `Settings` tab (not a separate table — store as JSON field in Settings row)
- [ ] `GET /api/reminders` — return reminder config from Settings
- [ ] Browser push: register service worker, request notification permission on first app load, schedule local notifications via `Notification API`
- [ ] Vercel Cron: `GET /api/cron/reminders` — run daily, returns a JSON payload; client-side service worker schedules the actual browser notifications based on this

**UI — Settings: Reminders section**
- [ ] List of toggleable reminders with time pickers: Morning weigh-in, Meal logging, Workout, End-of-day check-in
- [ ] "Enable Notifications" button — triggers browser permission prompt
- [ ] Shows current permission status (granted / denied / not asked)

**Dashboard integration**
- [ ] Mission progress ring: X of Y complete
- [ ] Task checklist widget (collapsed by default, expandable)

### Acceptance Criteria

- [ ] `generateDailyTasks` called twice for the same date produces the same rows (idempotent)
- [ ] Logging weight auto-marks the "Log weight" mission complete
- [ ] Reaching protein target auto-marks "Hit protein target" complete
- [ ] Completing all missions shows 100% on dashboard
- [ ] Browser notification fires at configured time (requires granted permission)
- [ ] Reminder settings persist across page reloads

---

## Phase 6 — AI Coach + Progress Analytics

### Goal
User sees a daily coaching summary and progress charts across all tracked metrics.

### TODOs

**Coaching Engine (`lib/coach.ts`)**
- [ ] `generateDailyCoaching(date)`:
  - Gather: today's weight vs trend, calories consumed, protein consumed, workout completed, missions done
  - Build system prompt with user context (goal, start weight, current weight, deficit target)
  - Call `gpt-4o` with structured output: `{ summary: string, wins: string[], focus: string[], next_step: string }`
  - Save to `CoachInsights` sheet
  - Cache: if insight for today already exists in sheet, return it without re-calling OpenAI
- [ ] `generateWeeklyReview(weekStartDate)` — same pattern but 7-day window

**API**
- [ ] `GET /api/coach/daily` — return today's coaching (generate if not cached)
- [ ] `GET /api/coach/weekly` — return this week's review

**Progress Analytics**
- [ ] `GET /api/progress/summary` — return: weight trend, calorie avg (7d), protein avg (7d), workout sessions (30d), mission completion rate (30d), projected goal date

**UI — Coach Page (`/app/coach`)**
- [ ] Daily summary card: wins list, focus list, next step
- [ ] Weekly review card (collapsible)
- [ ] Refresh button (re-generates coaching, with rate limit: max once per hour)

**UI — Progress Page (`/app/progress`)**
- [ ] Weight chart: 30-day line with 7-day MA
- [ ] Calorie chart: 7-day bar
- [ ] Protein chart: 7-day bar (with target line)
- [ ] Workout consistency: calendar heatmap (last 30 days)
- [ ] Mission completion: % bar last 7 days
- [ ] Goal projection: current pace vs target date

### Acceptance Criteria

- [ ] Daily coaching only calls OpenAI once per day (second request reads from sheet)
- [ ] Weekly review covers Mon–Sun of current week
- [ ] Progress charts render with correct data
- [ ] Empty coach state shows "Complete some missions to unlock your first coaching summary"
- [ ] Refresh rate limit: returns cached result if last generate was under 1 hour ago

---

## Phase 7 — PWA Polish + Deployment

### Goal
App is installable, fast, and production-ready.

### TODOs

**PWA**
- [ ] Add `manifest.json`: name, icons, theme_color, background_color, display=standalone
- [ ] Register service worker for offline shell caching (app shell only — data stays online)
- [ ] Add `Add to Home Screen` prompt on mobile

**Performance**
- [ ] Verify all API routes respond under 2s (Sheets API can be slow — add caching with `unstable_cache`)
- [ ] Add loading skeletons to dashboard, meals, workouts pages
- [ ] Add error boundary components for API failures

**Security**
- [ ] Audit all API routes: confirm auth check on every route
- [ ] Confirm service account key is never exposed to client
- [ ] Confirm Drive image URLs are public read only (no write)
- [ ] Confirm OpenAI key is server-only

**Final QA Checklist**
- [ ] Log weight → appears on dashboard and weight page
- [ ] Import workout → shows correct today workout
- [ ] Log meal photo → analysis works, confirm saves, daily totals update
- [ ] Missions auto-complete when triggered
- [ ] Browser notification fires at configured time
- [ ] Coach summary generates without error
- [ ] All charts render on progress page
- [ ] Install app on phone, test camera meal log end-to-end

### Acceptance Criteria

- [ ] Lighthouse PWA score ≥ 80
- [ ] App installs on Android Chrome and iOS Safari
- [ ] No API route accessible without authentication
- [ ] Vercel deployment passes with zero build errors
- [ ] All acceptance criteria from Phases 1–6 still pass

---

## Agent Chat Feature (Cross-Phase)

The `POST /agent/chat` endpoint and `/app/coach` chat UI are built incrementally as tools are added per phase.

| Phase | Tools Added |
|-------|-------------|
| Phase 2 | `log_weight`, `get_weight_trend` |
| Phase 3 | `get_today_workout`, `log_workout_set`, `get_progression_target` |
| Phase 4 | `analyze_meal_photo`, `save_meal`, `get_daily_nutrition` |
| Phase 5 | `get_task_status`, `complete_task` |
| Phase 6 | `generate_daily_coaching`, `generate_weekly_review` |

### Pydantic AI Implementation Pattern

```python
# api/agent/pydantic_agent.py
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncAzureOpenAI
import os

azure_client = AsyncAzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

model = OpenAIModel(
    os.environ["AZURE_OPENAI_DEPLOYMENT"],
    openai_client=azure_client,
)

agent = Agent(
    model,
    system_prompt="You are BodyOps coach...",
)
# tools are registered with @agent.tool decorator in tools.py
```

Each tool is a plain Python async function decorated with `@agent.tool` and typed with Pydantic models:

```python
from pydantic_ai import RunContext
from pydantic import BaseModel

class LogWeightInput(BaseModel):
    date: str       # YYYY-MM-DD
    weight_kg: float

@agent.tool
async def log_weight(ctx: RunContext, input: LogWeightInput) -> dict:
    return await weight_service.log(input.date, input.weight_kg)
```

### Chat History

- In-memory: `Dict[str, list[ModelMessage]]` keyed by `session_id` in FastAPI process memory
- Flush to Sheet: on session end or 30 min idle (background task via `asyncio`)
- New session start: load last 20 messages from Chat History Sheet as seed
- Reset: `DELETE /agent/history` — clears in-memory dict AND wipes all rows from Chat History Sheet tab

### Endpoint

```
POST /agent/chat
Body: { message: str, session_id: str }
Response: { reply: str, tool_calls: [...] }  (streaming optional in v2)
```

---

## Testing Strategy

Every feature implementation must include tests. See `.claude/CLAUDE.md` for the rule.

### Test Types by Layer

| Layer | Tool | What to Test |
|-------|------|-------------|
| Parsers (`api/services/`) | pytest | Valid input, invalid input, edge cases |
| API Routes (`api/routers/`) | pytest + `httpx.AsyncClient` (FastAPI test client) | Response shape, auth check (missing/expired JWT), error states |
| Services (`api/services/`) | pytest with mocked gspread + OpenAI | Business logic, data transformation |
| Agent tools (`api/agent/tools.py`) | pytest with mocked services | Tool input validation, correct service calls |
| UI | Playwright | Critical flows: login, meal log, workout log |

### Required Test Files Per Phase

- Phase 0: `tests/test_sheets_repo.py`
- Phase 1: `tests/test_auth.py`, `tests/test_settings.py`
- Phase 2: `tests/test_weight_router.py`, `tests/test_weight_service.py`
- Phase 3: `tests/test_workout_parser.py`, `tests/test_progression.py`, `tests/test_workout_router.py`
- Phase 4: `tests/test_meal_vision.py`, `tests/test_meal_router.py`
- Phase 5: `tests/test_missions.py`, `tests/test_tasks_router.py`
- Phase 6: `tests/test_coach.py`, `tests/test_agent_tools.py`
