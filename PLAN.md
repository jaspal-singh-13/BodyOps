# BodyOps — Implementation Plan

> Generated: 2026-06-07
> Status: Active
> Stack: Next.js 14+ App Router · TypeScript · Tailwind · Shadcn UI · Google Sheets API · Google Drive API · OpenAI · Telegram Bot · Vercel

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

- **Frontend**: Next.js 14 App Router, TypeScript, Tailwind, Shadcn UI
- **Backend**: Next.js API routes (no separate server)
- **Storage**: Google Sheets (one sheet = one table), Google Drive for images
- **AI**: OpenAI `gpt-4o` for meal vision + `gpt-4o` for coaching text
- **Auth**: NextAuth.js with single hardcoded credentials (email/password) — expandable later
- **Notifications**: Telegram Bot (webhook mode) + browser Notification API
- **Hosting**: Vercel (serverless functions)
- **Timezone**: Store all dates in UTC ISO-8601, display in user's local timezone (from browser)

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

- [ ] `npx create-next-app@latest bodyops --typescript --tailwind --app --src-dir`
- [ ] Install dependencies: `shadcn/ui`, `next-auth`, `googleapis`, `openai`, `axios`, `zod`, `date-fns`, `recharts`
- [ ] Create `.env.local` with all required keys (see env var list below)
- [ ] Create Google Cloud project, enable Sheets API + Drive API, create service account, download credentials JSON
- [ ] Create Google Spreadsheet, share with service account email
- [ ] Create initial sheets (tabs): `Users`, `WeightLogs`, `Meals`, `MealItems`, `WorkoutPrograms`, `WorkoutSchedules`, `WorkoutSessions`, `WorkoutSets`, `Tasks`, `DailyTaskStatus`, `CoachInsights`, `Reminders`, `Settings`
- [ ] Write `lib/sheets.ts` — authenticated Sheets client (singleton)
- [ ] Write `lib/drive.ts` — authenticated Drive client (singleton)
- [ ] Write `lib/openai.ts` — OpenAI client (singleton)
- [ ] Write `lib/sheets-repo.ts` — generic `readRows`, `appendRow`, `updateRow`, `findRow` helpers
- [ ] Set up Telegram bot via BotFather, store token in env
- [ ] Write `lib/telegram.ts` — `sendMessage(chatId, text)` helper
- [ ] Deploy blank app to Vercel, confirm env vars are injected
- [ ] Set up Telegram webhook pointing to `/api/reminders/webhook`

### Required Environment Variables

```env
GOOGLE_SERVICE_ACCOUNT_EMAIL=
GOOGLE_PRIVATE_KEY=
GOOGLE_SPREADSHEET_ID=
OPENAI_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
NEXTAUTH_SECRET=
NEXTAUTH_URL=
AUTH_EMAIL=
AUTH_PASSWORD=
```

### Acceptance Criteria

- [ ] `npm run dev` starts without errors
- [ ] `GET /api/health` returns `{ ok: true, sheets: true, drive: true }`
- [ ] Service account can read/write a test row to a scratch sheet
- [ ] Vercel deployment is live

---

## Phase 1 — Onboarding + Auth + Shell

### Goal
User can sign in. First-time users complete onboarding to set their profile. App shell (sidebar + bottom nav) renders.

### TODOs

**Auth**
- [ ] Configure NextAuth.js with `CredentialsProvider` using `AUTH_EMAIL` / `AUTH_PASSWORD` env vars
- [ ] Protect all `/app/*` routes with middleware — redirect to `/login` if unauthenticated
- [ ] Build `/login` page: email + password form, error state, submit loading

**Onboarding**
- [ ] Build `/onboarding` multi-step form (redirect here after first login if `Settings` sheet is empty):
  - Step 1: Name, current weight, goal weight, start date
  - Step 2: Daily calorie target (or auto-calculate from weight using 500 kcal deficit), protein target (auto-suggest: `body_weight_kg * 1.8 g`)
  - Step 3: Wake-up time, workout days per week (used for reminder scheduling)
- [ ] `POST /api/settings` — save onboarding data to `Settings` sheet
- [ ] `GET /api/settings` — load current settings

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
User sees a daily checklist. System sends reminders via Telegram and browser notifications.

### TODOs

