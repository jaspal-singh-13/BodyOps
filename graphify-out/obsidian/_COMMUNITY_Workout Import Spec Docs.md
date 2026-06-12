---
type: community
cohesion: 0.67
members: 3
---

# Workout Import Spec Docs

**Cohesion:** 0.67 - moderately connected
**Members:** 3 nodes

## Members
- [[Testing Strategy (pytest layers + required test files)]] - document - PLAN.md
- [[Workout Import Format Specification (NxM-P syntax, day headers, Rest)]] - document - PRD.md
- [[Workout Import Parser (apiservicesworkout_parser.py)]] - document - PLAN.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workout_Import_Spec_Docs
SORT file.name ASC
```
