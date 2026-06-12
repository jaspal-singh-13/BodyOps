---
type: community
cohesion: 0.33
members: 6
---

# Agent Chat Planning Docs

**Cohesion:** 0.33 - loosely connected
**Members:** 6 nodes

## Members
- [[API List (apiweight, apimeals, apiworkouts, apitasks, apicoach)]] - document - PRD.md
- [[Agent Capabilities & Behavior Requirements]] - document - PRD.md
- [[Chat History Sheet]] - document - PLAN.md
- [[POST agentchat Endpoint + Chat-to-Log Drawer]] - document - PLAN.md
- [[Pydantic AI Tool-Calling Agent]] - document - PLAN.md
- [[Tools  Internal Functions Catalog (workout, meal, weight, task, coach tools)]] - document - PRD.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Agent_Chat_Planning_Docs
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Architecture & Deployment Docs]]
- 1 edge to [[_COMMUNITY_Planned Feature Engines (Docs)]]
- 1 edge to [[_COMMUNITY_Auth & Setup Docs]]
- 1 edge to [[_COMMUNITY_Design Wireframes & Prototypes]]

## Top bridge nodes
- [[Chat History Sheet]] - degree 3, connects to 2 communities
- [[Pydantic AI Tool-Calling Agent]] - degree 4, connects to 1 community
- [[POST agentchat Endpoint + Chat-to-Log Drawer]] - degree 3, connects to 1 community