---
source_file: "PLAN.md"
type: "document"
community: "Architecture & Deployment Docs"
location: "§Architecture Decisions"
tags:
  - graphify/document
  - graphify/EXTRACTED
  - community/Architecture__Deployment_Docs
---

# FastAPI Backend (HF Spaces)

## Connections
- [[Backend Runtime Dependencies (fastapi, pydantic-ai, gspread, openai, tzdata)]] - `implements` [EXTRACTED]
- [[CORS Configuration in apimain.py (localhost + Vercel origin)]] - `references` [EXTRACTED]
- [[Chat History Sheet]] - `shares_data_with` [EXTRACTED]
- [[Deploy Backend to HF Spaces GitHub Workflow]] - `references` [EXTRACTED]
- [[JWT Auth via python-jose + Auth Sheet]] - `implements` [EXTRACTED]
- [[Main Data Sheet (11 tabs WeightLogs, Meals, WorkoutSets, etc.)]] - `shares_data_with` [EXTRACTED]
- [[Next.js 14 Frontend (Vercel)]] - `shares_data_with` [EXTRACTED]
- [[Service Split Architecture (Next.js UI shell + FastAPI backend)]] - `references` [EXTRACTED]
- [[Timezone Handling (X-Timezone header + zoneinfo)]] - `implements` [EXTRACTED]

#graphify/document #graphify/EXTRACTED #community/Architecture__Deployment_Docs