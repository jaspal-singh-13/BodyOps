---
type: community
cohesion: 0.15
members: 14
---

# Architecture & Deployment Docs

**Cohesion:** 0.15 - loosely connected
**Members:** 14 nodes

## Members
- [[Backend Runtime Dependencies (fastapi, pydantic-ai, gspread, openai, tzdata)]] - code - api/requirements.txt
- [[Backend as Next.js API Routes (PRD-era architecture)]] - document - PRD.md
- [[BodyOps Implementation Plan]] - document - PLAN.md
- [[CORS Configuration in apimain.py (localhost + Vercel origin)]] - document - SETUP.md
- [[FastAPI Backend (HF Spaces)]] - document - PLAN.md
- [[Frontend CLAUDE.md (delegates to AGENTS.md)]] - document - frontend/CLAUDE.md
- [[Frontend README (stock create-next-app boilerplate)]] - document - frontend/README.md
- [[Next.js 14 Frontend (Vercel)]] - document - PLAN.md
- [[Next.js Agent Rules (read node_modulesnextdistdocs before coding)]] - document - frontend/AGENTS.md
- [[Root Dependencies (adds instructor + pytest dev deps, lacks tzdata)]] - code - requirements.txt
- [[Service Split Architecture (Next.js UI shell + FastAPI backend)]] - document - PLAN.md
- [[Telegram + Browser Notifications (PRD-era plan)]] - document - PRD.md
- [[Timezone Handling (X-Timezone header + zoneinfo)]] - document - PLAN.md
- [[Vercel Frontend Deployment Procedure (vercel CLI, NEXT_PUBLIC_API_URL)]] - document - SETUP.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Architecture__Deployment_Docs
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_HF Spaces Deployment]]
- 1 edge to [[_COMMUNITY_PRD & Fat-Loss Goal]]
- 1 edge to [[_COMMUNITY_Design Wireframes & Prototypes]]
- 1 edge to [[_COMMUNITY_Agent Chat Planning Docs]]
- 1 edge to [[_COMMUNITY_Auth & Setup Docs]]
- 1 edge to [[_COMMUNITY_Planned Feature Engines (Docs)]]

## Top bridge nodes
- [[FastAPI Backend (HF Spaces)]] - degree 9, connects to 4 communities
- [[Next.js 14 Frontend (Vercel)]] - degree 6, connects to 1 community
- [[BodyOps Implementation Plan]] - degree 3, connects to 1 community