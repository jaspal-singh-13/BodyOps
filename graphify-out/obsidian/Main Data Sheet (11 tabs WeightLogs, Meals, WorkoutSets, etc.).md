---
source_file: "PLAN.md"
type: "document"
community: "Planned Feature Engines (Docs)"
location: "§Google Spreadsheet Layout"
tags:
  - graphify/document
  - graphify/EXTRACTED
  - community/Planned_Feature_Engines_Docs
---

# Main Data Sheet (11 tabs: WeightLogs, Meals, WorkoutSets, etc.)

## Connections
- [[AI Coaching Engine (dailyweekly summaries, cached in CoachInsights)]] - `shares_data_with` [EXTRACTED]
- [[Daily Mission Engine (generateDailyTasks, auto-completion hooks)]] - `shares_data_with` [EXTRACTED]
- [[Data Model (Users, WeightLogs, Meals, WorkoutPrograms, DailyTaskStatus, ...)]] - `implements` [EXTRACTED]
- [[FastAPI Backend (HF Spaces)]] - `shares_data_with` [EXTRACTED]
- [[Sheet Bootstrap Script (scriptssetup.py)]] - `calls` [EXTRACTED]
- [[Sheets-as-Relational-Tables Migration Principle (PostgresSupabase later)]] - `conceptually_related_to` [INFERRED]

#graphify/document #graphify/EXTRACTED #community/Planned_Feature_Engines_Docs