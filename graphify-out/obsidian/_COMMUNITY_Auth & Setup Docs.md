---
type: community
cohesion: 0.29
members: 7
---

# Auth & Setup Docs

**Cohesion:** 0.29 - loosely connected
**Members:** 7 nodes

## Members
- [[Auth Sheet (owner-only, plain-text credentials)]] - document - PLAN.md
- [[BodyOps Root README (setup + deployment quickstart)]] - document - README.md
- [[BodyOps Setup Guide (9-step provisioning + deployment)]] - document - SETUP.md
- [[GET health Endpoint ({ok, sheets, drive})]] - document - README.md
- [[Google Cloud Provisioning (service account, API key, SheetsDrive APIs)]] - document - SETUP.md
- [[JWT Auth via python-jose + Auth Sheet]] - document - PLAN.md
- [[Sheet Bootstrap Script (scriptssetup.py)]] - document - PLAN.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Auth__Setup_Docs
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Architecture & Deployment Docs]]
- 1 edge to [[_COMMUNITY_Planned Feature Engines (Docs)]]
- 1 edge to [[_COMMUNITY_Agent Chat Planning Docs]]
- 1 edge to [[_COMMUNITY_HF Spaces Deployment]]

## Top bridge nodes
- [[Sheet Bootstrap Script (scriptssetup.py)]] - degree 3, connects to 2 communities
- [[BodyOps Root README (setup + deployment quickstart)]] - degree 4, connects to 1 community
- [[JWT Auth via python-jose + Auth Sheet]] - degree 2, connects to 1 community