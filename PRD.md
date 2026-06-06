Below is a proper PRD in markdown for **BodyOps**. The structure follows common PRD guidance: define the purpose, features, behavior, user stories, design, out-of-scope items, and success criteria so the team has one source of truth. ([Atlassian][1])

# BodyOps PRD

## 1. Document Info

| Field         | Value                                      |
| ------------- | ------------------------------------------ |
| Product Name  | BodyOps                                    |
| Version       | V1 MVP                                     |
| Owner         | Jaspal Singh                               |
| Type          | Personal AI Fat-Loss Operating System      |
| Platforms     | Web PWA (mobile-first), desktop responsive |
| Backend       | Google Sheets + Google Drive               |
| AI            | OpenAI Vision + LLM reasoning              |
| Notifications | Telegram + browser notifications           |
| Status        | Draft                                      |

---

## 2. Product Summary

BodyOps is a personal AI-powered fat-loss system that helps the user lose weight by combining meal photo logging, weight tracking, workout tracking, daily habit missions, reminders, and coaching into one simple operating loop.

The key idea is not just to record data, but to reduce friction and guide the user day by day.

---

## 3. Problem Statement

The user wants to lose 30 kg in about 180 days, but traditional fitness apps create too much manual work and do not provide enough guidance or accountability.

Current pain points:

* Meal logging is slow.
* Workout logging is tedious.
* Weight fluctuations are hard to interpret.
* Habit tracking gets forgotten.
* Users know what to do but need daily execution support.
* Existing tools do not feel like a coach.

---

## 4. Goals

### Primary Goal

Help the user consistently execute a fat-loss plan for 180 days.

### Secondary Goals

* Make meal logging possible from a photo.
* Make workout logging extremely fast.
* Track weight and trends.
* Support progressive overload.
* Provide reminders and daily accountability.
* Give actionable daily coaching.
* Keep the system simple enough to build in 2 days.

---

## 5. Non-Goals / Out of Scope for V1

* Social/community features
* Multiple users and team management
* Native iOS/Android apps
* Wearable integrations
* Barcode scanner
* Recipe generation
* Grocery planning
* Subscription billing
* Complex nutrition database
* Multi-coach marketplace

---

## 6. Target User

### Primary User

* Working professional
* Limited time
* Wants fat loss
* Gym 5–6 days/week
* Prefers low-friction tracking
* Comfortable with AI-assisted workflows

### Example User Profile

* Weight: 107 kg
* Goal weight: 77 kg
* Daily work schedule: 2 PM to 10 PM
* Wants to wake up earlier
* Wants structure, not complexity

---

## 7. Product Principles

1. **Fast capture**

   * Log in under 10 seconds wherever possible.

2. **AI-assisted, not AI-dependent**

   * AI handles interpretation.
   * Deterministic logic handles rules and calculations.

3. **Progress over perfection**

   * Focus on trends, streaks, consistency.

4. **Mobile-first**

   * Most daily actions happen on phone.

5. **Future-proof architecture**

   * Google Sheets now.
   * Easy migration to Postgres/Supabase later.

---

## 8. Solution Overview

BodyOps has four major layers:

1. **User Interface**

   * Dashboard
   * Meals
   * Weight
   * Workouts
   * Progress
   * Coach
   * Settings

2. **Agent Layer**

   * Chat-based assistant
   * Workout import parser
   * Meal analysis
   * Daily coaching
   * Reminder triggers

3. **Service + Repository Layer**

   * Clean separation between business logic and storage

4. **Storage + AI**

   * Google Sheets for structured data
   * Google Drive for images
   * OpenAI for meal analysis and coaching
   * Telegram for reminders

---

## 9. Core User Flows

### 9.1 Meal Flow

1. User takes a photo of the meal.
2. Agent sends the image to vision model.
3. Model returns food items, calories, macros.
4. User confirms or edits the result.
5. Meal is saved to storage.
6. Daily totals update automatically.

