---
type: community
cohesion: 0.24
members: 10
---

# Streak Computation Tests

**Cohesion:** 0.24 - loosely connected
**Members:** 10 nodes

## Members
- [[.test_complete_today_extends_streak()]] - code - tests/test_missions.py
- [[.test_gap_breaks_streak()]] - code - tests/test_missions.py
- [[.test_incomplete_today_does_not_break_existing_streak()]] - code - tests/test_missions.py
- [[.test_no_rows_returns_zero()]] - code - tests/test_missions.py
- [[A fully complete today counts toward the streak.]] - rationale - tests/test_missions.py
- [[A missed day stops the count even if earlier days were complete.]] - rationale - tests/test_missions.py
- [[An in-progress today is skipped streak counts back from yesterday.]] - rationale - tests/test_missions.py
- [[Build n DailyTaskStatus rows for a date, all complete or all incomplete.]] - rationale - tests/test_missions.py
- [[TestComputeStreak]] - code - tests/test_missions.py
- [[_status_rows_for()]] - code - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Streak_Computation_Tests
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 4 edges to [[_COMMUNITY_Daily Task Service]]

## Top bridge nodes
- [[TestComputeStreak]] - degree 7, connects to 1 community
- [[_status_rows_for()]] - degree 5, connects to 1 community
- [[.test_complete_today_extends_streak()]] - degree 4, connects to 1 community
- [[.test_gap_breaks_streak()]] - degree 4, connects to 1 community
- [[.test_incomplete_today_does_not_break_existing_streak()]] - degree 4, connects to 1 community