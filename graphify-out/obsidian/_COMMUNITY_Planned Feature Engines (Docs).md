---
type: community
cohesion: 0.29
members: 8
---

# Planned Feature Engines (Docs)

**Cohesion:** 0.29 - loosely connected
**Members:** 8 nodes

## Members
- [[AI Coaching Engine (dailyweekly summaries, cached in CoachInsights)]] - document - PLAN.md
- [[Azure OpenAI gpt-4o (vision + coaching)]] - document - PLAN.md
- [[Daily Mission Engine (generateDailyTasks, auto-completion hooks)]] - document - PLAN.md
- [[Dashboard Card Stack Evolution (7 cards across phases)]] - document - PLAN.md
- [[Data Model (Users, WeightLogs, Meals, WorkoutPrograms, DailyTaskStatus, ...)]] - document - PRD.md
- [[Main Data Sheet (11 tabs WeightLogs, Meals, WorkoutSets, etc.)]] - document - PLAN.md
- [[Meal Vision Service (gpt-4o photo analysis + Drive upload)]] - document - PLAN.md
- [[Sheets-as-Relational-Tables Migration Principle (PostgresSupabase later)]] - document - PRD.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Planned_Feature_Engines_Docs
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Architecture & Deployment Docs]]
- 1 edge to [[_COMMUNITY_Agent Chat Planning Docs]]
- 1 edge to [[_COMMUNITY_Auth & Setup Docs]]
- 1 edge to [[_COMMUNITY_Design Wireframes & Prototypes]]

## Top bridge nodes
- [[Main Data Sheet (11 tabs WeightLogs, Meals, WorkoutSets, etc.)]] - degree 6, connects to 2 communities
- [[Azure OpenAI gpt-4o (vision + coaching)]] - degree 3, connects to 1 community
- [[Dashboard Card Stack Evolution (7 cards across phases)]] - degree 3, connects to 1 community