### 9.2 Weight Flow

1. User enters morning weight.
2. System stores the entry.
3. Trend and weekly average update.
4. AI coach uses the trend later.

### 9.3 Workout Flow

1. User pastes a workout plan once.
2. Agent parses it into the permitted format.
3. System creates workout program and weekly schedule.
4. On workout day, app shows today’s routine.
5. User logs sets and reps.
6. System suggests next overload target.

### 9.4 Daily Mission Flow

1. System generates a checklist for the day.
2. User completes tasks throughout the day.
3. Completion status updates in dashboard.
4. AI coach uses completion data.

### 9.5 Coaching Flow

1. System aggregates weight, meals, workouts, and habits.
2. AI generates a daily summary.
3. User sees what happened and what to focus on next.

---

## 10. Functional Requirements

### 10.1 Authentication

* User should be able to sign in securely.
* V1 can use a simple single-user auth model.
* Future multi-user support should not break schema.

### 10.2 Dashboard

The dashboard must show:

* Current weight
* Goal weight
* Weight remaining
* Calories consumed today
* Protein consumed today
* Daily mission completion
* Workout status
* Trend summary
* AI coach summary
* Projected goal date

### 10.3 Weight Tracking

* Log daily weight.
* Edit existing entries.
* View weekly and monthly trend.
* Compute moving average.
* Show total change over time.

### 10.4 Meal Photo Logging

* Upload meal photo.
* Analyze image with AI.
* Return food list and nutrition estimate.
* Allow user confirmation/editing.
* Save final result.

### 10.5 Meal History

* View all meals logged for the day.
* View meal details.
* Edit calories/macros if needed.

### 10.6 Workout Program Import

This is the key feature for easier workout entry.

The user can paste a workout plan in chat using a simple supported format, and the agent must convert it into the internal permissible structure.

#### Supported import format

Example:

```text
Push:
Bench Press 3x6-8
Incline DB Press 3x8-10
Shoulder Press 3x8-10

Pull:
Lat Pulldown 3x8-10
Cable Row 3x8-10

Legs:
Squat 3x6-8
RDL 3x8-10

Rest
```

#### What the system must do

* Parse the pasted text.
* Identify workout days.
* Detect rest days.
* Extract exercise name, sets, and rep range.
* Validate that the format is permissible.
* Store the program in structured form.
* Map weekday schedule if provided.
* Ask for clarification only when parsing fails.

### 10.7 Weekly Workout Scheduling

* Support weekday-wise planning.
* Support repeated cycles like PPL, Upper/Lower, Push/Pull/Legs, or custom schedules.
* Support rest days.
* Show today’s workout automatically based on schedule.

### 10.8 Workout Logging

* Log exercise, weight, and reps.
* Support multiple sets.
* Support rest timer later if needed.
* Save workout session summary.

### 10.9 Progressive Overload

* Retrieve previous performance for each exercise.
* Recommend next target weight/reps.
* Keep the logic deterministic.

Example:

* Last: 60 kg × 8
* Suggested: 62.5 kg × 6+

### 10.10 Daily Missions

Generate a checklist such as:

* Log weight
* Hit protein target
* Stay under calorie target
* Complete workout
* Hit step goal
* Drink water
* Sleep before target time

### 10.11 Reminders

* Morning weight reminder
* Meal logging reminder
* Workout reminder
* Sleep reminder
* Daily mission reminder

### 10.12 AI Coach

* Generate a daily summary.
* Generate weekly review.
* Highlight what improved.
* Highlight what needs attention.
* Give one or two actionable next steps.

### 10.13 Progress Analytics

* Show weight trend.
* Show calorie trend.
* Show protein trend.
* Show workout consistency.
* Show mission completion.
* Show goal projection.

---

## 11. Agent Capabilities

The chat agent is the main interface for power actions.

### Agent must support:

