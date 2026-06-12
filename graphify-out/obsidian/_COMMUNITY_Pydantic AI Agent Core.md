---
type: community
cohesion: 0.06
members: 52
---

# Pydantic AI Agent Core

**Cohesion:** 0.06 - loosely connected
**Members:** 52 nodes

## Members
- [[Agent]] - code - api/agent/agent.py
- [[AgentDeps]] - code - api/agent/agent.py
- [[AgentDeps_2]] - code - api/agent/prompts.py
- [[AgentDeps_3]] - code - api/agent/tools.py
- [[AsyncAzureOpenAI]] - code - api/agent/llm.py
- [[Build and return a configured ``OpenAIChatModel`` backed by Azure OpenAI.]] - rationale - api/agent/llm.py
- [[Central LLM model factory.  To swap the provider (e.g. from Azure OpenAI to An]] - rationale - api/agent/llm.py
- [[Central store for all LLM prompts used in BodyOps.]] - rationale - api/agent/prompts.py
- [[Construct and return the Pydantic AI ``Agent`` instance.      Passes ``get_sys]] - rationale - api/agent/agent.py
- [[Import a workout plan from free-form text in any format.      Uses AI to conve]] - rationale - api/agent/tools.py
- [[Log a single set for a workout exercise.      Args         ctx Pydantic AI]] - rationale - api/agent/tools.py
- [[Log the user's body weight for a given date.      Args         ctx Pydantic]] - rationale - api/agent/tools.py
- [[Mark a daily mission complete by its task ID.      Use ``get_task_status`` fir]] - rationale - api/agent/tools.py
- [[OpenAIChatModel]] - code - api/agent/llm.py
- [[Pydantic AI agent definition for BodyOps.  This module creates the singleton `]] - rationale - api/agent/agent.py
- [[Pydantic AI tool definitions for Phases 2–4 (Weight, Workout, Meal Tracking).]] - rationale - api/agent/tools.py
- [[Retrieve the user's weight trend and goal projection.      Fetches the 7-day m]] - rationale - api/agent/tools.py
- [[Return a raw ``AsyncAzureOpenAI`` client built from environment variables.]] - rationale - api/agent/llm.py
- [[Return all saved workout plans in the user's plan library.      Use this befor]] - rationale - api/agent/tools.py
- [[Return the suggested weight and reps for the next session of an exercise.]] - rationale - api/agent/tools.py
- [[Return the system prompt with today's date in the user's local timezone.]] - rationale - api/agent/prompts.py
- [[Return today's consumed nutrition vs targets.      Args         ctx Pydanti]] - rationale - api/agent/tools.py
- [[Return today's mission list with name, completion flag, and timestamp.      Ar]] - rationale - api/agent/tools.py
- [[Return today's workout plan with progressive overload suggestions.      Args]] - rationale - api/agent/tools.py
- [[Run AI vision analysis on a Drive-hosted meal photo URL.      Returns a macro]] - rationale - api/agent/tools.py
- [[RunContext]] - code - api/agent/prompts.py
- [[RunContext_1]] - code - api/agent/tools.py
- [[Runtime dependencies injected into every agent tool call.  This module is inte]] - rationale - api/agent/deps.py
- [[Save a meal and its items to the Sheets.      Use this when the user describes]] - rationale - api/agent/tools.py
- [[Switch the user's active workout plan by name.      Resolves the name case-ins]] - rationale - api/agent/tools.py
- [[agent.py]] - code - api/agent/agent.py
- [[analyze_meal_photo()]] - code - api/agent/tools.py
- [[build_agent()]] - code - api/agent/agent.py
- [[complete_task()]] - code - api/agent/tools.py
- [[deps.py]] - code - api/agent/deps.py
- [[get_async_client()]] - code - api/agent/llm.py
- [[get_daily_nutrition()]] - code - api/agent/tools.py
- [[get_model()]] - code - api/agent/llm.py
- [[get_progression_target()]] - code - api/agent/tools.py
- [[get_system_prompt()]] - code - api/agent/prompts.py
- [[get_task_status()]] - code - api/agent/tools.py
- [[get_today_workout()]] - code - api/agent/tools.py
- [[get_weight_trend()]] - code - api/agent/tools.py
- [[import_workout_from_text()]] - code - api/agent/tools.py
- [[list_workout_plans()]] - code - api/agent/tools.py
- [[llm.py]] - code - api/agent/llm.py
- [[log_weight()]] - code - api/agent/tools.py
- [[log_workout_set()]] - code - api/agent/tools.py
- [[prompts.py]] - code - api/agent/prompts.py
- [[save_meal()]] - code - api/agent/tools.py
- [[switch_workout_plan()]] - code - api/agent/tools.py
- [[tools.py]] - code - api/agent/tools.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Pydantic_AI_Agent_Core
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 3 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 2 edges to [[_COMMUNITY_Meal Macro Schemas]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 1 edge to [[_COMMUNITY_Meal Vision Service]]
- 1 edge to [[_COMMUNITY_Workout Plan Management]]
- 1 edge to [[_COMMUNITY_AI Workout Import]]

## Top bridge nodes
- [[get_async_client()]] - degree 8, connects to 4 communities
- [[tools.py]] - degree 20, connects to 3 communities
- [[agent.py]] - degree 10, connects to 2 communities
- [[deps.py]] - degree 6, connects to 2 communities
- [[AgentDeps_3]] - degree 14, connects to 1 community