**Daily Mission Engine (`lib/missions.ts`)**
- [ ] `generateDailyTasks(date, settings)` — produce task list based on current settings:
  - Log weight (daily)
  - Hit protein target
  - Stay under calorie target
  - Complete workout (only on workout days)
  - Hit step goal (if enabled)
  - Drink water (if enabled)
  - Sleep before target time (if enabled)
- [ ] Store generated tasks in `DailyTaskStatus` sheet (one row per task per day)
- [ ] Idempotent — calling twice for same date does not duplicate

**API**
- [ ] `GET /api/tasks/today` — return today's task list with completion status
- [ ] `POST /api/tasks/complete` — mark task as complete, timestamp completion
- [ ] `GET /api/tasks/status` — summary: total, completed, percentage

**Auto-completion hooks (background)**
- [ ] Mark "Log weight" complete when weight is logged for today
- [ ] Mark "Hit protein target" complete when daily protein ≥ target
- [ ] Mark "Stay under calories" evaluated at end of day (or on demand)
- [ ] Mark "Complete workout" complete when workout session logged for today

**Reminders**
- [ ] `POST /api/reminders` — save reminder config to `Reminders` sheet
- [ ] `GET /api/reminders` — return all reminders
- [ ] Telegram webhook handler `POST /api/reminders/webhook` — handle `/start`, `/status`, incoming commands
- [ ] Vercel Cron: `GET /api/cron/reminders` — run every 15 minutes, check due reminders, send Telegram messages
- [ ] Browser push: register service worker, request notification permission on first visit, send push from server action

**UI — Settings: Reminders section**
- [ ] List of toggleable reminders with time pickers
- [ ] Telegram setup instructions (link to bot, `/start` command)
- [ ] Notification permission button

**Dashboard integration**
- [ ] Mission progress ring / bar: X of Y complete
- [ ] Task checklist widget (collapsed by default, expandable)

### Acceptance Criteria

- [ ] `generateDailyTasks` called twice for the same date produces the same task list (idempotent)
- [ ] Logging weight auto-marks the "Log weight" mission complete
- [ ] Completing all missions shows 100% on dashboard
- [ ] Vercel cron fires and sends Telegram message at scheduled time
- [ ] Browser notification fires when triggered
- [ ] Telegram `/status` command returns today's mission summary

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
- [ ] Telegram reminder fires at correct time
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

The `/api/agent/chat` endpoint and `/app/coach` chat UI are built incrementally as tools are added. Wire up tools phase by phase:

| Phase | Tools Added |
|-------|-------------|
| Phase 2 | `log_weight`, `get_weight_trend` |
| Phase 3 | `get_today_workout`, `log_workout_set`, `get_progression_target` |
| Phase 4 | `analyze_meal_photo`, `save_meal`, `get_daily_nutrition` |
| Phase 5 | `get_task_status`, `complete_task` |
| Phase 6 | `generate_daily_coaching`, `generate_weekly_review` |

Agent implementation pattern:
- Use OpenAI function calling (tool_choice: auto)
- Each tool is a TypeScript function that calls the corresponding internal service
- Agent responses must include tool call results, not just summaries
- Store conversation in session (not persisted in Sheets — session only)

---

## Testing Strategy

Every feature implementation must include tests. See `.claude/CLAUDE.md` for the rule.

### Test Types by Layer

| Layer | Tool | What to Test |
|-------|------|-------------|
| Parsers (`lib/`) | Jest | Valid input, invalid input, edge cases |
| API Routes | Jest + `node-mocks-http` or Next.js test utils | Response shape, auth check, error states |
| Services (`lib/`) | Jest with mocked Sheets/OpenAI | Business logic, data transformation |
| UI | Playwright or React Testing Library | Critical flows: login, meal log, workout log |

### Required Test Files Per Phase

- Phase 0: `lib/sheets-repo.test.ts`
- Phase 1: `app/api/auth.test.ts`, `lib/settings.test.ts`
- Phase 2: `app/api/weight.test.ts`, `lib/weight-trend.test.ts`
- Phase 3: `lib/workout-parser.test.ts`, `lib/progression.test.ts`, `app/api/workouts.test.ts`
- Phase 4: `lib/meal-vision.test.ts`, `app/api/meals.test.ts`
- Phase 5: `lib/missions.test.ts`, `app/api/tasks.test.ts`
- Phase 6: `lib/coach.test.ts`, `app/api/coach.test.ts`