* Import workout plans from pasted text
* Parse meal photos
* Log weight
* Log workouts
* Show today’s workout
* Show remaining calories/protein
* Show daily tasks
* Mark tasks complete
* Give coaching summary
* Explain progress plateaus
* Answer “what should I do today?”

### Agent behavior requirements

* Must use tools when a deterministic action is needed.
* Must not guess when parsing workout plans.
* Must return structured confirmation after import.
* Must ask for clarification only if the input cannot be normalized.

---

## 12. Tools / Internal Functions

### Workout Tools

* `create_workout_program`
* `get_today_workout`
* `log_workout_set`
* `get_progression_target`
* `get_workout_summary`

### Meal Tools

* `analyze_meal_photo`
* `save_meal`
* `get_daily_nutrition`
* `get_remaining_macros`

### Weight Tools

* `log_weight`
* `get_weight_trend`
* `get_goal_projection`

### Task Tools

* `generate_daily_tasks`
* `complete_task`
* `get_task_status`

### Coach Tools

* `generate_daily_coaching`
* `generate_weekly_review`

### Reminder Tools

* `schedule_reminder`
* `send_reminder`

### Sheet/Storage Tools

* `write_sheet_record`
* `read_sheet_records`
* `update_sheet_record`

### Media Tools

* `upload_meal_image_to_drive`
* `get_drive_link`

---

## 13. API List

### Agent APIs

* `POST /api/agent/chat`
* `POST /api/agent/import-workout`

### Weight APIs

* `POST /api/weight`
* `GET /api/weight/history`
* `GET /api/weight/trend`

### Meal APIs

* `POST /api/meals/analyze`
* `POST /api/meals`
* `GET /api/meals/today`
* `GET /api/meals/history`

### Workout APIs

* `POST /api/workouts/import`
* `GET /api/workouts/today`
* `POST /api/workouts/log`
* `GET /api/workouts/progression`
* `GET /api/workouts/history`

### Task APIs

* `GET /api/tasks/today`
* `POST /api/tasks/complete`
* `GET /api/tasks/status`

### Coach APIs

* `GET /api/coach/daily`
* `GET /api/coach/weekly`

### Reminder APIs

* `POST /api/reminders`
* `GET /api/reminders`

### Settings APIs

* `GET /api/settings`
* `POST /api/settings`

---

## 14. Data Model

### Users

* id
* name
* created_at

### WeightLogs

* id
* user_id
* date
* weight

### Meals

* id
* user_id
* date
* meal_type
* calories
* protein
* carbs
* fat
* image_url

### MealItems

* id
* meal_id
* food_name
* quantity
* unit
* calories
* protein
* carbs
* fat

### WorkoutPrograms

* id
* program_name
* day_name
* exercise_name
* sets
* rep_min
* rep_max
* rest_day_flag

### WorkoutSchedules

* id
* program_id
* weekday
* workout_day_name

### WorkoutSessions

* id
* user_id
* workout_date
* workout_day_name

### WorkoutSets

* id
* session_id
* exercise_name
* set_number
* weight
* reps

### Tasks

* id
* task_name
* task_type

### DailyTaskStatus

* id
* date
* task_id
* completed

### CoachInsights

* id
* user_id
* date
* summary

### Reminders

* id
* reminder_type
* reminder_time
* channel
* enabled

---

## 15. Workout Import Format Specification

### Allowed syntax

* Day headers:

  * `Push:`
  * `Pull:`
  * `Legs:`
  * `Upper:`
  * `Lower:`
  * `Rest`
* Exercise lines:

  * `Bench Press 3x6-8`
  * `RDL 4x8-10`

### Parsing rules

* Each day header starts a new block.
* `Rest` creates a rest day.
* Each exercise line should parse into:

  * exercise name
  * sets
  * minimum reps
  * maximum reps
* Invalid lines should return a validation error with the exact line number.

### Output behavior

After import, the agent should confirm:

* Program name
* Number of workout days
* Number of rest days
* Total exercises imported
* Any unsupported lines ignored or corrected

---

## 16. Workout Planning Logic

### Schedule support

The system should support:

* Fixed weekday split
* Rotating weekly split
* Rest-day insertion
* Repeatable cycles

### Example schedule types

* Push / Pull / Legs / Rest / Push / Pull / Legs
* Upper / Lower / Rest / Upper / Lower / Rest / Rest
* Custom weekday mapping

### Example user experience

User pastes:

```text
Mon - Push
Tue - Pull
Wed - Legs
Thu - Rest
Fri - Push
Sat - Pull
Sun - Rest
```

The system should store this as a weekly schedule and automatically show the correct day’s workout.

---

## 17. UX Requirements

### Mobile

* Bottom navigation
* Single-column layouts
* Fast add actions
* Large touch targets
* Camera-first meal flow

### Desktop

* Multi-column dashboard
* Persistent sidebar
* Side-by-side charts
* Faster data review and editing

### Empty states

Must provide friendly empty states for:

* No meals logged
* No weight logged
* No workout plan imported
* No reminders set
* No coach history yet

---

## 18. Technical Architecture

### Frontend

* Next.js PWA
* TypeScript
* Tailwind
* Shadcn UI

### Backend

* Next.js API routes or server actions

### Storage

* Google Sheets as structured tables
* Google Drive for meal images

### AI

* OpenAI vision for meal analysis
* OpenAI reasoning model for coaching

### Notifications

* Telegram bot
* Browser notifications

### Hosting

* Vercel

---

## 19. Architecture Principle for Future Migration

The sheet structure must behave like relational tables so it can later move to Postgres/Supabase with minimal transformation.

Rules:

* One sheet = one table
* One row = one record
* No merged cells
* No nested JSON blobs unless necessary
* No formula-dependent business logic in the sheet
* All business logic lives in the app layer

---

## 20. Success Metrics

### User Success

* Weight logged at least 5 days/week
* Meals logged consistently
* Workout sessions logged every training day
* Missions completed daily
* User keeps using it for 30+ days

### Product Success

* Meal import works reliably
* Workout import works reliably
* The user trusts the coaching summary
* The user can stay on track without manual spreadsheet work

---

## 21. Risks and Mitigations

| Risk                                 | Mitigation                                       |
| ------------------------------------ | ------------------------------------------------ |
| Meal photo recognition is inaccurate | Let user confirm/edit before saving              |
| Workout parsing fails on messy text  | Provide supported format and validation feedback |
| User stops logging                   | Daily reminders + simple flows                   |
| Sheets become messy over time        | Strict schema and repository layer               |
| AI costs grow                        | Save outputs and avoid reprocessing              |

---

## 22. Release Plan

### Day 1

* Auth
* Dashboard
* Weight logging
* Workout program import
* Workout schedule
* Workout logging
* Daily missions

### Day 2

* Meal photo upload
* Meal analysis
* Coaching summary
* Reminder system
* Progress charts
* Deployment

---

## 23. Acceptance Criteria

The MVP is ready when the user can:

* Paste a workout plan into chat and import it successfully.
* See today’s workout automatically.
* Log sets in under 30 seconds.
* Log weight in under 10 seconds.
* Upload a meal photo and get calories/macros.
* Receive reminders.
* See daily coaching and progress trends.
* Store all data in the approved sheet format.

---

## 24. Final Product Statement

BodyOps is a personal AI fat-loss operating system that turns meal tracking, workout progression, weight logging, reminders, and coaching into one guided execution loop.

It is designed to reduce friction, improve consistency, and make fat loss feel like a system rather than a guessing game.

If you want, I can turn this into a **clean .md file** and give you the download link.

[1]: https://www.atlassian.com/agile/product-management/requirements?utm_source=chatgpt.com "How to create a product requirements document (PRD)"
